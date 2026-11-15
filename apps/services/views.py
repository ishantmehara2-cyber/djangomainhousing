import math
import csv
from datetime import timedelta
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, JsonResponse, Http404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from django.db import models
from django.db.models import Max, Count, Q
from django.utils import timezone
from django.views.decorators.http import require_POST
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

from apps.accounts.permissions import admin_required
from apps.locations.models import State, City, Locality
from apps.core.validators import validate_file_size_5mb
from apps.services.models import (
    BankPartner,
    BankCategoryChoices,
    ProcessingFeeTypeChoices,
    BankLoanProduct,
    BankLoanEnquiry,
    RentalAgreementRequest,
    RentalAgreementStatus,
    AgreementType,
    LoanInquiryLead,
    LoanInquiryNote,
    LoanInquiryStatusHistory,
    LoanInquiryStatusChoices,
    EmploymentTypeChoices,
    ServiceCategory,
    Service,
    ServiceProvider,
    ProviderApprovalStatusChoices,
    ProviderServiceArea,
    ServiceProviderDocument,
    ServiceEnquiry,
    ServiceAssignment,
    ServiceEnquiryStatusHistory,
    ServiceEnquiryStatusChoices
)
from apps.services.forms import (
    LoanInquiryLeadForm,
    BankLoanEnquiryForm,
    HomeLoanCalculatorForm,
    RentalAgreementRequestForm,
    BankPartnerForm,
    ServiceEnquiryForm
)
from apps.services.enquiry_service import (
    create_service_enquiry,
    send_service_enquiry_notification,
    send_provider_registration_notification
)

User = get_user_model()


def bank_loans_view(request):
    """
    Renders the Bank Loan Services page with database-driven Banking Partners,
    loan eligibility overview, required documents, FAQs, and a LoanInquiryLead submission form.
    """
    banks = BankPartner.objects.filter(is_active=True).order_by('display_order', 'name')
    latest_updated = banks.aggregate(Max('updated_at'))['updated_at__max'] if banks.exists() else None

    if request.method == 'POST':
        form = LoanInquiryLeadForm(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            mobile = cd['mobile_number'].strip()
            email = cd['email_address'].strip().lower()
            amount = cd['desired_loan_amount']

            # Duplicate submission check (120-second window)
            recent_cutoff = timezone.now() - timedelta(seconds=120)
            duplicate = LoanInquiryLead.objects.filter(
                Q(mobile_number=mobile) | Q(email_address__iexact=email),
                desired_loan_amount=amount,
                created_at__gte=recent_cutoff,
                is_deleted=False
            ).first()

            if duplicate:
                messages.success(request, "Your home loan enquiry has been submitted successfully. Our team will contact you shortly.")
                return redirect('services:bank-loans')

            lead = form.save()
            LoanInquiryStatusHistory.objects.create(
                lead=lead,
                old_status='',
                new_status=LoanInquiryStatusChoices.NEW,
                notes='Initial callback enquiry submitted via Bank Loans page.'
            )

            # Dual-sync to BankLoanEnquiry model for legacy admin compatibility
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

            messages.success(request, "Your home loan enquiry has been submitted successfully. Our team will contact you shortly.")
            return redirect('services:bank-loans')
        else:
            messages.error(request, "Please correct the errors in the loan enquiry form below.")
    else:
        form = LoanInquiryLeadForm()

    context = {
        'banks': banks,
        'latest_updated_at': latest_updated,
        'form': form,
    }
    return render(request, 'services/bank_loans.html', context)


def home_loan_calculator_view(request):
    """
    Home Loan Eligibility & EMI Calculator.
    Mathematically computes maximum eligible loan amount and EMI based on FOIR.
    """
    form = HomeLoanCalculatorForm(request.GET if request.GET else None)

    income = 75000.0
    existing_emi = 0.0
    tenure_years = 20
    annual_rate = 8.50
    foir_percent = 50.0

    if request.GET and form.is_valid():
        income = float(form.cleaned_data['monthly_income'])
        existing_emi = float(form.cleaned_data.get('existing_emi') or 0.0)
        tenure_years = int(form.cleaned_data['tenure_years'])
        annual_rate = float(form.cleaned_data['interest_rate'])
        foir_percent = float(form.cleaned_data.get('foir_percentage') or 50.0)
    elif request.GET:
        try:
            income = float(request.GET.get('monthly_income', 75000))
            existing_emi = float(request.GET.get('existing_emi', 0))
            tenure_years = int(request.GET.get('tenure_years', 20))
            annual_rate = float(request.GET.get('interest_rate', 8.5))
        except (ValueError, TypeError):
            pass

    max_total_emi_capacity = income * (foir_percent / 100.0)
    max_available_emi = max(0.0, max_total_emi_capacity - existing_emi)

    r = (annual_rate / 100.0) / 12.0
    n = tenure_years * 12

    if max_available_emi > 0 and r > 0 and n > 0:
        discount_factor = ((1 + r) ** n - 1) / (r * ((1 + r) ** n))
        max_loan_amount = max_available_emi * discount_factor
        estimated_emi = max_available_emi
        total_repayment = estimated_emi * n
        total_interest = total_repayment - max_loan_amount
    else:
        max_loan_amount = 0.0
        estimated_emi = 0.0
        total_repayment = 0.0
        total_interest = 0.0

    result = {
        'monthly_income': income,
        'existing_emi': existing_emi,
        'foir_percent': foir_percent,
        'max_total_emi_capacity': round(max_total_emi_capacity, 2),
        'max_available_emi': round(max_available_emi, 2),
        'max_loan_amount': round(max_loan_amount, 2),
        'estimated_emi': round(estimated_emi, 2),
        'total_repayment': round(total_repayment, 2),
        'total_interest': round(total_interest, 2),
        'tenure_years': tenure_years,
        'annual_rate': annual_rate,
        'is_eligible': max_available_emi > 0 and max_loan_amount > 0,
    }

    if request.headers.get('x-requested-with') == 'XMLHttpRequest' or request.GET.get('format') == 'json':
        return JsonResponse({'success': True, 'result': result})

    context = {
        'form': form,
        'result': result,
    }
    return render(request, 'services/loan_calculator.html', context)


def rental_agreement_services_view(request):
    """
    Rental Agreement Services page with legal process workflow, required documents,
    pricing options, and request submission form.
    """
    if request.method == 'POST':
        form = RentalAgreementRequestForm(request.POST)
        if form.is_valid():
            req_obj = form.save(commit=False)
            if request.user.is_authenticated:
                req_obj.user = request.user

            if req_obj.agreement_type == AgreementType.REGISTERED:
                req_obj.estimated_charge = 1999.00
            elif req_obj.agreement_type == AgreementType.NOTARIZED:
                req_obj.estimated_charge = 799.00
            else:
                req_obj.estimated_charge = 499.00

            req_obj.save()

            try:
                from apps.services.email_service import send_company_rental_agreement_notification_email
                send_company_rental_agreement_notification_email(req_obj)
            except Exception:
                pass

            messages.success(
                request,
                f"Your rental agreement request has been submitted successfully! "
                f"Reference Number: {req_obj.reference_number}. "
                f"A notification has been sent to our legal executive team with your details."
            )
            return redirect('services:rental-agreement-detail', ref_num=req_obj.reference_number)
        else:
            messages.error(request, "Please check the form inputs and try again.")
    else:
        initial_data = {}
        if request.user.is_authenticated:
            initial_data = {
                'full_name': request.user.get_full_name() or request.user.username,
                'email': request.user.email,
                'phone': getattr(request.user, 'phone', '') or '',
            }
        form = RentalAgreementRequestForm(initial=initial_data)

    context = {
        'form': form,
    }
    return render(request, 'services/rental_agreement.html', context)


def rental_agreement_detail_view(request, ref_num):
    agreement_req = get_object_or_404(RentalAgreementRequest, reference_number=ref_num)
    context = {
        'agreement': agreement_req,
    }
    return render(request, 'services/rental_agreement_detail.html', context)


@login_required
@admin_required
def admin_rental_agreements_view(request):
    status_filter = request.GET.get('status', '')
    agreements = RentalAgreementRequest.objects.all()
    if status_filter:
        agreements = agreements.filter(status=status_filter)

    context = {
        'agreements': agreements,
        'status_choices': RentalAgreementStatus.choices,
        'selected_status': status_filter,
    }
    return render(request, 'services/admin_rental_agreements.html', context)


# ==============================================================================
# ADMIN DASHBOARD - BANK MANAGEMENT VIEWS
# ==============================================================================

@login_required
@admin_required
def admin_bank_management_view(request):
    q = request.GET.get('q', '').strip()
    category = request.GET.get('category', '').strip()
    status = request.GET.get('status', '').strip()

    banks = BankPartner.objects.all()

    if q:
        banks = banks.filter(name__icontains=q)
    if category:
        banks = banks.filter(category=category)
    if status == 'active':
        banks = banks.filter(is_active=True)
    elif status == 'inactive':
        banks = banks.filter(is_active=False)

    banks = banks.order_by('display_order', 'name')

    context = {
        'banks': banks,
        'query': q,
        'category_filter': category,
        'status_filter': status,
        'categories': BankCategoryChoices.choices,
    }
    return render(request, 'admin_panel/bank_management.html', context)


@login_required
@admin_required
def admin_add_bank_view(request):
    if request.method == 'POST':
        form = BankPartnerForm(request.POST, request.FILES)
        if form.is_valid():
            bank = form.save()
            messages.success(request, f"Banking partner '{bank.name}' added successfully!")
            return redirect('services:admin-bank-management')
        else:
            messages.error(request, "Please correct the form errors below.")
    else:
        form = BankPartnerForm()

    context = {
        'form': form,
        'is_edit': False,
    }
    return render(request, 'admin_panel/add_edit_bank.html', context)


@login_required
@admin_required
def admin_edit_bank_view(request, pk):
    bank = get_object_or_404(BankPartner, pk=pk)

    if request.method == 'POST':
        form = BankPartnerForm(request.POST, request.FILES, instance=bank)
        if form.is_valid():
            bank = form.save()
            messages.success(request, f"Banking partner '{bank.name}' updated successfully!")
            return redirect('services:admin-bank-management')
        else:
            messages.error(request, "Please correct the form errors below.")
    else:
        form = BankPartnerForm(instance=bank)

    context = {
        'form': form,
        'bank': bank,
        'is_edit': True,
    }
    return render(request, 'admin_panel/add_edit_bank.html', context)


@login_required
@admin_required
@require_POST
def admin_toggle_bank_active_view(request, pk):
    bank = get_object_or_404(BankPartner, pk=pk)
    bank.is_active = not bank.is_active
    bank.save(update_fields=['is_active'])
    status_str = "activated" if bank.is_active else "deactivated"
    messages.success(request, f"Bank '{bank.name}' has been {status_str}.")
    return redirect('services:admin-bank-management')


@login_required
@admin_required
@require_POST
def admin_delete_bank_view(request, pk):
    bank = get_object_or_404(BankPartner, pk=pk)
    has_enquiries = BankLoanEnquiry.objects.filter(preferred_bank=bank).exists()

    if has_enquiries:
        bank.is_active = False
        bank.save(update_fields=['is_active'])
        messages.warning(request, f"Bank '{bank.name}' has existing loan enquiries associated with it. It was deactivated instead of permanently deleted.")
    else:
        bank_name = bank.name
        bank.delete()
        messages.success(request, f"Bank '{bank_name}' was permanently deleted.")

    return redirect('services:admin-bank-management')


# ==============================================================================
# ADMIN PORTAL - LOAN INQUIRY LEADS
# ==============================================================================

@login_required
@admin_required
def admin_loan_inquiries_view(request):
    query = request.GET.get('q', '').strip()
    status_filter = request.GET.get('status', '').strip()
    bank_filter = request.GET.get('bank', '').strip()
    employment_filter = request.GET.get('employment_type', '').strip()
    sort_order = request.GET.get('sort', 'newest')

    leads = LoanInquiryLead.objects.filter(is_deleted=False).select_related('preferred_bank', 'assigned_staff')

    if query:
        leads = leads.filter(
            Q(lead_id__icontains=query) |
            Q(full_name__icontains=query) |
            Q(email_address__icontains=query) |
            Q(mobile_number__icontains=query)
        )
    if status_filter:
        leads = leads.filter(status=status_filter)
    if bank_filter:
        leads = leads.filter(preferred_bank_id=bank_filter)
    if employment_filter:
        leads = leads.filter(employment_type=employment_filter)

    if sort_order == 'oldest':
        leads = leads.order_by('created_at')
    else:
        leads = leads.order_by('-created_at')

    total_count = LoanInquiryLead.objects.filter(is_deleted=False).count()
    new_count = LoanInquiryLead.objects.filter(is_deleted=False, status='NEW').count()
    pending_count = LoanInquiryLead.objects.filter(is_deleted=False, status='CONTACT_PENDING').count()
    eval_count = LoanInquiryLead.objects.filter(is_deleted=False, status='UNDER_BANK_EVALUATION').count()
    approved_count = LoanInquiryLead.objects.filter(is_deleted=False, status='LOAN_APPROVED').count()
    rejected_count = LoanInquiryLead.objects.filter(is_deleted=False, status='LOAN_REJECTED').count()

    paginator = Paginator(leads, 15)
    page_number = request.GET.get('page', 1)
    try:
        page_obj = paginator.page(page_number)
    except PageNotAnInteger:
        page_obj = paginator.page(1)
    except EmptyPage:
        page_obj = paginator.page(paginator.num_pages)

    banks = BankPartner.objects.all().order_by('name')
    staff_members = User.objects.filter(Q(is_staff=True) | Q(is_superuser=True) | Q(role__in=['ADMIN', 'SUPER_ADMIN', 'MODERATOR'])).order_by('first_name')

    context = {
        'page_obj': page_obj,
        'leads': page_obj,
        'total_count': total_count,
        'new_count': new_count,
        'pending_count': pending_count,
        'eval_count': eval_count,
        'approved_count': approved_count,
        'rejected_count': rejected_count,
        'query': query,
        'status_filter': status_filter,
        'bank_filter': bank_filter,
        'employment_filter': employment_filter,
        'sort_order': sort_order,
        'status_choices': LoanInquiryStatusChoices.choices,
        'employment_choices': EmploymentTypeChoices.choices,
        'banks': banks,
        'staff_members': staff_members,
    }
    return render(request, 'admin_panel/loan_inquiry_leads.html', context)


@login_required
@admin_required
def admin_loan_inquiry_detail_view(request, lead_id):
    lead = get_object_or_404(LoanInquiryLead.objects.select_related('preferred_bank', 'assigned_staff'), id=lead_id)

    if request.method == 'POST':
        action_type = request.POST.get('action')

        if action_type == 'add_note':
            note_text = request.POST.get('note_text', '').strip()
            if note_text:
                LoanInquiryNote.objects.create(
                    lead=lead,
                    author=request.user,
                    note_text=note_text
                )
                messages.success(request, "Internal note added successfully.")
            return redirect('services:admin-loan-inquiry-detail', lead_id=lead.id)

        elif action_type == 'update_lead' or not action_type:
            new_status = request.POST.get('status', lead.status)
            assigned_staff_id = request.POST.get('assigned_staff')
            follow_up_date = request.POST.get('follow_up_date')
            notes_update = request.POST.get('admin_notes', '').strip()

            status_changed = False
            old_status = lead.status

            if new_status and new_status != old_status:
                lead.status = new_status
                status_changed = True

            if assigned_staff_id is not None:
                if assigned_staff_id and assigned_staff_id.isdigit():
                    lead.assigned_staff_id = int(assigned_staff_id)
                elif assigned_staff_id == '':
                    lead.assigned_staff = None

            if follow_up_date:
                lead.follow_up_date = follow_up_date
            elif follow_up_date == '':
                lead.follow_up_date = None

            if notes_update:
                lead.admin_notes = notes_update

            lead.save()

            if status_changed:
                LoanInquiryStatusHistory.objects.create(
                    lead=lead,
                    old_status=old_status,
                    new_status=new_status,
                    updated_by=request.user,
                    notes=f"Status changed to {lead.get_status_display()} by {request.user.get_full_name() or request.user.username}."
                )
                messages.success(request, f"Lead status updated to '{lead.get_status_display()}'.")
            else:
                messages.success(request, "Lead information updated successfully.")

            return redirect('services:admin-loan-inquiry-detail', lead_id=lead.id)

    notes = lead.notes.select_related('author').all()
    history = lead.status_history.select_related('updated_by').all()
    staff_members = User.objects.filter(Q(is_staff=True) | Q(is_superuser=True) | Q(role__in=['ADMIN', 'SUPER_ADMIN', 'MODERATOR'])).order_by('first_name')

    context = {
        'lead': lead,
        'notes': notes,
        'history': history,
        'status_choices': LoanInquiryStatusChoices.choices,
        'staff_members': staff_members,
    }
    return render(request, 'admin_panel/loan_inquiry_detail.html', context)


@login_required
@admin_required
@require_POST
def admin_delete_loan_inquiry_view(request, pk):
    lead = get_object_or_404(LoanInquiryLead, pk=pk)
    lead.is_deleted = True
    lead.save(update_fields=['is_deleted'])
    messages.success(request, f"Loan inquiry lead {lead.lead_id} ({lead.full_name}) was archived successfully.")
    return redirect('services:admin-loan-inquiries')


@login_required
@admin_required
def admin_export_loan_inquiries_csv_view(request):
    query = request.GET.get('q', '').strip()
    status_filter = request.GET.get('status', '').strip()
    bank_filter = request.GET.get('bank', '').strip()

    leads = LoanInquiryLead.objects.filter(is_deleted=False).select_related('preferred_bank', 'assigned_staff')

    if query:
        leads = leads.filter(
            Q(lead_id__icontains=query) |
            Q(full_name__icontains=query) |
            Q(email_address__icontains=query) |
            Q(mobile_number__icontains=query)
        )
    if status_filter:
        leads = leads.filter(status=status_filter)
    if bank_filter:
        leads = leads.filter(preferred_bank_id=bank_filter)

    leads = leads.order_by('-created_at')

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="loan_inquiry_leads_{timezone.now().strftime("%Y%m%d_%H%M")}.csv"'

    writer = csv.writer(response)
    writer.writerow([
        'Lead ID', 'Full Name', 'Mobile Number', 'Email Address',
        'Employment Type', 'Net Monthly Income', 'Desired Loan Amount',
        'Preferred Bank', 'Status', 'Assigned Staff', 'Submission Date', 'Follow-up Date'
    ])

    for lead in leads:
        writer.writerow([
            lead.lead_id,
            lead.full_name,
            lead.mobile_number,
            lead.email_address,
            lead.get_employment_type_display(),
            float(lead.net_monthly_income),
            float(lead.desired_loan_amount),
            lead.preferred_bank.name if lead.preferred_bank else 'Any Bank',
            lead.get_status_display(),
            lead.assigned_staff.get_full_name() if lead.assigned_staff else 'Unassigned',
            lead.created_at.strftime("%Y-%m-%d %H:%M:%S"),
            lead.follow_up_date.strftime("%Y-%m-%d") if lead.follow_up_date else ''
        ])

    return response


# ==============================================================================
# UNIFIED PARTNER MARKETPLACE SERVICE PROVIDER VIEWS
# ==============================================================================

def partner_marketplace_view(request):
    """
    Unified Partner Marketplace main portal view.
    Single Source of Truth: ServiceProvider database model.
    Public visibility condition: approval_status='APPROVED', is_active=True, is_published=True.
    """
    active_tab = request.GET.get('tab', 'services')

    agents = User.objects.filter(role__in=['AGENT', 'DEVELOPER'], status='ACTIVE').order_by('-date_joined')
    categories = ServiceCategory.objects.filter(
        approval_status='APPROVED',
        is_published=True,
        is_active=True
    ).order_by('display_order', 'name')

    approved_providers = ServiceProvider.objects.filter(
        approval_status=ProviderApprovalStatusChoices.APPROVED,
        is_active=True,
        is_published=True
    ).select_related('city', 'state', 'category').prefetch_related('categories').order_by('-created_at')

    featured_providers = approved_providers.filter(is_featured=True)

    featured_services = Service.objects.filter(
        approval_status='APPROVED',
        is_published=True,
        is_active=True,
        is_featured=True,
        category__approval_status='APPROVED',
        category__is_published=True,
        category__is_active=True
    ).select_related('category').order_by('display_order', 'name')[:12]

    search_q = request.GET.get('q', '').strip()
    if search_q:
        agents = agents.filter(Q(username__icontains=search_q) | Q(first_name__icontains=search_q) | Q(last_name__icontains=search_q) | Q(agency_name__icontains=search_q))
        categories = categories.filter(
            Q(name__icontains=search_q) | Q(description__icontains=search_q)
        ).distinct()
        approved_providers = approved_providers.filter(
            Q(business_name__icontains=search_q) | Q(full_name__icontains=search_q) | Q(city__name__icontains=search_q) | Q(category__name__icontains=search_q)
        ).distinct()

    context = {
        'agents': agents,
        'categories': categories,
        'approved_providers': approved_providers,
        'featured_providers': featured_providers,
        'featured_services': featured_services,
        'active_tab': active_tab,
        'search_query': search_q,
    }
    return render(request, 'brokers/partner_marketplace.html', context)


def service_category_detail_view(request, slug):
    """
    Displays all individual services and approved service provider companies under a specific category.
    Returns 404 if category itself is not approved, published, and active.
    """
    category = get_object_or_404(
        ServiceCategory,
        slug=slug,
        approval_status='APPROVED',
        is_published=True,
        is_active=True
    )

    services = Service.objects.filter(
        category=category,
        approval_status='APPROVED',
        is_published=True,
        is_active=True
    ).order_by('display_order', 'name')

    approved_providers = ServiceProvider.objects.filter(
        approval_status=ProviderApprovalStatusChoices.APPROVED,
        is_active=True,
        is_published=True
    ).filter(
        Q(category=category) | Q(categories=category)
    ).select_related('city', 'state').prefetch_related('categories').distinct().order_by('-created_at')

    search_q = request.GET.get('q', '').strip()
    if search_q:
        services = services.filter(
            Q(name__icontains=search_q) | Q(short_description__icontains=search_q) | Q(detailed_description__icontains=search_q)
        ).distinct()
        approved_providers = approved_providers.filter(
            Q(business_name__icontains=search_q) | Q(full_name__icontains=search_q) | Q(city__name__icontains=search_q)
        ).distinct()

    all_categories = ServiceCategory.objects.filter(
        approval_status='APPROVED',
        is_published=True,
        is_active=True
    ).order_by('display_order')

    states = State.objects.filter(is_active=True).order_by('name')
    cities = City.objects.filter(is_active=True).order_by('name')

    context = {
        'category': category,
        'services': services,
        'approved_providers': approved_providers,
        'all_categories': all_categories,
        'search_query': search_q,
        'states': states,
        'cities': cities,
    }
    return render(request, 'services/category_detail.html', context)


def service_detail_view(request, slug):
    """
    Displays dedicated detail page for an individual service item.
    Enforces strict backend visibility rules: 404 if service or parent category is not approved, published, and active.
    """
    service = get_object_or_404(
        Service.objects.select_related('category'),
        slug=slug,
        approval_status='APPROVED',
        is_published=True,
        is_active=True,
        category__approval_status='APPROVED',
        category__is_published=True,
        category__is_active=True
    )

    related_services = Service.objects.filter(
        category=service.category,
        approval_status='APPROVED',
        is_published=True,
        is_active=True
    ).exclude(id=service.id).order_by('display_order', 'name')[:6]

    eligible_providers = service.providers.filter(
        approval_status=ProviderApprovalStatusChoices.APPROVED,
        is_active=True,
        is_published=True
    ).select_related('city', 'state').distinct()

    if not eligible_providers.exists():
        eligible_providers = ServiceProvider.objects.filter(
            approval_status=ProviderApprovalStatusChoices.APPROVED,
            is_active=True,
            is_published=True
        ).filter(
            Q(category=service.category) | Q(categories=service.category)
        ).select_related('city', 'state').distinct()[:6]

    states = State.objects.filter(is_active=True).order_by('name')
    cities = City.objects.filter(is_active=True).order_by('name')

    context = {
        'service': service,
        'category': service.category,
        'related_services': related_services,
        'eligible_providers': eligible_providers,
        'states': states,
        'cities': cities,
    }
    return render(request, 'services/service_detail.html', context)


def submit_service_enquiry_view(request):
    """
    Handles customer enquiry form submission for any specific service or custom service request.
    Validates service selection against the actual database.
    Saves record to DB as a ServiceEnquiry lead FIRST before triggering email notifications.
    """
    if request.method == 'POST':
        service_id = request.POST.get('service_id')
        service_slug = request.POST.get('service_slug')
        category_id = request.POST.get('category_id')
        category_slug = request.POST.get('category_slug')
        requested_service_name = request.POST.get('requested_service_name') or request.POST.get('service_name') or request.POST.get('service')

        service = None
        category = None

        if service_id and str(service_id).isdigit():
            service = Service.objects.filter(
                id=int(service_id),
                approval_status='APPROVED',
                is_active=True,
                is_published=True,
                category__approval_status='APPROVED',
                category__is_active=True,
                category__is_published=True
            ).first()
        elif service_slug:
            service = Service.objects.filter(
                slug=service_slug,
                approval_status='APPROVED',
                is_active=True,
                is_published=True,
                category__approval_status='APPROVED',
                category__is_active=True,
                category__is_published=True
            ).first()

        if service:
            category = service.category
            requested_service_name = service.name
        elif category_id and str(category_id).isdigit():
            category = ServiceCategory.objects.filter(id=int(category_id), approval_status='APPROVED', is_active=True, is_published=True).first()
        elif category_slug:
            category = ServiceCategory.objects.filter(slug=category_slug, approval_status='APPROVED', is_active=True, is_published=True).first()

        full_name = request.POST.get('full_name', '').strip()
        mobile_number = request.POST.get('mobile_number', '').strip()
        email = request.POST.get('email', '').strip()
        company_name = request.POST.get('company_name', '').strip() or None
        state_id = request.POST.get('state')
        city_id = request.POST.get('city')
        locality_id = request.POST.get('locality')
        locality_name = request.POST.get('locality_name', '').strip() or None
        requirement_description = request.POST.get('requirement_description', '').strip()
        preferred_contact_method = request.POST.get('preferred_contact_method', 'PHONE')
        preferred_contact_time = request.POST.get('preferred_contact_time', 'Anytime')

        if service:
            redirect_target = redirect('services:service-detail', slug=service.slug)
        elif category:
            redirect_target = redirect('services:service-category-detail', slug=category.slug)
        else:
            redirect_target = redirect('services:partner-marketplace')

        # Mandatory Backend Field Validation
        if not full_name or len(full_name) < 2:
            messages.error(request, "Please enter your full name (at least 2 characters).")
            return redirect_target

        digits = ''.join([c for c in mobile_number if c.isdigit()])
        if not mobile_number or len(digits) < 10:
            messages.error(request, "Please enter a valid mobile number with at least 10 digits.")
            return redirect_target

        if not email or '@' not in email:
            messages.error(request, "Please enter a valid email address.")
            return redirect_target

        if not requirement_description or len(requirement_description) < 5:
            messages.error(request, "Please describe your requirement details (at least 5 characters).")
            return redirect_target

        state = State.objects.filter(id=state_id).first() if state_id and str(state_id).isdigit() else None
        city = City.objects.filter(id=city_id).first() if city_id and str(city_id).isdigit() else None
        locality = Locality.objects.filter(id=locality_id).first() if locality_id and str(locality_id).isdigit() else None
        user = request.user if request.user.is_authenticated else None

        enquiry, created, msg = create_service_enquiry(
            service=service,
            category=category,
            requested_service_name=requested_service_name,
            full_name=full_name,
            mobile_number=mobile_number,
            email=email,
            company_name=company_name,
            state=state,
            city=city,
            locality=locality,
            locality_name=locality_name,
            requirement_description=requirement_description,
            preferred_contact_method=preferred_contact_method,
            preferred_contact_time=preferred_contact_time,
            user=user,
            request=request
        )

        if created:
            messages.success(request, msg)
        else:
            messages.warning(request, msg)

        return redirect_target

    return redirect('services:partner-marketplace')


def register_service_provider_view(request):
    """
    Public registration portal for businesses and individuals to become a Service Provider.
    Registers provider in ServiceProvider table with defaults:
    approval_status='PENDING', is_active=False, is_featured=False, is_published=False.
    """
    categories = ServiceCategory.objects.filter(approval_status='APPROVED', is_published=True, is_active=True).order_by('display_order', 'name')
    states = State.objects.filter(is_active=True).order_by('name')
    cities = City.objects.filter(is_active=True).order_by('name')

    if request.method == 'POST':
        full_name = request.POST.get('full_name', '').strip()
        mobile_number = request.POST.get('mobile_number', '').strip()
        email = request.POST.get('email', '').strip()

        business_name = request.POST.get('business_name', '').strip()
        business_type = request.POST.get('business_type', 'Proprietorship')
        business_description = request.POST.get('business_description', '').strip()
        business_address = request.POST.get('business_address', '').strip()
        category_id = request.POST.get('category')
        selected_category_ids = request.POST.getlist('selected_categories')

        state_id = request.POST.get('state')
        city_id = request.POST.get('city')
        locality_id = request.POST.get('locality')
        pincode = request.POST.get('pincode', '').strip()
        website = request.POST.get('website', '').strip()

        years_exp = request.POST.get('years_of_experience', '1')
        business_contact = request.POST.get('business_contact_number', '').strip()
        business_email = request.POST.get('business_email', '').strip()
        working_days = request.POST.get('working_days', 'Monday to Saturday')
        working_hours = request.POST.get('working_hours', '9:00 AM - 7:00 PM')
        short_profile = request.POST.get('short_profile', '').strip()

        if not (full_name and mobile_number and email and business_name and business_address):
            messages.error(request, "Please fill in all mandatory business and contact details.")
            return redirect('services:register-provider')

        state = State.objects.filter(id=state_id).first() if state_id and str(state_id).isdigit() else None
        city = City.objects.filter(id=city_id).first() if city_id and str(city_id).isdigit() else None
        locality = Locality.objects.filter(id=locality_id).first() if locality_id and str(locality_id).isdigit() else None
        primary_category = ServiceCategory.objects.filter(id=category_id).first() if category_id and str(category_id).isdigit() else None

        user = request.user if request.user.is_authenticated else None

        provider = ServiceProvider.objects.create(
            user=user,
            full_name=full_name,
            mobile_number=mobile_number,
            email=email,
            business_name=business_name,
            business_type=business_type,
            business_description=business_description,
            business_address=business_address,
            category=primary_category,
            state=state,
            city=city,
            locality=locality,
            pincode=pincode,
            website=website if website.startswith(('http://', 'https://')) else (f"https://{website}" if website else None),
            years_of_experience=int(years_exp) if str(years_exp).isdigit() else 1,
            business_contact_number=business_contact,
            business_email=business_email,
            working_days=working_days,
            working_hours=working_hours,
            short_profile=short_profile,
            approval_status=ProviderApprovalStatusChoices.PENDING,
            is_active=False,
            is_featured=False,
            is_published=False
        )

        for c_id in selected_category_ids:
            if str(c_id).isdigit():
                cat = ServiceCategory.objects.filter(id=int(c_id)).first()
                if cat:
                    provider.categories.add(cat)

        if state or city:
            ProviderServiceArea.objects.create(provider=provider, state=state, city=city, locality=locality)

        uploaded_files = request.FILES.getlist('documents')
        for doc_file in uploaded_files:
            try:
                validate_file_size_5mb(doc_file)
                ServiceProviderDocument.objects.create(
                    provider=provider,
                    document_name=doc_file.name,
                    file=doc_file
                )
            except Exception as e:
                messages.warning(request, f"Document '{doc_file.name}' could not be saved: {e}")

        # Trigger automatic email notification to connectthehomefirst@gmail.com
        send_provider_registration_notification(provider, request=request)

        messages.success(
            request,
            f"Registration submitted successfully! Your Provider Reference ID is #{provider.provider_id}. "
            f"Your application is currently Pending Review by our compliance team."
        )
        return redirect('services:register-provider')

    context = {
        'categories': categories,
        'states': states,
        'cities': cities,
    }
    return render(request, 'services/register_provider.html', context)


@login_required
def service_provider_dashboard_view(request):
    """
    Dedicated Dashboard for Approved and Registered Service Providers.
    """
    provider = ServiceProvider.objects.filter(user=request.user).first()
    if not provider:
        provider = ServiceProvider.objects.filter(Q(email__iexact=request.user.email) | Q(mobile_number=getattr(request.user, 'phone', ''))).first()
        if provider and not provider.user:
            provider.user = request.user
            provider.save(update_fields=['user'])

    if not provider:
        messages.info(request, "You do not have an active Service Provider profile. Please register as a Service Provider to access the provider portal.")
        return redirect('services:register-provider')

    if request.method == 'POST':
        action = request.POST.get('action')
        assignment_id = request.POST.get('assignment_id')

        if assignment_id and action in ['accept', 'decline', 'submit_quotation', 'update_progress']:
            assignment = get_object_or_404(ServiceAssignment, id=assignment_id, provider=provider)

            if action == 'accept':
                assignment.response_status = 'ACCEPTED'
                assignment.response_at = timezone.now()
                assignment.save()
                messages.success(request, f"You accepted assignment #{assignment.enquiry.enquiry_id}.")

            elif action == 'decline':
                assignment.response_status = 'DECLINED'
                assignment.response_at = timezone.now()
                assignment.save()
                messages.warning(request, f"You declined assignment #{assignment.enquiry.enquiry_id}.")

            elif action == 'submit_quotation':
                amount = request.POST.get('quotation_amount')
                notes = request.POST.get('quotation_notes', '').strip()
                if amount:
                    assignment.quotation_amount = float(amount)
                    assignment.quotation_notes = notes
                    assignment.save()
                    messages.success(request, f"Quotation of ₹{amount} submitted for enquiry #{assignment.enquiry.enquiry_id}.")

            elif action == 'update_progress':
                p_notes = request.POST.get('progress_notes', '').strip()
                if p_notes:
                    assignment.progress_notes = p_notes
                    assignment.save()
                    messages.success(request, "Progress notes updated.")

            return redirect('services:provider-dashboard')

    assignments = ServiceAssignment.objects.filter(provider=provider).select_related('enquiry').order_by('-assigned_at')

    context = {
        'provider': provider,
        'assignments': assignments,
    }
    return render(request, 'services/provider_dashboard.html', context)
