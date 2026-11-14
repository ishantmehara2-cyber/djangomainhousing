import json
import logging
from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.utils import timezone
from apps.core.models import CompanyNotificationLog

logger = logging.getLogger(__name__)

class CentralNotificationService:
    @staticmethod
    def get_company_notification_email():
        """
        Retrieves the company's configured Gmail/email address from settings.
        Reuses EMAIL_HOST_USER or DEFAULT_FROM_EMAIL.
        """
        email = (
            getattr(settings, 'EMAIL_HOST_USER', '').strip() or
            getattr(settings, 'DEFAULT_FROM_EMAIL', '').strip() or
            'support@thehomefirst.com'
        )
        if '<' in email and '>' in email:
            email = email.split('<')[1].split('>')[0].strip()
        return email

    @classmethod
    def send_company_lead_notification(cls, category, lead_ref, name, mobile, email, details_dict, admin_url=None):
        """
        Centralized internal email notification service.
        Sends email to the company's configured Gmail/email address.
        Maintains audit log in CompanyNotificationLog.
        """
        recipient = cls.get_company_notification_email()

        is_doc_assistance = ("Documents Pending Assistance" in category) or ("Documents Assistance" in category)
        if is_doc_assistance:
            subject = "[THF] Government/Business Registration Documents Assistance Required"
            template_name = 'emails/document_assistance_notification.html'
        else:
            subject = f"[THF] New {category} – #{lead_ref}"
            template_name = 'emails/company_lead_notification.html'

        # Prevent duplicate email dispatches
        existing_sent = CompanyNotificationLog.objects.filter(
            lead_ref=lead_ref,
            notification_type=category,
            status='SENT'
        ).exists()
        if existing_sent:
            logger.info(f"Company notification already sent for {category} #{lead_ref}. Skipping duplicate dispatch.")
            return True

        agency_val = details_dict.get('Agency / Business Name') or details_dict.get('agency') or details_dict.get('agency_name') or 'Not specified'
        city_val = details_dict.get('City') or details_dict.get('city') or details_dict.get('city_name') or ''
        message_val = details_dict.get('Message / Details') or details_dict.get('message') or ''

        context = {
            'category': category,
            'lead_ref': lead_ref,
            'name': name,
            'mobile': mobile,
            'email': email,
            'agency': agency_val,
            'city': city_val,
            'message': message_val,
            'details': details_dict,
            'submission_date': timezone.now().strftime("%d %B %Y, %I:%M %p"),
            'admin_url': admin_url,
            'platform_name': 'The Home First (THF)'
        }

        try:
            html_content = render_to_string(template_name, context)
        except Exception as te:
            logger.error(f"Template rendering error for notification: {te}")
            if is_doc_assistance:
                html_content = (
                    f"<p>A visitor has requested assistance regarding government/business registration documents on The Home First website.</p>"
                    f"<p><strong>Applicant Details:</strong></p>"
                    f"<p>Name: {name}<br>Mobile: {mobile}<br>Email: {email}<br>Business / Agency: {agency_val}<br>City: {city_val}<br>Message: {message_val}</p>"
                    f"<p>Submitted On: {context['submission_date']}</p>"
                    f"<p>Please review this request and contact the applicant to guide them through the registration process.</p>"
                    f"<p>The Home First</p>"
                )
            else:
                html_content = f"<h3>{subject}</h3><p>Ref: #{lead_ref}</p><p>Name: {name}</p><p>Mobile: {mobile}</p><p>Email: {email}</p>"

        if is_doc_assistance:
            text_content = (
                "A visitor has requested assistance regarding government/business registration documents on The Home First website.\n\n"
                "Applicant Details:\n\n"
                f"Name: {name}\n"
                f"Mobile: {mobile}\n"
                f"Email: {email}\n"
                f"Business / Agency: {agency_val}\n"
                f"City: {city_val}\n"
                f"Message: {message_val}\n\n"
                "Email Verification: Successful\n\n"
                f"Submitted On: {context['submission_date']}\n\n"
                "Please review this request and contact the applicant to guide them through the registration process.\n\n"
                "The Home First"
            )
        else:
            text_content = strip_tags(html_content)

        from_email = getattr(settings, 'DEFAULT_FROM_EMAIL', 'The Home First <noreply@thehomefirst.com>')

        log_obj, _ = CompanyNotificationLog.objects.get_or_create(
            lead_ref=lead_ref,
            notification_type=category,
            defaults={
                'recipient': recipient,
                'subject': subject,
                'payload_json': json.dumps(details_dict, default=str),
                'status': 'FAILED'
            }
        )

        try:
            msg = EmailMultiAlternatives(
                subject=subject,
                body=text_content,
                from_email=from_email,
                to=[recipient]
            )
            msg.attach_alternative(html_content, "text/html")
            msg.send(fail_silently=False)

            log_obj.status = 'SENT'
            log_obj.error_message = ''
            log_obj.save(update_fields=['status', 'error_message', 'updated_at'])
            return True
        except Exception as e:
            err_msg = str(e)
            logger.error(f"Failed to dispatch company notification email for #{lead_ref}: {err_msg}")
            log_obj.status = 'FAILED'
            log_obj.error_message = err_msg
            log_obj.save(update_fields=['status', 'error_message', 'updated_at'])
            return False
