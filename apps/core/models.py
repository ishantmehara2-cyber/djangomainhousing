import json
from django.db import models
from django.conf import settings
from django.core.exceptions import ValidationError

class CMSContent(models.Model):
    slug = models.SlugField(max_length=100, unique=True)
    title = models.CharField(max_length=255)
    content = models.TextField()
    meta_title = models.CharField(max_length=255, null=True, blank=True)
    meta_desc = models.TextField(null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'cms_contents'

    def __str__(self):
        return self.title

class FeatureFlag(models.Model):
    key = models.CharField(max_length=100, unique=True)
    description = models.TextField(null=True, blank=True)
    is_enabled = models.BooleanField(default=False)

    class Meta:
        db_table = 'feature_flags'

    def __str__(self):
        return f"{self.key} ({'ON' if self.is_enabled else 'OFF'})"

class SystemSetting(models.Model):
    key = models.CharField(max_length=100, unique=True)
    value = models.TextField()

    class Meta:
        db_table = 'system_settings'

    def __str__(self):
        return f"{self.key} = {self.value}"

class FAQCategory(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=100, unique=True)
    description = models.TextField(null=True, blank=True)
    display_order = models.IntegerField(default=0)

    class Meta:
        db_table = 'faq_categories'
        ordering = ['display_order', 'name']
        verbose_name_plural = 'FAQ Categories'

    def __str__(self):
        return self.name

class FAQItem(models.Model):
    category = models.ForeignKey(FAQCategory, on_delete=models.CASCADE, related_name='faqs')
    question = models.CharField(max_length=255)
    answer = models.TextField()
    display_order = models.IntegerField(default=0)
    is_published = models.BooleanField(default=True)

    class Meta:
        db_table = 'faq_items'
        ordering = ['display_order', 'id']
        verbose_name_plural = 'FAQ Items'

    def __str__(self):
        return self.question

class TicketCategoryChoices(models.TextChoices):
    ACCOUNT = 'ACCOUNT', 'Account and Login'
    LISTING = 'LISTING', 'Property Listing'
    ENQUIRY = 'ENQUIRY', 'Property Enquiries & Visits'
    PAYMENT = 'PAYMENT', 'Payments and Subscriptions'
    TECHNICAL = 'TECHNICAL', 'Technical Issues'
    OTHER = 'OTHER', 'Other'

class TicketStatusChoices(models.TextChoices):
    OPEN = 'OPEN', 'Open'
    IN_PROGRESS = 'IN_PROGRESS', 'In Progress'
    WAITING_FOR_USER = 'WAITING_FOR_USER', 'Waiting for User'
    RESOLVED = 'RESOLVED', 'Resolved'
    CLOSED = 'CLOSED', 'Closed'

class TicketPriorityChoices(models.TextChoices):
    LOW = 'LOW', 'Low'
    MEDIUM = 'MEDIUM', 'Medium'
    HIGH = 'HIGH', 'High'
    URGENT = 'URGENT', 'Urgent'

class SupportTicket(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='support_tickets')
    ticket_id = models.CharField(max_length=50, unique=True)
    category = models.CharField(max_length=30, choices=TicketCategoryChoices.choices, default=TicketCategoryChoices.OTHER)
    subject = models.CharField(max_length=255)
    description = models.TextField()
    status = models.CharField(max_length=30, choices=TicketStatusChoices.choices, default=TicketStatusChoices.OPEN)
    priority = models.CharField(max_length=20, choices=TicketPriorityChoices.choices, default=TicketPriorityChoices.MEDIUM)
    attachment = models.FileField(upload_to='support_attachments/', null=True, blank=True)
    assigned_to = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='assigned_tickets')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'support_tickets'
        ordering = ['-created_at']

    def __str__(self):
        return f"TICKET-{self.ticket_id} ({self.get_status_display()})"

class TicketMessage(models.Model):
    ticket = models.ForeignKey(SupportTicket, on_delete=models.CASCADE, related_name='messages')
    sender = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='ticket_messages')
    message = models.TextField()
    is_internal = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'ticket_messages'
        ordering = ['created_at']


class ContactEnquiry(models.Model):
    reference_number = models.CharField(max_length=50, unique=True, db_index=True)
    name = models.CharField(max_length=255)
    email = models.EmailField()
    phone = models.CharField(max_length=20, blank=True, null=True)
    subject = models.CharField(max_length=255, blank=True, null=True)
    message = models.TextField()
    status = models.CharField(max_length=30, default='NEW')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'contact_enquiries'
        ordering = ['-created_at']

    def __str__(self):
        return f"#{self.reference_number} - {self.name} ({self.email})"


class CompanyNotificationLog(models.Model):
    lead_ref = models.CharField(max_length=100, db_index=True)
    notification_type = models.CharField(max_length=100)
    recipient = models.CharField(max_length=255)
    subject = models.CharField(max_length=255)
    status = models.CharField(
        max_length=20,
        choices=[('SENT', 'Sent'), ('FAILED', 'Failed')],
        default='SENT'
    )
    error_message = models.TextField(blank=True, null=True)
    payload_json = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'company_notification_logs'
        ordering = ['-created_at']

    def __str__(self):
        return f"[{self.status}] {self.notification_type} - {self.lead_ref}"


class SEOPage(models.Model):
    ROBOTS_INDEX_CHOICES = [
        ('index', 'Index'),
        ('noindex', 'Noindex'),
    ]
    ROBOTS_FOLLOW_CHOICES = [
        ('follow', 'Follow'),
        ('nofollow', 'Nofollow'),
    ]
    TWITTER_CARD_CHOICES = [
        ('summary_large_image', 'Summary Card with Large Image'),
        ('summary', 'Summary Card'),
    ]

    page_name = models.CharField(max_length=255, help_text="Human-readable name of the page (e.g., Homepage, Buy Properties)")
    page_url = models.CharField(max_length=255, unique=True, db_index=True, help_text="Path of the page starting with '/' (e.g. '/' or '/properties/buy/')")
    url_slug = models.SlugField(max_length=255, blank=True, null=True, help_text="Optional unique slug for routing identification")

    seo_title = models.CharField(max_length=255, help_text="SEO Title tag (50-60 characters recommended)")
    meta_description = models.TextField(help_text="SEO Meta Description (150-160 characters recommended)")
    meta_keywords = models.CharField(max_length=255, blank=True, null=True, help_text="Optional legacy meta keywords comma separated")

    canonical_url = models.CharField(max_length=500, blank=True, null=True, help_text="Optional custom canonical URL. Defaults to page absolute URL if blank.")
    robots_index = models.CharField(max_length=20, choices=ROBOTS_INDEX_CHOICES, default='index')
    robots_follow = models.CharField(max_length=20, choices=ROBOTS_FOLLOW_CHOICES, default='follow')

    og_title = models.CharField(max_length=255, blank=True, null=True, help_text="Open Graph Title. Defaults to SEO Title if blank.")
    og_description = models.TextField(blank=True, null=True, help_text="Open Graph Description. Defaults to Meta Description if blank.")
    og_image_file = models.ImageField(upload_to='seo/og/', blank=True, null=True, help_text="Upload Open Graph social share image")
    og_image_url = models.CharField(max_length=500, blank=True, null=True, help_text="Or specify absolute URL to Open Graph image")
    og_type = models.CharField(max_length=50, default='website')

    twitter_card_type = models.CharField(max_length=50, choices=TWITTER_CARD_CHOICES, default='summary_large_image')
    twitter_title = models.CharField(max_length=255, blank=True, null=True, help_text="Twitter Title. Defaults to OG Title if blank.")
    twitter_description = models.TextField(blank=True, null=True, help_text="Twitter Description. Defaults to OG Description if blank.")
    twitter_image_file = models.ImageField(upload_to='seo/twitter/', blank=True, null=True, help_text="Upload Twitter share image")
    twitter_image_url = models.CharField(max_length=500, blank=True, null=True, help_text="Or specify absolute URL to Twitter image")

    structured_data_json = models.TextField(blank=True, null=True, help_text="Valid JSON-LD schema markup script content")
    is_in_sitemap = models.BooleanField(default=True, help_text="Include this page in XML sitemap")
    sitemap_priority = models.DecimalField(max_digits=2, decimal_places=1, default=0.8, help_text="Sitemap priority between 0.0 and 1.0")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'seo_pages'
        verbose_name = 'SEO Page'
        verbose_name_plural = 'SEO Pages'
        ordering = ['page_name']

    def __str__(self):
        return f"{self.page_name} ({self.page_url})"

    def clean(self):
        super().clean()
        if self.page_url:
            self.page_url = self.page_url.strip()
            if not self.page_url.startswith('/'):
                self.page_url = '/' + self.page_url
        if self.structured_data_json:
            try:
                json.loads(self.structured_data_json)
            except Exception as e:
                raise ValidationError({'structured_data_json': f"Invalid JSON-LD format: {str(e)}"})
        if self.sitemap_priority is not None:
            if self.sitemap_priority < 0.0 or self.sitemap_priority > 1.0:
                raise ValidationError({'sitemap_priority': "Sitemap priority must be between 0.0 and 1.0"})

