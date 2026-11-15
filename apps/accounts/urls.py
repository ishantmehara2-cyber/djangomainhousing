from django.urls import path
from django.contrib.auth import views as auth_views
from apps.accounts.views import (
    register_view,
    documents_assistance_view,
    assistance_send_otp_view,
    assistance_verify_otp_view,
    verify_otp_view,
    verify_login_otp_view,
    resend_otp_view,
    login_view,
    logout_view,
    dashboard_view,
    buyer_dashboard_view,
    tenant_dashboard_view,
    owner_dashboard_view,
    agent_dashboard_view,
    partner_dashboard_view,
    partner_upload_document_view,
    admin_dashboard_view,
    admin_partner_applications_view,
    admin_partner_detail_view,
    admin_download_partner_document_view,
    admin_documents_pending_leads_view,
    admin_documents_pending_detail_view,
    profile_view,
    edit_profile_view,
    update_lead_status_view,
    api_register_view,
    api_verify_registration_otp_view,
    api_login_view,
    api_verify_login_otp_view,
    api_resend_otp_view,
)
from apps.accounts.forms import CustomPasswordResetForm, CustomSetPasswordForm

app_name = 'accounts'

urlpatterns = [
    # Auth Web Pages
    path('auth/register/', register_view, name='register'),
    path('auth/partner-documents-assistance/', documents_assistance_view, name='documents_assistance'),
    path('auth/partner-documents-assistance/send-otp/', assistance_send_otp_view, name='documents_assistance_send_otp'),
    path('auth/partner-documents-assistance/verify-otp/', assistance_verify_otp_view, name='documents_assistance_verify_otp'),
    path('auth/verify-otp/', verify_otp_view, name='verify_otp'),
    path('auth/login/', login_view, name='login'),
    path('auth/verify-login-otp/', verify_login_otp_view, name='verify_login_otp'),
    path('auth/resend-otp/', resend_otp_view, name='resend_otp'),
    path('auth/logout/', logout_view, name='logout'),

    # REST APIs
    path('api/auth/register/', api_register_view, name='api_register'),
    path('api/auth/verify-registration-otp/', api_verify_registration_otp_view, name='api_verify_registration_otp'),
    path('api/auth/login/', api_login_view, name='api_login'),
    path('api/auth/verify-login-otp/', api_verify_login_otp_view, name='api_verify_login_otp'),
    path('api/auth/resend-otp/', api_resend_otp_view, name='api_resend_otp'),

    # Profile
    path('profile/', profile_view, name='profile'),
    path('profile/edit/', edit_profile_view, name='edit_profile'),

    # Dashboards
    path('dashboard/', dashboard_view, name='dashboard'),
    path('dashboard/partner/', partner_dashboard_view, name='partner_dashboard'),
    path('dashboard/partner/upload-document/', partner_upload_document_view, name='partner_upload_document'),
    path('dashboard/buyer/', buyer_dashboard_view, name='buyer_dashboard'),
    path('dashboard/tenant/', tenant_dashboard_view, name='tenant_dashboard'),
    path('dashboard/owner/', owner_dashboard_view, name='owner_dashboard'),
    path('dashboard/agent/', agent_dashboard_view, name='agent_dashboard'),
    path('dashboard/admin/', admin_dashboard_view, name='admin_dashboard'),

    # Admin Verification Portal Routes
    path('admin-panel/partners/', admin_partner_applications_view, name='admin_partner_applications'),
    path('admin/partners/', admin_partner_applications_view),
    path('admin-panel/partners/<int:user_id>/', admin_partner_detail_view, name='admin_partner_detail'),
    path('admin/partners/<int:user_id>/', admin_partner_detail_view),
    path('admin-panel/partners/documents/<int:doc_id>/download/', admin_download_partner_document_view, name='admin_download_partner_document'),
    path('admin/partners/documents/<int:doc_id>/download/', admin_download_partner_document_view),

    # Admin Documents Pending Leads Routes (MODULE 3)
    path('admin-panel/documents-pending-leads/', admin_documents_pending_leads_view, name='admin_documents_pending_leads'),
    path('admin/documents-pending-leads/', admin_documents_pending_leads_view),
    path('admin-panel/documents-pending-leads/<int:lead_id>/', admin_documents_pending_detail_view, name='admin_documents_pending_detail'),
    path('admin/documents-pending-leads/<int:lead_id>/', admin_documents_pending_detail_view),

    # Lead management
    path('leads/<int:lead_id>/update-status/', update_lead_status_view, name='update_lead_status'),

    # Password Reset Workflow
    path('auth/password-reset/', auth_views.PasswordResetView.as_view(
        template_name='auth/password_reset_form.html',
        email_template_name='auth/password_reset_email.html',
        subject_template_name='auth/password_reset_subject.txt',
        form_class=CustomPasswordResetForm,
        success_url='/auth/password-reset/done/'
    ), name='password_reset'),

    path('auth/password-reset/done/', auth_views.PasswordResetDoneView.as_view(
        template_name='auth/password_reset_done.html'
    ), name='password_reset_done'),

    path('auth/password-reset-confirm/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(
        template_name='auth/password_reset_confirm.html',
        form_class=CustomSetPasswordForm,
        success_url='/auth/password-reset-complete/'
    ), name='password_reset_complete_confirm'),

    path('auth/password-reset-complete/', auth_views.PasswordResetCompleteView.as_view(
        template_name='auth/password_reset_complete.html'
    ), name='password_reset_complete'),
]
