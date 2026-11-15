import csv
from django.contrib import admin
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import path
from django.contrib import messages
from django.utils import timezone
from django.utils.html import format_html
from django.http import HttpResponse

from apps.services.models import (
    BankPartner,
    BankLoanProduct,
    BankLoanEnquiry,
    RentalAgreementRequest,
    EmailOTP,
    LoanInquiryLead,
    LoanInquiryNote,
    LoanInquiryStatusHistory,
    ServiceCategory,
    Service,
    ServiceProvider,
    ProviderApprovalStatusChoices,
    ProviderServiceArea,
    ServiceProviderDocument,
    ServiceProviderNotificationLog,
    ServiceEnquiry,
    ServiceAssignment,
    ServiceEnquiryStatusHistory,
    ServiceEnquiryNotificationLog,
    ServiceNotificationStatusChoices,
    ServiceEnquiryStatusChoices
)
from apps.services.enquiry_service import (
    retry_service_enquiry_notification,
    retry_provider_registration_notification
)


@admin.register(LoanInquiryLead)
class LoanInquiryLeadAdmin(admin.ModelAdmin):
    list_display = ('lead_id', 'full_name', 'mobile_number', 'email_address', 'employment_type', 'net_monthly_income', 'desired_loan_amount', 'preferred_bank', 'status', 'created_at')
    list_filter = ('status', 'employment_type', 'preferred_bank', 'is_deleted')
    search_fields = ('lead_id', 'full_name', 'email_address', 'mobile_number')
    ordering = ('-created_at',)


@admin.register(LoanInquiryNote)
class LoanInquiryNoteAdmin(admin.ModelAdmin):
    list_display = ('id', 'lead', 'author', 'created_at')
    search_fields = ('lead__lead_id', 'lead__full_name', 'note_text')


@admin.register(LoanInquiryStatusHistory)
class LoanInquiryStatusHistoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'lead', 'old_status', 'new_status', 'updated_by', 'created_at')
    search_fields = ('lead__lead_id', 'lead__full_name')


@admin.register(BankPartner)
class BankPartnerAdmin(admin.ModelAdmin):
    list_display = ('name', 'min_interest_rate', 'max_tenure_years', 'is_active', 'display_order')
    list_filter = ('is_active',)
    search_fields = ('name',)


@admin.register(BankLoanProduct)
class BankLoanProductAdmin(admin.ModelAdmin):
    list_display = ('title', 'bank', 'is_active')
    list_filter = ('bank', 'is_active')
    search_fields = ('title', 'bank__name')


@admin.register(BankLoanEnquiry)
class BankLoanEnquiryAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'email', 'phone', 'desired_loan_amount', 'status', 'created_at')
    list_filter = ('status', 'employment_type')
    search_fields = ('name', 'email', 'phone')


@admin.register(RentalAgreementRequest)
class RentalAgreementRequestAdmin(admin.ModelAdmin):
    list_display = ('reference_number', 'full_name', 'email', 'phone', 'agreement_type', 'status', 'created_at')
    list_filter = ('status', 'agreement_type')
    search_fields = ('reference_number', 'full_name', 'email', 'phone', 'property_address')


@admin.register(EmailOTP)
class EmailOTPAdmin(admin.ModelAdmin):
    list_display = ('email', 'created_at', 'expires_at', 'attempts_count', 'resend_count', 'is_verified')
    list_filter = ('is_verified',)
    search_fields = ('email',)


# ==========================================
# PARTNER MARKETPLACE SERVICE MANAGEMENT ADMIN
# ==========================================

@admin.register(ServiceCategory)
class ServiceCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'icon', 'display_order', 'approval_status', 'is_published', 'is_active', 'active_services_count', 'created_at')
    list_filter = ('approval_status', 'is_published', 'is_active')
    search_fields = ('name', 'description')
    prepopulated_fields = {'slug': ('name',)}
    list_editable = ('display_order', 'approval_status', 'is_published', 'is_active')
    actions = ['approve_categories', 'reject_categories', 'activate_categories', 'deactivate_categories', 'publish_categories', 'unpublish_categories']

    def approve_categories(self, request, queryset):
        updated = queryset.update(
            approval_status='APPROVED',
            is_active=True,
            is_published=True
        )
        self.message_user(request, f"Successfully approved {updated} service category/categories.")
    approve_categories.short_description = "Approve Selected Categories"

    def reject_categories(self, request, queryset):
        updated = queryset.update(approval_status='REJECTED')
        self.message_user(request, f"Successfully rejected {updated} service category/categories.")
    reject_categories.short_description = "Reject Selected Categories"

    def activate_categories(self, request, queryset):
        updated = queryset.update(is_active=True)
        self.message_user(request, f"Successfully activated {updated} service category/categories.")
    activate_categories.short_description = "Activate Selected Categories"

    def deactivate_categories(self, request, queryset):
        updated = queryset.update(is_active=False)
        self.message_user(request, f"Successfully deactivated {updated} service category/categories.")
    deactivate_categories.short_description = "Deactivate Selected Categories"

    def publish_categories(self, request, queryset):
        updated = queryset.update(is_published=True)
        self.message_user(request, f"Successfully published {updated} service category/categories.")
    publish_categories.short_description = "Publish Selected Categories"

    def unpublish_categories(self, request, queryset):
        updated = queryset.update(is_published=False)
        self.message_user(request, f"Successfully unpublished {updated} service category/categories.")
    unpublish_categories.short_description = "Unpublish Selected Categories"


@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = (
        'service_id',
        'name',
        'category',
        'display_order',
        'approval_status',
        'is_published',
        'is_active',
        'is_featured',
        'created_at'
    )
    list_filter = ('approval_status', 'is_published', 'is_active', 'is_featured', 'category')
    search_fields = ('service_id', 'name', 'short_description', 'detailed_description')
    prepopulated_fields = {'slug': ('name',)}
    list_editable = ('display_order', 'approval_status', 'is_published', 'is_active', 'is_featured')
    actions = [
        'approve_services',
        'reject_services',
        'activate_services',
        'deactivate_services',
        'publish_services',
        'unpublish_services',
        'feature_services',
        'unfeature_services'
    ]

    fieldsets = (
        ("Service Identification", {
            'fields': ('service_id', 'name', 'slug', 'category', 'icon', 'image', 'display_order')
        }),
        ("Content & Descriptions", {
            'fields': ('short_description', 'detailed_description', 'benefits', 'whats_included', 'how_it_works', 'required_documents', 'faqs')
        }),
        ("Approval & Visibility Controls", {
            'fields': ('approval_status', 'is_active', 'is_featured', 'is_published')
        }),
        ("Timestamps", {
            'fields': ('created_at', 'updated_at')
        }),
    )
    readonly_fields = ('service_id', 'created_at', 'updated_at')

    def approve_services(self, request, queryset):
        updated = queryset.update(approval_status='APPROVED', is_active=True, is_published=True)
        self.message_user(request, f"Successfully approved {updated} service(s).")
    approve_services.short_description = "Approve Selected Services"

    def reject_services(self, request, queryset):
        updated = queryset.update(approval_status='REJECTED')
        self.message_user(request, f"Successfully rejected {updated} service(s).")
    reject_services.short_description = "Reject Selected Services"

    def activate_services(self, request, queryset):
        updated = queryset.update(is_active=True)
        self.message_user(request, f"Successfully activated {updated} service(s).")
    activate_services.short_description = "Activate Selected Services"

    def deactivate_services(self, request, queryset):
        updated = queryset.update(is_active=False)
        self.message_user(request, f"Successfully deactivated {updated} service(s).")
    deactivate_services.short_description = "Deactivate Selected Services"

    def publish_services(self, request, queryset):
        updated = queryset.update(is_published=True)
        self.message_user(request, f"Successfully published {updated} service(s).")
    publish_services.short_description = "Publish Selected Services"

    def unpublish_services(self, request, queryset):
        updated = queryset.update(is_published=False)
        self.message_user(request, f"Successfully unpublished {updated} service(s).")
    unpublish_services.short_description = "Unpublish Selected Services"

    def feature_services(self, request, queryset):
        updated = queryset.update(is_featured=True)
        self.message_user(request, f"Successfully featured {updated} service(s).")
    feature_services.short_description = "Feature Selected Services"

    def unfeature_services(self, request, queryset):
        updated = queryset.update(is_featured=False)
        self.message_user(request, f"Successfully unfeatured {updated} service(s).")
    unfeature_services.short_description = "Unfeature Selected Services"


class ProviderServiceAreaInline(admin.TabularInline):
    model = ProviderServiceArea
    extra = 1


class ServiceProviderDocumentInline(admin.TabularInline):
    model = ServiceProviderDocument
    extra = 0
    readonly_fields = ['uploaded_at']


class ServiceProviderNotificationLogInline(admin.TabularInline):
    model = ServiceProviderNotificationLog
    extra = 0
    readonly_fields = ['attempt_timestamp', 'recipient_email', 'subject', 'delivery_status', 'retry_count', 'error_details']
    can_delete = False
    ordering = ['-attempt_timestamp']


@admin.register(ServiceProviderNotificationLog)
class ServiceProviderNotificationLogAdmin(admin.ModelAdmin):
    list_display = ('id', 'provider', 'recipient_email', 'subject', 'delivery_status_badge', 'retry_count', 'attempt_timestamp')
    list_filter = ('delivery_status', 'attempt_timestamp')
    search_fields = ('provider__provider_id', 'provider__business_name', 'recipient_email', 'subject', 'error_details')
    readonly_fields = ('provider', 'recipient_email', 'subject', 'attempt_timestamp', 'delivery_status', 'error_details', 'retry_count')

    def delivery_status_badge(self, obj):
        if obj.delivery_status == ServiceNotificationStatusChoices.SENT:
            return format_html('<span style="background-color: #dcfce7; color: #15803d; padding: 3px 8px; border-radius: 9999px; font-weight: bold; font-size: 11px;">Sent</span>')
        elif obj.delivery_status == ServiceNotificationStatusChoices.PENDING:
            return format_html('<span style="background-color: #fef9c3; color: #a16207; padding: 3px 8px; border-radius: 9999px; font-weight: bold; font-size: 11px;">Pending</span>')
        else:
            return format_html('<span style="background-color: #fee2e2; color: #b91c1c; padding: 3px 8px; border-radius: 9999px; font-weight: bold; font-size: 11px;">Failed</span>')
    delivery_status_badge.short_description = "Status"


@admin.register(ServiceProvider)
class ServiceProviderAdmin(admin.ModelAdmin):
    list_display = (
        'provider_id',
        'business_name',
        'full_name',
        'mobile_number',
        'city',
        'approval_status',
        'is_active',
        'is_featured',
        'is_published',
        'notification_status_badge',
        'created_at'
    )
    list_editable = ('approval_status', 'is_active', 'is_featured', 'is_published')
    list_filter = ('approval_status', 'is_active', 'is_featured', 'is_published', 'category', 'business_type', 'city', 'created_at')
    search_fields = ('provider_id', 'business_name', 'full_name', 'mobile_number', 'email', 'city__name')
    readonly_fields = ('provider_id', 'created_at', 'updated_at', 'notification_status_display', 'retry_notification_button')
    inlines = [ProviderServiceAreaInline, ServiceProviderDocumentInline, ServiceProviderNotificationLogInline]
    actions = [
        'approve_providers',
        'reject_providers',
        'activate_providers',
        'deactivate_providers',
        'feature_providers',
        'unfeature_providers',
        'publish_providers',
        'unpublish_providers',
        'retry_failed_provider_notifications'
    ]

    filter_horizontal = ('categories', 'services')
    fieldsets = (
        ("Application & Provider ID", {
            'fields': ('provider_id', 'full_name', 'mobile_number', 'email')
        }),
        ("Business Information", {
            'fields': ('business_name', 'business_type', 'category', 'categories', 'services', 'business_description', 'business_address', 'website', 'years_of_experience', 'business_contact_number', 'business_email', 'working_days', 'working_hours', 'short_profile')
        }),
        ("Location Information", {
            'fields': ('state', 'city', 'locality', 'pincode')
        }),
        ("Approval & Publication Controls", {
            'fields': ('approval_status', 'is_active', 'is_featured', 'is_published', 'internal_notes', 'rejection_reason')
        }),
        ("Email Notification Tracking", {
            'fields': ('notification_status_display', 'retry_notification_button', 'created_at', 'updated_at')
        }),
    )

    def notification_status_badge(self, obj):
        if obj.notification_status == ServiceNotificationStatusChoices.SENT:
            return format_html('<span style="background-color: #dcfce7; color: #15803d; padding: 3px 8px; border-radius: 9999px; font-weight: bold; font-size: 11px;">Sent</span>')
        elif obj.notification_status == ServiceNotificationStatusChoices.PENDING:
            return format_html('<span style="background-color: #fef9c3; color: #a16207; padding: 3px 8px; border-radius: 9999px; font-weight: bold; font-size: 11px;">Pending</span>')
        else:
            return format_html('<span style="background-color: #fee2e2; color: #b91c1c; padding: 3px 8px; border-radius: 9999px; font-weight: bold; font-size: 11px;">Failed</span>')
    notification_status_badge.short_description = "Email Notification"

    def notification_status_display(self, obj):
        return self.notification_status_badge(obj)
    notification_status_display.short_description = "Notification Status"

    def retry_notification_button(self, obj):
        if obj.pk:
            url = f"/admin/services/serviceprovider/{obj.pk}/retry-notification/"
            return format_html('<a class="button" style="background-color: #0284c7; color: white; padding: 6px 12px; border-radius: 6px; text-decoration: none; font-weight: bold;" href="{}">✉ Retry Email Notification</a>', url)
        return "-"
    retry_notification_button.short_description = "Notification Actions"

    def approve_providers(self, request, queryset):
        updated = queryset.update(
            approval_status=ProviderApprovalStatusChoices.APPROVED,
            is_active=True,
            is_published=True
        )
        self.message_user(request, f"Successfully approved {updated} service provider(s).")
    approve_providers.short_description = "Approve Selected Providers"

    def reject_providers(self, request, queryset):
        updated = queryset.update(
            approval_status=ProviderApprovalStatusChoices.REJECTED,
            is_active=False,
            is_published=False
        )
        self.message_user(request, f"Successfully rejected {updated} service provider(s).")
    reject_providers.short_description = "Reject Selected Providers"

    def activate_providers(self, request, queryset):
        updated = queryset.update(is_active=True)
        self.message_user(request, f"Successfully activated {updated} service provider(s).")
    activate_providers.short_description = "Activate Selected Providers"

    def deactivate_providers(self, request, queryset):
        updated = queryset.update(is_active=False)
        self.message_user(request, f"Successfully deactivated {updated} service provider(s).")
    deactivate_providers.short_description = "Deactivate Selected Providers"

    def feature_providers(self, request, queryset):
        updated = queryset.update(is_featured=True)
        self.message_user(request, f"Successfully featured {updated} service provider(s).")
    feature_providers.short_description = "Feature Selected Providers"

    def unfeature_providers(self, request, queryset):
        updated = queryset.update(is_featured=False)
        self.message_user(request, f"Successfully unfeatured {updated} service provider(s).")
    unfeature_providers.short_description = "Unfeature Selected Providers"

    def publish_providers(self, request, queryset):
        updated = queryset.update(is_published=True)
        self.message_user(request, f"Successfully published {updated} service provider(s).")
    publish_providers.short_description = "Publish Selected Providers"

    def unpublish_providers(self, request, queryset):
        updated = queryset.update(is_published=False)
        self.message_user(request, f"Successfully unpublished {updated} service provider(s).")
    unpublish_providers.short_description = "Unpublish Selected Providers"

    def retry_failed_provider_notifications(self, request, queryset):
        success_count = 0
        fail_count = 0
        for provider in queryset:
            success = retry_provider_registration_notification(provider, request=request)
            if success:
                success_count += 1
            else:
                fail_count += 1
        self.message_user(request, f"Provider Notification retry completed: {success_count} succeeded, {fail_count} failed.")
    retry_failed_provider_notifications.short_description = "Retry Selected Email Notifications"

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('<path:object_id>/retry-notification/', self.admin_site.admin_view(self.retry_provider_notification_view), name='services_serviceprovider_retry_notification'),
        ]
        return custom_urls + urls

    def retry_provider_notification_view(self, request, object_id):
        provider = get_object_or_404(ServiceProvider, id=object_id)
        success = retry_provider_registration_notification(provider, request=request)
        if success:
            messages.success(request, f"Registration Email Notification for Provider #{provider.provider_id} sent successfully to connectthehomefirst@gmail.com.")
        else:
            messages.error(request, f"Failed to send email notification for Provider #{provider.provider_id}. Please check SMTP configuration.")
        return redirect('admin:services_serviceprovider_change', object_id)


class ServiceAssignmentInline(admin.TabularInline):
    model = ServiceAssignment
    extra = 0
    readonly_fields = ['assigned_at', 'response_at']


class ServiceEnquiryStatusHistoryInline(admin.TabularInline):
    model = ServiceEnquiryStatusHistory
    extra = 0
    readonly_fields = ['created_at', 'old_status', 'new_status', 'updated_by', 'notes']
    can_delete = False


class ServiceEnquiryNotificationLogInline(admin.TabularInline):
    model = ServiceEnquiryNotificationLog
    extra = 0
    readonly_fields = ['attempt_timestamp', 'recipient_email', 'subject', 'delivery_status', 'retry_count', 'error_details']
    can_delete = False
    ordering = ['-attempt_timestamp']


@admin.register(ServiceEnquiryNotificationLog)
class ServiceEnquiryNotificationLogAdmin(admin.ModelAdmin):
    list_display = ('id', 'enquiry', 'recipient_email', 'subject', 'delivery_status_badge', 'retry_count', 'attempt_timestamp')
    list_filter = ('delivery_status', 'attempt_timestamp')
    search_fields = ('enquiry__enquiry_id', 'recipient_email', 'subject', 'error_details')
    readonly_fields = ('enquiry', 'recipient_email', 'subject', 'attempt_timestamp', 'delivery_status', 'error_details', 'retry_count')

    def delivery_status_badge(self, obj):
        if obj.delivery_status == ServiceNotificationStatusChoices.SENT:
            return format_html('<span style="background-color: #dcfce7; color: #15803d; padding: 3px 8px; border-radius: 9999px; font-weight: bold; font-size: 11px;">Sent</span>')
        elif obj.delivery_status == ServiceNotificationStatusChoices.PENDING:
            return format_html('<span style="background-color: #fef9c3; color: #a16207; padding: 3px 8px; border-radius: 9999px; font-weight: bold; font-size: 11px;">Pending</span>')
        else:
            return format_html('<span style="background-color: #fee2e2; color: #b91c1c; padding: 3px 8px; border-radius: 9999px; font-weight: bold; font-size: 11px;">Failed</span>')
    delivery_status_badge.short_description = "Status"


@admin.register(ServiceEnquiry)
class ServiceEnquiryAdmin(admin.ModelAdmin):
    list_display = (
        'enquiry_id',
        'full_name',
        'mobile_number',
        'email',
        'get_company_name',
        'get_service_category',
        'get_service_name',
        'get_city',
        'created_at',
        'status',
        'notification_status_badge'
    )
    list_filter = ('status', 'notification_status', 'category', 'service', 'city', 'created_at')
    search_fields = ('enquiry_id', 'full_name', 'mobile_number', 'email', 'company_name', 'requirement_description', 'requested_service_name', 'service__name')
    readonly_fields = ('enquiry_id', 'created_at', 'updated_at', 'notification_status_display', 'retry_notification_button')
    inlines = [ServiceAssignmentInline, ServiceEnquiryStatusHistoryInline, ServiceEnquiryNotificationLogInline]
    actions = ['retry_failed_email_notifications', 'export_enquiries_csv', 'mark_as_contacted', 'mark_as_in_progress', 'mark_as_completed']

    fieldsets = (
        ("Enquiry Information", {
            'fields': ('enquiry_id', 'full_name', 'mobile_number', 'email', 'company_name')
        }),
        ("Requested Service & Requirement", {
            'fields': ('service', 'category', 'requested_service_name', 'requirement_description', 'preferred_contact_method', 'preferred_contact_time')
        }),
        ("Location Information", {
            'fields': ('state', 'city', 'locality', 'locality_name')
        }),
        ("Status & Staff Assignment", {
            'fields': ('status', 'assigned_staff', 'internal_notes', 'user')
        }),
        ("Email Notification Tracking", {
            'fields': ('notification_status_display', 'retry_notification_button', 'created_at', 'updated_at')
        }),
    )

    def get_company_name(self, obj):
        return obj.company_name or "-"
    get_company_name.short_description = "Company Name"

    def get_service_category(self, obj):
        return obj.category_name
    get_service_category.short_description = "Service Category"
    get_service_category.admin_order_field = "category__name"

    def get_service_name(self, obj):
        return obj.service_name_display
    get_service_name.short_description = "Requested Service"
    get_service_name.admin_order_field = "requested_service_name"

    def get_city(self, obj):
        return obj.city.name if obj.city else "Not specified"
    get_city.short_description = "City"
    get_city.admin_order_field = "city__name"

    def notification_status_badge(self, obj):
        if obj.notification_status == ServiceNotificationStatusChoices.SENT:
            return format_html('<span style="background-color: #dcfce7; color: #15803d; padding: 3px 8px; border-radius: 9999px; font-weight: bold; font-size: 11px;">Sent</span>')
        elif obj.notification_status == ServiceNotificationStatusChoices.PENDING:
            return format_html('<span style="background-color: #fef9c3; color: #a16207; padding: 3px 8px; border-radius: 9999px; font-weight: bold; font-size: 11px;">Pending</span>')
        else:
            return format_html('<span style="background-color: #fee2e2; color: #b91c1c; padding: 3px 8px; border-radius: 9999px; font-weight: bold; font-size: 11px;">Failed</span>')
    notification_status_badge.short_description = "Email Notification"

    def notification_status_display(self, obj):
        return self.notification_status_badge(obj)
    notification_status_display.short_description = "Notification Status"

    def retry_notification_button(self, obj):
        if obj.pk:
            url = f"/admin/services/serviceenquiry/{obj.pk}/retry-notification/"
            return format_html('<a class="button" style="background-color: #0284c7; color: white; padding: 6px 12px; border-radius: 6px; text-decoration: none; font-weight: bold;" href="{}">✉ Retry Email Notification</a>', url)
        return "-"
    retry_notification_button.short_description = "Notification Actions"

    def save_model(self, request, obj, form, change):
        if change and 'status' in form.changed_data:
            old_obj = ServiceEnquiry.objects.get(pk=obj.pk)
            old_status = old_obj.status
            new_status = obj.status
            super().save_model(request, obj, form, change)
            ServiceEnquiryStatusHistory.objects.create(
                enquiry=obj,
                old_status=old_status,
                new_status=new_status,
                updated_by=request.user,
                notes=f"Status updated via Django Admin by {request.user.get_full_name() or request.user.username}."
            )
        else:
            super().save_model(request, obj, form, change)

    def retry_failed_email_notifications(self, request, queryset):
        success_count = 0
        fail_count = 0
        for enquiry in queryset:
            success = retry_service_enquiry_notification(enquiry, request=request)
            if success:
                success_count += 1
            else:
                fail_count += 1
        self.message_user(request, f"Notification retry completed: {success_count} succeeded, {fail_count} failed.")
    retry_failed_email_notifications.short_description = "Retry Selected Email Notifications"

    def export_enquiries_csv(self, request, queryset):
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename="service_enquiries_{timezone.now().strftime("%Y%m%d_%H%M")}.csv"'
        writer = csv.writer(response)
        writer.writerow([
            'Enquiry ID', 'Customer Name', 'Mobile Number', 'Email',
            'Company Name', 'Service Category', 'Requested Service',
            'State', 'City', 'Locality', 'Requirement Description',
            'Preferred Contact Method', 'Preferred Contact Time',
            'Status', 'Notification Status', 'Submitted Date'
        ])
        for enq in queryset:
            writer.writerow([
                enq.enquiry_id,
                enq.full_name,
                enq.mobile_number,
                enq.email,
                enq.company_name or '',
                enq.category_name,
                enq.service_name_display,
                enq.state.name if enq.state else '',
                enq.city.name if enq.city else '',
                enq.locality_display,
                enq.requirement_description,
                enq.get_preferred_contact_method_display(),
                enq.get_preferred_contact_time_display(),
                enq.get_status_display(),
                enq.get_notification_status_display(),
                enq.created_at.strftime("%Y-%m-%d %H:%M:%S") if enq.created_at else ''
            ])
        return response
    export_enquiries_csv.short_description = "Export Selected Enquiries to CSV"

    def mark_as_contacted(self, request, queryset):
        for enquiry in queryset:
            if enquiry.status != ServiceEnquiryStatusChoices.CONTACTED:
                old_status = enquiry.status
                enquiry.status = ServiceEnquiryStatusChoices.CONTACTED
                enquiry.save()
                ServiceEnquiryStatusHistory.objects.create(
                    enquiry=enquiry,
                    old_status=old_status,
                    new_status=ServiceEnquiryStatusChoices.CONTACTED,
                    updated_by=request.user,
                    notes="Marked as Contacted via Admin Bulk Action."
                )
        self.message_user(request, f"Updated {queryset.count()} enquiry status(es) to Contacted.")
    mark_as_contacted.short_description = "Mark Selected as Contacted"

    def mark_as_in_progress(self, request, queryset):
        for enquiry in queryset:
            if enquiry.status != ServiceEnquiryStatusChoices.IN_PROGRESS:
                old_status = enquiry.status
                enquiry.status = ServiceEnquiryStatusChoices.IN_PROGRESS
                enquiry.save()
                ServiceEnquiryStatusHistory.objects.create(
                    enquiry=enquiry,
                    old_status=old_status,
                    new_status=ServiceEnquiryStatusChoices.IN_PROGRESS,
                    updated_by=request.user,
                    notes="Marked as In Progress via Admin Bulk Action."
                )
        self.message_user(request, f"Updated {queryset.count()} enquiry status(es) to In Progress.")
    mark_as_in_progress.short_description = "Mark Selected as In Progress"

    def mark_as_completed(self, request, queryset):
        for enquiry in queryset:
            if enquiry.status != ServiceEnquiryStatusChoices.COMPLETED:
                old_status = enquiry.status
                enquiry.status = ServiceEnquiryStatusChoices.COMPLETED
                enquiry.save()
                ServiceEnquiryStatusHistory.objects.create(
                    enquiry=enquiry,
                    old_status=old_status,
                    new_status=ServiceEnquiryStatusChoices.COMPLETED,
                    updated_by=request.user,
                    notes="Marked as Completed via Admin Bulk Action."
                )
        self.message_user(request, f"Updated {queryset.count()} enquiry status(es) to Completed.")
    mark_as_completed.short_description = "Mark Selected as Completed"

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('<path:object_id>/retry-notification/', self.admin_site.admin_view(self.retry_notification_view), name='services_serviceenquiry_retry_notification'),
            path('<path:object_id>/match-providers/', self.admin_site.admin_view(self.match_providers_view), name='services_serviceenquiry_match_providers'),
        ]
        return custom_urls + urls

    def retry_notification_view(self, request, object_id):
        enquiry = get_object_or_404(ServiceEnquiry, id=object_id)
        success = retry_service_enquiry_notification(enquiry, request=request)
        if success:
            messages.success(request, f"Email notification for Enquiry #{enquiry.enquiry_id} sent successfully to connectthehomefirst@gmail.com.")
        else:
            messages.error(request, f"Failed to send email notification for Enquiry #{enquiry.enquiry_id}. Please check SMTP configuration.")
        return redirect('admin:services_serviceenquiry_change', object_id)

    def match_providers_view(self, request, object_id):
        enquiry = get_object_or_404(ServiceEnquiry, id=object_id)

        matching_providers = ServiceProvider.objects.filter(
            approval_status=ProviderApprovalStatusChoices.APPROVED,
            is_active=True,
            is_published=True
        )

        if enquiry.category:
            matching_providers = matching_providers.filter(
                models.Q(category=enquiry.category) | models.Q(categories=enquiry.category)
            )

        matching_providers = matching_providers.distinct()

        if enquiry.city:
            matching_providers = matching_providers.filter(
                service_areas__city=enquiry.city
            ).distinct()

        if request.method == 'POST':
            provider_id = request.POST.get('provider_id')
            if provider_id:
                provider = get_object_or_404(ServiceProvider, id=provider_id)
                assignment, created = ServiceAssignment.objects.get_or_create(
                    enquiry=enquiry,
                    provider=provider,
                    defaults={'assigned_by': request.user}
                )

                old_status = enquiry.status
                enquiry.status = ServiceEnquiryStatusChoices.PROVIDER_ASSIGNED
                enquiry.save()

                ServiceEnquiryStatusHistory.objects.create(
                    enquiry=enquiry,
                    old_status=old_status,
                    new_status=ServiceEnquiryStatusChoices.PROVIDER_ASSIGNED,
                    updated_by=request.user,
                    notes=f"Assigned provider: {provider.business_name} ({provider.provider_id})"
                )

                messages.success(request, f"Successfully assigned provider '{provider.business_name}' to enquiry {enquiry.enquiry_id}.")
                return redirect('admin:services_serviceenquiry_change', object_id)

        context = {
            **self.admin_site.each_context(request),
            'opts': self.model._meta,
            'enquiry': enquiry,
            'matching_providers': matching_providers,
            'title': f"Match Providers for {enquiry.enquiry_id}",
        }
        return render(request, 'admin/services/match_providers.html', context)


@admin.register(ServiceAssignment)
class ServiceAssignmentAdmin(admin.ModelAdmin):
    list_display = ('id', 'enquiry', 'provider', 'response_status', 'quotation_amount', 'assigned_at', 'is_active')
    list_filter = ('response_status', 'is_active', 'assigned_at')
    search_fields = ('enquiry__enquiry_id', 'provider__business_name', 'provider__full_name')
