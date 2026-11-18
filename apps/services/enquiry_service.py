import logging
from datetime import timedelta
from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.urls import reverse
from django.utils import timezone
from django.db import models
from django.utils.html import strip_tags

from apps.services.models import (
    ServiceEnquiry,
    ServiceEnquiryStatusChoices,
    ServiceEnquiryStatusHistory,
    ServiceEnquiryNotificationLog,
    ServiceNotificationStatusChoices,
    ServiceCategory,
    ServiceProvider,
    ServiceProviderNotificationLog
)

logger = logging.getLogger(__name__)


def get_official_company_email():
    """
    Returns official company email notification recipient address.
    Defaults to connectthehomefirst@gmail.com as required.
    """
    email = getattr(settings, 'EMAIL_HOST_USER', '').strip() or getattr(settings, 'DEFAULT_FROM_EMAIL', '').strip()
    if '<' in email and '>' in email:
        email = email.split('<')[1].split('>')[0].strip()
    if not email or 'example.com' in email:
        email = 'connectthehomefirst@gmail.com'
    return email


def build_admin_enquiry_url(enquiry, request=None):
    """
    Generates a valid direct Django Admin URL for reviewing the enquiry detail page.
    """
    try:
        rel_path = reverse('admin:services_serviceenquiry_change', args=[enquiry.id])
        if request:
            return request.build_absolute_uri(rel_path)
        site_url = getattr(settings, 'SITE_URL', '').rstrip('/')
        if site_url:
            return f"{site_url}{rel_path}"
        return rel_path
    except Exception as e:
        logger.warning(f"Failed to resolve admin detail URL for enquiry #{enquiry.enquiry_id}: {e}")
        return f"/admin/services/serviceenquiry/{enquiry.id}/change/"


def build_admin_provider_url(provider, request=None):
    """
    Generates a valid direct Django Admin URL for reviewing the provider registration application.
    """
    try:
        rel_path = reverse('admin:services_serviceprovider_change', args=[provider.id])
        if request:
            return request.build_absolute_uri(rel_path)
        site_url = getattr(settings, 'SITE_URL', '').rstrip('/')
        if site_url:
            return f"{site_url}{rel_path}"
        return rel_path
    except Exception as e:
        logger.warning(f"Failed to resolve admin detail URL for provider #{provider.provider_id}: {e}")
        return f"/admin/services/serviceprovider/{provider.id}/change/"


def send_service_enquiry_notification(enquiry, request=None, is_retry=False):
    """
    Triggers an automatic email notification to connectthehomefirst@gmail.com for customer service enquiries.
    Logs every attempt in ServiceEnquiryNotificationLog.
    Email failure does NOT raise an exception or roll back the enquiry record in DB.
    """
    recipient = get_official_company_email()
    service_name = enquiry.service_name_display
    subject = f"[THF] New Service Enquiry — {service_name} — {enquiry.enquiry_id}"

    # Check existing notification log
    log_obj = ServiceEnquiryNotificationLog.objects.filter(enquiry=enquiry).first()

    if log_obj and log_obj.delivery_status == ServiceNotificationStatusChoices.SENT and not is_retry:
        logger.info(f"Notification already sent for enquiry {enquiry.enquiry_id}. Skipping duplicate dispatch.")
        return True

    if not log_obj:
        log_obj = ServiceEnquiryNotificationLog.objects.create(
            enquiry=enquiry,
            recipient_email=recipient,
            subject=subject,
            delivery_status=ServiceNotificationStatusChoices.PENDING,
            retry_count=0
        )
    elif is_retry:
        log_obj.retry_count += 1
        log_obj.delivery_status = ServiceNotificationStatusChoices.PENDING
        log_obj.save(update_fields=['retry_count', 'delivery_status'])

    location_str = enquiry.location_display
    locality_str = enquiry.locality_display
    submitted_on_str = enquiry.created_at.strftime("%d %B %Y, %I:%M %p") if enquiry.created_at else timezone.now().strftime("%d %B %Y, %I:%M %p")
    admin_url = build_admin_enquiry_url(enquiry, request)

    body_text = (
        "Hello Team,\n\n"
        "A new service enquiry has been received through The Home First Partner Marketplace.\n\n"
        "Enquiry Details\n\n"
        f"- Enquiry ID: {enquiry.enquiry_id}\n"
        f"- Customer Name: {enquiry.full_name}\n"
        f"- Mobile Number: {enquiry.mobile_number}\n"
        f"- Email Address: {enquiry.email}\n"
        f"- Company Name: {enquiry.company_name or 'Not provided'}\n"
        f"- Service Category: {enquiry.category_name}\n"
        f"- Requested Service: {service_name}\n"
        f"- Location: {location_str}\n"
        f"- Locality: {locality_str}\n"
        f"- Requirement: {enquiry.requirement_description}\n"
        f"- Preferred Contact Method: {enquiry.get_preferred_contact_method_display()}\n"
        f"- Preferred Contact Time: {enquiry.get_preferred_contact_time_display()}\n"
        f"- Submitted On: {submitted_on_str}\n\n"
        "Action Required:\n\n"
        "Please log in to the The Home First Admin Panel, open Service Enquiries and review this enquiry. "
        "Contact the customer and proceed with the required follow-up.\n\n"
        f"Admin Direct Link: {admin_url}\n\n"
        "Regards,\n"
        "The Home First\n"
        "AINexTech LLP\n"
        "Your Property. Your Possibilities."
    )

    body_html = (
        f"<div style='font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; color: #1e293b; font-size: 14px; line-height: 1.6; border: 1px solid #e2e8f0; border-radius: 12px; padding: 24px; background-color: #ffffff;'>"
        f"<div style='background-color: #0f172a; padding: 16px; border-radius: 8px; text-align: center; margin-bottom: 20px;'>"
        f"<h2 style='color: #ffffff; margin: 0; font-size: 18px;'>The Home First — New Service Enquiry</h2>"
        f"</div>"
        f"<p>Hello Team,</p>"
        f"<p>A new service enquiry has been received through <strong>The Home First Partner Marketplace</strong>.</p>"
        f"<h3 style='color: #0f172a; border-bottom: 2px solid #e2e8f0; padding-bottom: 6px; margin-top: 20px;'>Enquiry Details</h3>"
        f"<table style='width: 100%; border-collapse: collapse; font-size: 13px;'>"
        f"<tr><td style='padding: 6px 0; font-weight: bold; width: 35%; color: #475569;'>Enquiry ID:</td><td style='padding: 6px 0; font-weight: bold; color: #0284c7;'>{enquiry.enquiry_id}</td></tr>"
        f"<tr><td style='padding: 6px 0; font-weight: bold; color: #475569;'>Customer Name:</td><td style='padding: 6px 0;'>{enquiry.full_name}</td></tr>"
        f"<tr><td style='padding: 6px 0; font-weight: bold; color: #475569;'>Mobile Number:</td><td style='padding: 6px 0;'>{enquiry.mobile_number}</td></tr>"
        f"<tr><td style='padding: 6px 0; font-weight: bold; color: #475569;'>Email Address:</td><td style='padding: 6px 0;'>{enquiry.email}</td></tr>"
        f"<tr><td style='padding: 6px 0; font-weight: bold; color: #475569;'>Company Name:</td><td style='padding: 6px 0;'>{enquiry.company_name or 'Not provided'}</td></tr>"
        f"<tr><td style='padding: 6px 0; font-weight: bold; color: #475569;'>Service Category:</td><td style='padding: 6px 0;'>{enquiry.category_name}</td></tr>"
        f"<tr><td style='padding: 6px 0; font-weight: bold; color: #475569;'>Requested Service:</td><td style='padding: 6px 0; font-weight: bold;'>{service_name}</td></tr>"
        f"<tr><td style='padding: 6px 0; font-weight: bold; color: #475569;'>Location:</td><td style='padding: 6px 0;'>{location_str}</td></tr>"
        f"<tr><td style='padding: 6px 0; font-weight: bold; color: #475569;'>Locality:</td><td style='padding: 6px 0;'>{locality_str}</td></tr>"
        f"<tr><td style='padding: 6px 0; font-weight: bold; color: #475569;'>Requirement:</td><td style='padding: 6px 0;'>{enquiry.requirement_description}</td></tr>"
        f"<tr><td style='padding: 6px 0; font-weight: bold; color: #475569;'>Preferred Contact:</td><td style='padding: 6px 0;'>{enquiry.get_preferred_contact_method_display()} ({enquiry.get_preferred_contact_time_display()})</td></tr>"
        f"<tr><td style='padding: 6px 0; font-weight: bold; color: #475569;'>Submitted On:</td><td style='padding: 6px 0;'>{submitted_on_str}</td></tr>"
        f"</table>"
        f"<div style='margin-top: 24px; padding: 16px; background-color: #f8fafc; border-left: 4px solid #0284c7; border-radius: 4px;'>"
        f"<p style='margin: 0 0 8px 0; font-weight: bold; color: #0f172a;'>Action Required:</p>"
        f"<p style='margin: 0 0 12px 0;'>Please log in to the <strong>The Home First Admin Panel</strong>, open Service Enquiries and review this enquiry. Contact the customer and proceed with the required follow-up.</p>"
        f"<a href='{admin_url}' style='display: inline-block; background-color: #0284c7; color: #ffffff; text-decoration: none; padding: 10px 18px; border-radius: 6px; font-weight: bold; font-size: 13px;'>Open Enquiry in Admin Panel &rarr;</a>"
        f"</div>"
        f"<hr style='border: 0; border-top: 1px solid #e2e8f0; margin: 24px 0;'>"
        f"<p style='margin: 0; font-size: 12px; color: #64748b;'>Regards,<br><strong>The Home First</strong><br>AINexTech LLP<br><em>Your Property. Your Possibilities.</em></p>"
        f"</div>"
    )

    from_email = getattr(settings, 'DEFAULT_FROM_EMAIL', 'The Home First <connectthehomefirst@gmail.com>')

    try:
        msg = EmailMultiAlternatives(
            subject=subject,
            body=body_text,
            from_email=from_email,
            to=[recipient]
        )
        msg.attach_alternative(body_html, "text/html")
        msg.send(fail_silently=False)

        log_obj.delivery_status = ServiceNotificationStatusChoices.SENT
        log_obj.error_details = ""
        log_obj.save(update_fields=['delivery_status', 'error_details'])

        enquiry.notification_status = ServiceNotificationStatusChoices.SENT
        enquiry.save(update_fields=['notification_status'])
        logger.info(f"Successfully delivered service enquiry email notification for {enquiry.enquiry_id} to {recipient}.")
        return True

    except Exception as e:
        err_msg = str(e)
        logger.error(f"Failed to dispatch service enquiry email notification for {enquiry.enquiry_id}: {err_msg}")

        log_obj.delivery_status = ServiceNotificationStatusChoices.FAILED
        log_obj.error_details = err_msg
        log_obj.save(update_fields=['delivery_status', 'error_details'])

        enquiry.notification_status = ServiceNotificationStatusChoices.FAILED
        enquiry.save(update_fields=['notification_status'])
        return False


def retry_service_enquiry_notification(enquiry, request=None):
    """
    Manually retries email notification for a failed enquiry.
    """
    return send_service_enquiry_notification(enquiry, request=request, is_retry=True)


def send_provider_registration_notification(provider, request=None, is_retry=False):
    """
    Triggers an automatic email notification to connectthehomefirst@gmail.com
    whenever a company or individual submits a Service Provider registration.
    Logs every attempt in ServiceProviderNotificationLog.
    Email failure does NOT raise an exception or roll back provider registration in DB.
    """
    recipient = get_official_company_email()
    subject = f"[THF] New Service Provider Registration — {provider.business_name} — {provider.provider_id}"

    log_obj = ServiceProviderNotificationLog.objects.filter(provider=provider).first()

    if log_obj and log_obj.delivery_status == ServiceNotificationStatusChoices.SENT and not is_retry:
        logger.info(f"Notification already sent for provider registration {provider.provider_id}. Skipping duplicate dispatch.")
        return True

    if not log_obj:
        log_obj = ServiceProviderNotificationLog.objects.create(
            provider=provider,
            recipient_email=recipient,
            subject=subject,
            delivery_status=ServiceNotificationStatusChoices.PENDING,
            retry_count=0
        )
    elif is_retry:
        log_obj.retry_count += 1
        log_obj.delivery_status = ServiceNotificationStatusChoices.PENDING
        log_obj.save(update_fields=['retry_count', 'delivery_status'])

    submitted_on_str = provider.created_at.strftime("%d %B %Y, %I:%M %p") if provider.created_at else timezone.now().strftime("%d %B %Y, %I:%M %p")
    admin_url = build_admin_provider_url(provider, request)
    services_offered_str = provider.services_offered_display
    location_str = provider.location_display

    body_text = (
        "Hello Team,\n\n"
        "A new Service Provider registration application has been received through The Home First Partner Marketplace.\n\n"
        "Applicant & Business Details:\n\n"
        f"- Application / Provider ID: {provider.provider_id}\n"
        f"- Applicant Full Name: {provider.full_name}\n"
        f"- Business / Company Name: {provider.business_name}\n"
        f"- Business Entity Type: {provider.get_business_type_display()}\n"
        f"- Mobile Number: {provider.mobile_number}\n"
        f"- Email Address: {provider.email}\n"
        f"- Business Address: {provider.business_address}\n"
        f"- State, City, Locality & Pincode: {location_str}\n"
        f"- Services Offered: {services_offered_str}\n"
        f"- Operating Locations: {location_str}\n"
        f"- Years of Experience: {provider.years_of_experience} year(s)\n"
        f"- Website: {provider.website or 'Not provided'}\n"
        f"- Submission Date: {submitted_on_str}\n"
        f"- Admin Review Status: {provider.get_approval_status_display()}\n\n"
        "Important Note:\n"
        "This application is currently PENDING ADMIN REVIEW and has NOT been automatically approved.\n\n"
        "Action Required:\n"
        "Please log in to the The Home First Admin Panel, open Service Provider Management, review the registration details and compliance documents, and approve or request additional information.\n\n"
        f"Admin Direct Link: {admin_url}\n\n"
        "Regards,\n"
        "The Home First\n"
        "AINexTech LLP\n"
        "Your Property. Your Possibilities."
    )

    body_html = (
        f"<div style='font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; color: #1e293b; font-size: 14px; line-height: 1.6; border: 1px solid #e2e8f0; border-radius: 12px; padding: 24px; background-color: #ffffff;'>"
        f"<div style='background-color: #0f172a; padding: 16px; border-radius: 8px; text-align: center; margin-bottom: 20px;'>"
        f"<h2 style='color: #ffffff; margin: 0; font-size: 18px;'>The Home First — New Service Provider Application</h2>"
        f"</div>"
        f"<p>Hello Team,</p>"
        f"<p>A new <strong>Service Provider registration</strong> application has been submitted through <strong>The Home First Partner Marketplace</strong>.</p>"
        f"<h3 style='color: #0f172a; border-bottom: 2px solid #e2e8f0; padding-bottom: 6px; margin-top: 20px;'>Applicant & Business Details</h3>"
        f"<table style='width: 100%; border-collapse: collapse; font-size: 13px;'>"
        f"<tr><td style='padding: 6px 0; font-weight: bold; width: 35%; color: #475569;'>Provider ID:</td><td style='padding: 6px 0; font-weight: bold; color: #0284c7;'>{provider.provider_id}</td></tr>"
        f"<tr><td style='padding: 6px 0; font-weight: bold; color: #475569;'>Applicant Name:</td><td style='padding: 6px 0;'>{provider.full_name}</td></tr>"
        f"<tr><td style='padding: 6px 0; font-weight: bold; color: #475569;'>Business Name:</td><td style='padding: 6px 0; font-weight: bold;'>{provider.business_name}</td></tr>"
        f"<tr><td style='padding: 6px 0; font-weight: bold; color: #475569;'>Business Type:</td><td style='padding: 6px 0;'>{provider.get_business_type_display()}</td></tr>"
        f"<tr><td style='padding: 6px 0; font-weight: bold; color: #475569;'>Mobile Number:</td><td style='padding: 6px 0;'>{provider.mobile_number}</td></tr>"
        f"<tr><td style='padding: 6px 0; font-weight: bold; color: #475569;'>Email Address:</td><td style='padding: 6px 0;'>{provider.email}</td></tr>"
        f"<tr><td style='padding: 6px 0; font-weight: bold; color: #475569;'>Business Address:</td><td style='padding: 6px 0;'>{provider.business_address}</td></tr>"
        f"<tr><td style='padding: 6px 0; font-weight: bold; color: #475569;'>Location & Pincode:</td><td style='padding: 6px 0;'>{location_str}</td></tr>"
        f"<tr><td style='padding: 6px 0; font-weight: bold; color: #475569;'>Services Offered:</td><td style='padding: 6px 0;'>{services_offered_str}</td></tr>"
        f"<tr><td style='padding: 6px 0; font-weight: bold; color: #475569;'>Years of Experience:</td><td style='padding: 6px 0;'>{provider.years_of_experience} year(s)</td></tr>"
        f"<tr><td style='padding: 6px 0; font-weight: bold; color: #475569;'>Website:</td><td style='padding: 6px 0;'>{provider.website or 'Not provided'}</td></tr>"
        f"<tr><td style='padding: 6px 0; font-weight: bold; color: #475569;'>Submission Date:</td><td style='padding: 6px 0;'>{submitted_on_str}</td></tr>"
        f"<tr><td style='padding: 6px 0; font-weight: bold; color: #475569;'>Admin Review Status:</td><td style='padding: 6px 0; color: #d97706; font-weight: bold;'>{provider.get_approval_status_display()}</td></tr>"
        f"</table>"
        f"<div style='margin-top: 24px; padding: 16px; background-color: #fffbebfb; border-left: 4px solid #d97706; border-radius: 4px;'>"
        f"<p style='margin: 0 0 6px 0; font-weight: bold; color: #b45309;'>Status Notification:</p>"
        f"<p style='margin: 0;'>This application is currently <strong>Pending Admin Review</strong> and has <strong>NOT</strong> been automatically approved.</p>"
        f"</div>"
        f"<div style='margin-top: 16px; padding: 16px; background-color: #f8fafc; border-left: 4px solid #0284c7; border-radius: 4px;'>"
        f"<p style='margin: 0 0 8px 0; font-weight: bold; color: #0f172a;'>Action Required:</p>"
        f"<p style='margin: 0 0 12px 0;'>Please log in to the <strong>The Home First Admin Panel</strong>, review the provider registration details and compliance documents, and perform approval or document verification.</p>"
        f"<a href='{admin_url}' style='display: inline-block; background-color: #0284c7; color: #ffffff; text-decoration: none; padding: 10px 18px; border-radius: 6px; font-weight: bold; font-size: 13px;'>Review Application in Admin Panel &rarr;</a>"
        f"</div>"
        f"<hr style='border: 0; border-top: 1px solid #e2e8f0; margin: 24px 0;'>"
        f"<p style='margin: 0; font-size: 12px; color: #64748b;'>Regards,<br><strong>The Home First</strong><br>AINexTech LLP<br><em>Your Property. Your Possibilities.</em></p>"
        f"</div>"
    )

    from_email = getattr(settings, 'DEFAULT_FROM_EMAIL', 'The Home First <connectthehomefirst@gmail.com>')

    try:
        msg = EmailMultiAlternatives(
            subject=subject,
            body=body_text,
            from_email=from_email,
            to=[recipient]
        )
        msg.attach_alternative(body_html, "text/html")
        msg.send(fail_silently=False)

        log_obj.delivery_status = ServiceNotificationStatusChoices.SENT
        log_obj.error_details = ""
        log_obj.save(update_fields=['delivery_status', 'error_details'])

        provider.notification_status = ServiceNotificationStatusChoices.SENT
        provider.save(update_fields=['notification_status'])
        logger.info(f"Successfully delivered Service Provider registration notification for {provider.provider_id} to {recipient}.")
        return True

    except Exception as e:
        err_msg = str(e)
        logger.error(f"Failed to dispatch Service Provider registration notification for {provider.provider_id}: {err_msg}")

        log_obj.delivery_status = ServiceNotificationStatusChoices.FAILED
        log_obj.error_details = err_msg
        log_obj.save(update_fields=['delivery_status', 'error_details'])

        provider.notification_status = ServiceNotificationStatusChoices.FAILED
        provider.save(update_fields=['notification_status'])
        return False


def retry_provider_registration_notification(provider, request=None):
    """
    Manually retries email notification for a failed provider registration.
    """
    return send_provider_registration_notification(provider, request=request, is_retry=True)


def create_service_enquiry(
    service,
    full_name,
    mobile_number,
    email,
    requirement_description,
    category=None,
    requested_service_name=None,
    company_name=None,
    state=None,
    city=None,
    locality=None,
    locality_name=None,
    preferred_contact_method='PHONE',
    preferred_contact_time='Anytime',
    user=None,
    request=None
):
    """
    Centralized service enquiry lead handler.
    1. Validates inputs & prevents duplicate submissions within 120 seconds.
    2. Permanent DB storage of enquiry lead (Primary requirement).
    3. Auto-generates unique enquiry ID.
    4. Records initial status history log.
    5. Attempts immediate email notification to connectthehomefirst@gmail.com.
    """
    mobile_clean = str(mobile_number).strip()
    email_clean = str(email).strip().lower()

    # Determine service name and category
    if service:
        svc_name_str = service.name
        cat_obj = service.category
    else:
        svc_name_str = str(requested_service_name).strip() if requested_service_name else "Custom Service Request"
        cat_obj = category

    # 1. Anti-duplicate submission check within 120 seconds cutoff window
    recent_cutoff = timezone.now() - timedelta(seconds=120)
    qs = ServiceEnquiry.objects.filter(
        mobile_number=mobile_clean,
        email__iexact=email_clean,
        created_at__gte=recent_cutoff
    )
    if service:
        qs = qs.filter(service=service)
    elif requested_service_name:
        qs = qs.filter(requested_service_name__iexact=requested_service_name)

    existing_duplicate = qs.order_by('-created_at').first()

    if existing_duplicate:
        logger.info(f"Duplicate service enquiry prevented for {mobile_clean} / {email_clean} on {svc_name_str}.")
        return existing_duplicate, False, f"Your enquiry for '{svc_name_str}' has already been received recently. Reference ID: #{existing_duplicate.enquiry_id}."

    # 2. Permanent Database Save
    enquiry = ServiceEnquiry.objects.create(
        service=service,
        category=cat_obj,
        requested_service_name=svc_name_str,
        full_name=str(full_name).strip(),
        mobile_number=mobile_clean,
        email=email_clean,
        company_name=str(company_name).strip() if company_name else None,
        state=state,
        city=city,
        locality=locality,
        locality_name=str(locality_name).strip() if locality_name else None,
        requirement_description=str(requirement_description).strip(),
        preferred_contact_method=preferred_contact_method,
        preferred_contact_time=preferred_contact_time,
        status=ServiceEnquiryStatusChoices.NEW,
        user=user,
        notification_status=ServiceNotificationStatusChoices.PENDING
    )

    # 3. Save initial Status History
    ServiceEnquiryStatusHistory.objects.create(
        enquiry=enquiry,
        old_status='',
        new_status=ServiceEnquiryStatusChoices.NEW,
        notes='Initial customer enquiry lead submitted via Partner Marketplace.'
    )

    # 4. Trigger Email Notification (Email failure will NOT roll back DB record)
    send_service_enquiry_notification(enquiry, request=request)

    success_msg = (
        f"Thank you, {enquiry.full_name}! Your service requirement for '{svc_name_str}' has been submitted successfully. "
        f"Enquiry Reference ID: #{enquiry.enquiry_id}."
    )
    return enquiry, True, success_msg
