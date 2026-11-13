import json
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.views.decorators.http import require_http_methods, require_GET, require_POST
from django.contrib.auth.decorators import login_required
from django.utils.text import slugify
from django.db.models import Max

from django.db import models
from apps.accounts.permissions import admin_required
from apps.services.models import (
    BankPartner,
    BankLoanEnquiry,
    BankCategoryChoices,
    ProcessingFeeTypeChoices,
    LoanInquiryLead,
    LoanInquiryNote,
    LoanInquiryStatusHistory,
    LoanInquiryStatusChoices,
    EmploymentTypeChoices
)


def serialize_bank(bank, is_admin=False):
    data = {
        'id': bank.id,
        'name': bank.name,
        'slug': bank.slug,
        'logo_url': bank.logo.url if bank.logo else None,
        'short_description': bank.short_description or '',
        'full_description': bank.full_description or '',
        'website_url': bank.website_url or '',
        'application_url': bank.application_url or '',
        'category': bank.category,
        'category_display': bank.get_category_display(),
        'display_order': bank.display_order,
        'is_active': bank.is_active,
        'min_interest_rate': float(bank.min_interest_rate) if bank.min_interest_rate is not None else None,
        'max_interest_rate': float(bank.max_interest_rate) if bank.max_interest_rate is not None else None,
        'max_tenure_years': bank.max_tenure_years,
        'min_loan_amount': float(bank.min_loan_amount) if bank.min_loan_amount is not None else None,
        'max_loan_amount': float(bank.max_loan_amount) if bank.max_loan_amount is not None else None,
        'processing_fee_info': bank.processing_fee_info or '',
        'processing_fee_type': bank.processing_fee_type,
        'processing_fee_description': bank.processing_fee_description or '',
        'additional_charges': bank.additional_charges or '',
        'benefits': bank.get_benefits_list,
        'eligibility_info': bank.eligibility_info or '',
        'required_documents': bank.required_documents or '',
        'special_offers': bank.special_offers or '',
        'disclaimer': bank.disclaimer or '',
        'updated_at': bank.updated_at.isoformat() if bank.updated_at else None,
    }
    return data


# ==============================================================================
# PUBLIC APIS
# ==============================================================================

@require_GET
def api_public_banks_list(request):
    """
    Returns list of active bank partners ordered by display order.
    """
    banks = BankPartner.objects.filter(is_active=True).order_by('display_order', 'name')
    data = [serialize_bank(b) for b in banks]
    return JsonResponse({'success': True, 'count': len(data), 'banks': data})


@require_GET
def api_public_bank_detail(request, pk):
    """
    Returns public detail view of a single active bank.
    """
    bank = get_object_or_404(BankPartner, pk=pk, is_active=True)
    return JsonResponse({'success': True, 'bank': serialize_bank(bank)})


# ==============================================================================
# ADMIN APIS (Protected)
# ==============================================================================

@login_required
@admin_required
@require_GET
def api_admin_banks_list(request):
    """
    Returns list of all banks (both active & inactive) for admin management.
    """
    query = request.GET.get('q', '').strip()
    category = request.GET.get('category', '').strip()
    status = request.GET.get('status', '').strip()

    banks = BankPartner.objects.all()

    if query:
        banks = banks.filter(name__icontains=query)
    if category:
        banks = banks.filter(category=category)
    if status == 'active':
        banks = banks.filter(is_active=True)
    elif status == 'inactive':
        banks = banks.filter(is_active=False)

    banks = banks.order_by('display_order', 'name')
    data = [serialize_bank(b, is_admin=True) for b in banks]
    return JsonResponse({'success': True, 'count': len(data), 'banks': data})


@login_required
@admin_required
@require_POST
def api_admin_bank_create(request):
    """
    Creates a new banking partner via REST API.
    """
    try:
        data = json.loads(request.body.decode('utf-8')) if request.body else request.POST
    except Exception:
        data = request.POST

    name = data.get('name', '').strip()
    if not name:
        return JsonResponse({'success': False, 'error': 'Bank name is required.'}, status=400)

    min_rate = data.get('min_interest_rate')
    if min_rate is None or str(min_rate).strip() == '':
        return JsonResponse({'success': False, 'error': 'Minimum interest rate is required.'}, status=400)

    slug = data.get('slug', '').strip() or slugify(name)
    if BankPartner.objects.filter(slug=slug).exists():
        slug = f"{slug}-{BankPartner.objects.count() + 1}"

    benefits_input = data.get('benefits', [])
    if isinstance(benefits_input, str):
        benefits_list = [b.strip() for b in benefits_input.split('\n') if b.strip()]
    elif isinstance(benefits_input, list):
        benefits_list = benefits_input
    else:
        benefits_list = []

    logo_file = request.FILES.get('logo')
    if logo_file:
        allowed_types = ['image/jpeg', 'image/png', 'image/webp', 'image/svg+xml']
        if logo_file.content_type not in allowed_types:
            return JsonResponse({'success': False, 'error': 'Invalid logo file format. Use PNG, JPEG, WebP, or SVG.'}, status=400)
        if logo_file.size > 5 * 1024 * 1024:
            return JsonResponse({'success': False, 'error': 'Maximum allowed file size is 5 MB per file.'}, status=400)

    bank = BankPartner.objects.create(
        name=name,
        slug=slug,
        logo=logo_file,
        short_description=data.get('short_description', ''),
        full_description=data.get('full_description', ''),
        website_url=data.get('website_url', ''),
        application_url=data.get('application_url', ''),
        category=data.get('category', BankCategoryChoices.PRIVATE_SECTOR),
        display_order=int(data.get('display_order') or 0),
        is_active=bool(data.get('is_active', True)),
        min_interest_rate=float(min_rate),
        max_interest_rate=float(data['max_interest_rate']) if data.get('max_interest_rate') else None,
        max_tenure_years=int(data.get('max_tenure_years') or 30),
        min_loan_amount=float(data['min_loan_amount']) if data.get('min_loan_amount') else None,
        max_loan_amount=float(data['max_loan_amount']) if data.get('max_loan_amount') else None,
        processing_fee_info=data.get('processing_fee_info', 'Up to 0.50% + GST'),
        processing_fee_type=data.get('processing_fee_type', ProcessingFeeTypeChoices.CUSTOM),
        processing_fee_description=data.get('processing_fee_description', ''),
        additional_charges=data.get('additional_charges', ''),
        benefits=benefits_list,
        eligibility_info=data.get('eligibility_info', ''),
        required_documents=data.get('required_documents', ''),
        special_offers=data.get('special_offers', ''),
        disclaimer=data.get('disclaimer', '')
    )

    return JsonResponse({
        'success': True,
        'message': f'Bank {bank.name} created successfully.',
        'bank': serialize_bank(bank, is_admin=True)
    }, status=211 if False else 201)


@login_required
@admin_required
@require_http_methods(["GET", "PUT", "PATCH", "DELETE"])
def api_admin_bank_detail(request, pk):
    """
    Handles GET detail, PUT/PATCH update, and DELETE for a single bank partner.
    """
    bank = get_object_or_404(BankPartner, pk=pk)

    if request.method == 'GET':
        return JsonResponse({'success': True, 'bank': serialize_bank(bank, is_admin=True)})

    elif request.method in ['PUT', 'PATCH']:
        try:
            data = json.loads(request.body.decode('utf-8')) if request.body else request.POST
        except Exception:
            data = request.POST

        if 'name' in data and data['name'].strip():
            bank.name = data['name'].strip()
        if 'min_interest_rate' in data and data['min_interest_rate'] is not None:
            bank.min_interest_rate = float(data['min_interest_rate'])
        if 'max_interest_rate' in data:
            bank.max_interest_rate = float(data['max_interest_rate']) if data['max_interest_rate'] else None
        if 'max_tenure_years' in data:
            bank.max_tenure_years = int(data['max_tenure_years'])
        if 'processing_fee_info' in data:
            bank.processing_fee_info = data['processing_fee_info']
        if 'processing_fee_type' in data:
            bank.processing_fee_type = data['processing_fee_type']
        if 'category' in data:
            bank.category = data['category']
        if 'display_order' in data:
            bank.display_order = int(data['display_order'])
        if 'is_active' in data:
            bank.is_active = bool(data['is_active'])
        if 'website_url' in data:
            bank.website_url = data['website_url']
        if 'application_url' in data:
            bank.application_url = data['application_url']
        if 'short_description' in data:
            bank.short_description = data['short_description']
        if 'full_description' in data:
            bank.full_description = data['full_description']

        if 'benefits' in data:
            b_input = data['benefits']
            if isinstance(b_input, str):
                bank.benefits = [b.strip() for b in b_input.split('\n') if b.strip()]
            elif isinstance(b_input, list):
                bank.benefits = b_input

        if request.FILES.get('logo'):
            logo_file = request.FILES['logo']
            allowed_types = ['image/jpeg', 'image/png', 'image/webp', 'image/svg+xml']
            if logo_file.content_type in allowed_types and logo_file.size <= 5 * 1024 * 1024:
                bank.logo = logo_file

        bank.save()
        return JsonResponse({
            'success': True,
            'message': f'Bank {bank.name} updated successfully.',
            'bank': serialize_bank(bank, is_admin=True)
        })

    elif request.method == 'DELETE':
        has_enquiries = BankLoanEnquiry.objects.filter(preferred_bank=bank).exists()
        if has_enquiries:
            bank.is_active = False
            bank.save(update_fields=['is_active'])
            return JsonResponse({
                'success': True,
                'soft_deleted': True,
                'message': f'Bank {bank.name} has active loan enquiries associated with it. It has been deactivated instead of permanently deleted.'
            })
        else:
            bank_name = bank.name
            bank.delete()
            return JsonResponse({
                'success': True,
                'deleted': True,
                'message': f'Bank {bank_name} has been permanently deleted.'
            })


# ==============================================================================
# LOAN INQUIRY LEAD REST APIS (MODULE 8)
# ==============================================================================

def serialize_loan_lead(lead, is_admin=False):
    data = {
        'id': lead.id,
        'lead_id': lead.lead_id,
        'full_name': lead.full_name,
        'mobile_number': lead.mobile_number,
        'email_address': lead.email_address,
        'employment_type': lead.employment_type,
        'employment_type_display': lead.get_employment_type_display(),
        'net_monthly_income': float(lead.net_monthly_income),
        'desired_loan_amount': float(lead.desired_loan_amount),
        'preferred_bank': {
            'id': lead.preferred_bank.id,
            'name': lead.preferred_bank.name,
            'logo_url': lead.preferred_bank.logo.url if lead.preferred_bank.logo else None
        } if lead.preferred_bank else None,
        'status': lead.status,
        'status_display': lead.get_status_display(),
        'created_at': lead.created_at.isoformat(),
        'submission_date': lead.created_at.strftime("%Y-%m-%d"),
        'submission_time': lead.created_at.strftime("%H:%M:%S"),
        'updated_at': lead.updated_at.isoformat(),
    }
    if is_admin:
        data.update({
            'admin_notes': lead.admin_notes or '',
            'follow_up_date': lead.follow_up_date.isoformat() if lead.follow_up_date else None,
            'assigned_staff': {
                'id': lead.assigned_staff.id,
                'name': lead.assigned_staff.get_full_name() or lead.assigned_staff.username,
                'email': lead.assigned_staff.email
            } if lead.assigned_staff else None,
        })
    return data


@require_POST
def api_public_loan_inquiry_create(request):
    """
    POST /api/loan-inquiries/
    Public REST API for submitting callback home loan enquiries.
    """
    try:
        data = json.loads(request.body.decode('utf-8')) if request.body else request.POST
    except Exception:
        data = request.POST

    full_name = data.get('full_name', data.get('name', '')).strip()
    mobile_number = data.get('mobile_number', data.get('phone', '')).strip()
    email_address = data.get('email_address', data.get('email', '')).strip().lower()
    employment_type = data.get('employment_type', 'SALARIED')
    monthly_income = data.get('net_monthly_income', data.get('monthly_income'))
    loan_amount = data.get('desired_loan_amount')
    preferred_bank_id = data.get('preferred_bank')

    if not full_name or not mobile_number or not email_address or not monthly_income or not loan_amount:
        return JsonResponse({'success': False, 'error': 'Full name, mobile number, email address, monthly income, and desired loan amount are required.'}, status=400)

    try:
        income_val = float(monthly_income)
        amount_val = float(loan_amount)
    except (ValueError, TypeError):
        return JsonResponse({'success': False, 'error': 'Invalid numeric value for income or loan amount.'}, status=400)

    # Duplicate check within 120 seconds
    from datetime import timedelta
    from django.utils import timezone
    recent_cutoff = timezone.now() - timedelta(seconds=120)
    duplicate = LoanInquiryLead.objects.filter(
        models.Q(mobile_number=mobile_number) | models.Q(email_address__iexact=email_address),
        desired_loan_amount=amount_val,
        created_at__gte=recent_cutoff,
        is_deleted=False
    ).first()

    if duplicate:
        return JsonResponse({
            'success': True,
            'message': 'Your home loan enquiry has been submitted successfully. Our team will contact you shortly.',
            'lead_id': duplicate.lead_id
        })

    bank_obj = None
    if preferred_bank_id:
        try:
            bank_obj = BankPartner.objects.get(id=preferred_bank_id)
        except BankPartner.DoesNotExist:
            pass

    lead = LoanInquiryLead.objects.create(
        full_name=full_name,
        mobile_number=mobile_number,
        email_address=email_address,
        employment_type=employment_type,
        net_monthly_income=income_val,
        desired_loan_amount=amount_val,
        preferred_bank=bank_obj
    )

    LoanInquiryStatusHistory.objects.create(
        lead=lead,
        old_status='',
        new_status=LoanInquiryStatusChoices.NEW,
        notes='Submitted via public REST API endpoint.'
    )

    try:
        BankLoanEnquiry.objects.create(
            name=lead.full_name,
            phone=lead.mobile_number,
            email=lead.email_address,
            employment_type=lead.employment_type,
            monthly_income=lead.net_monthly_income,
            desired_loan_amount=lead.desired_loan_amount,
            preferred_bank=lead.preferred_bank,
            status='NEW'
        )
    except Exception:
        pass

    return JsonResponse({
        'success': True,
        'message': 'Your home loan enquiry has been submitted successfully. Our team will contact you shortly.',
        'lead_id': lead.lead_id,
        'lead': serialize_loan_lead(lead)
    }, status=201)


@login_required
@admin_required
@require_GET
def api_admin_loan_inquiries_list(request):
    """
    GET /api/admin/loan-inquiries/
    Returns paginated list of leads for admin management.
    """
    query = request.GET.get('q', '').strip()
    status_filter = request.GET.get('status', '').strip()
    bank_filter = request.GET.get('bank', '').strip()

    leads = LoanInquiryLead.objects.filter(is_deleted=False).select_related('preferred_bank', 'assigned_staff').order_by('-created_at')

    if query:
        leads = leads.filter(
            models.Q(lead_id__icontains=query) |
            models.Q(full_name__icontains=query) |
            models.Q(email_address__icontains=query) |
            models.Q(mobile_number__icontains=query)
        )
    if status_filter:
        leads = leads.filter(status=status_filter)
    if bank_filter:
        leads = leads.filter(preferred_bank_id=bank_filter)

    data = [serialize_loan_lead(l, is_admin=True) for l in leads]
    return JsonResponse({'success': True, 'count': len(data), 'leads': data})


@login_required
@admin_required
@require_http_methods(["GET", "PATCH"])
def api_admin_loan_inquiry_detail(request, pk):
    """
    GET /api/admin/loan-inquiries/{id}/
    PATCH /api/admin/loan-inquiries/{id}/
    """
    lead = get_object_or_404(LoanInquiryLead, pk=pk, is_deleted=False)

    if request.method == 'GET':
        return JsonResponse({'success': True, 'lead': serialize_loan_lead(lead, is_admin=True)})

    elif request.method == 'PATCH':
        try:
            data = json.loads(request.body.decode('utf-8')) if request.body else request.POST
        except Exception:
            data = request.POST

        old_status = lead.status
        new_status = data.get('status')
        if new_status and new_status in dict(LoanInquiryStatusChoices.choices) and new_status != old_status:
            lead.status = new_status
            LoanInquiryStatusHistory.objects.create(
                lead=lead,
                old_status=old_status,
                new_status=new_status,
                updated_by=request.user,
                notes=f"Status updated via API to {new_status}."
            )

        if 'admin_notes' in data:
            lead.admin_notes = data['admin_notes']
        if 'assigned_staff_id' in data:
            lead.assigned_staff_id = data['assigned_staff_id'] if data['assigned_staff_id'] else None
        if 'follow_up_date' in data:
            lead.follow_up_date = data['follow_up_date'] if data['follow_up_date'] else None

        lead.save()
        return JsonResponse({'success': True, 'message': 'Lead updated successfully.', 'lead': serialize_loan_lead(lead, is_admin=True)})


@login_required
@admin_required
@require_POST
def api_admin_loan_inquiry_add_note(request, pk):
    """
    POST /api/admin/loan-inquiries/{id}/notes/
    """
    lead = get_object_or_404(LoanInquiryLead, pk=pk, is_deleted=False)
    try:
        data = json.loads(request.body.decode('utf-8')) if request.body else request.POST
    except Exception:
        data = request.POST

    note_text = data.get('note_text', '').strip()
    if not note_text:
        return JsonResponse({'success': False, 'error': 'Note text is required.'}, status=400)

    note = LoanInquiryNote.objects.create(
        lead=lead,
        author=request.user,
        note_text=note_text
    )

    return JsonResponse({
        'success': True,
        'message': 'Note added successfully.',
        'note': {
            'id': note.id,
            'note_text': note.note_text,
            'author_name': note.author.get_full_name() if note.author else 'System',
            'created_at': note.created_at.isoformat()
        }
    }, status=201)


@login_required
@admin_required
@require_GET
def api_admin_loan_inquiry_history(request, pk):
    """
    GET /api/admin/loan-inquiries/{id}/history/
    """
    lead = get_object_or_404(LoanInquiryLead, pk=pk, is_deleted=False)
    history = lead.status_history.select_related('updated_by').all()
    data = [{
        'id': h.id,
        'old_status': h.old_status,
        'new_status': h.new_status,
        'new_status_display': h.get_new_status_display(),
        'updated_by_name': h.updated_by.get_full_name() if h.updated_by else 'System',
        'notes': h.notes or '',
        'created_at': h.created_at.isoformat()
    } for h in history]
    return JsonResponse({'success': True, 'count': len(data), 'history': data})
