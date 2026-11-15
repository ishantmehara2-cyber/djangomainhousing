from unittest.mock import patch
from decimal import Decimal
from django.test import TestCase, Client
from django.urls import reverse
from django.core import mail
from django.core.management import call_command
import django.test.client

from apps.services.models import (
    BankPartner,
    BankLoanEnquiry,
    RentalAgreementRequest,
    AgreementType,
    BankCategoryChoices,
    ServiceCategory,
    Service,
    ServiceProvider,
    ProviderApprovalStatusChoices,
    ServiceProviderNotificationLog,
    ServiceEnquiry,
    ServiceEnquiryNotificationLog,
    ServiceEnquiryStatusHistory,
    ServiceNotificationStatusChoices,
    ServiceEnquiryStatusChoices
)
from apps.properties.models import Property, PropertyType
from apps.locations.models import State, City, Locality
from apps.accounts.models import User, RoleChoices
from apps.services.enquiry_service import (
    create_service_enquiry,
    retry_service_enquiry_notification,
    retry_provider_registration_notification
)

django.test.client.store_rendered_templates = lambda *args, **kwargs: None


class BankManagementAndServicesTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.admin_user = User.objects.create_superuser(
            username="admin_user",
            email="admin@example.com",
            password="AdminPassword123!",
            role=RoleChoices.ADMIN
        )
        self.customer_user = User.objects.create_user(
            username="customer_user",
            email="customer@example.com",
            password="CustomerPassword123!",
            role=RoleChoices.BUYER
        )

        self.hdfc, _ = BankPartner.objects.get_or_create(
            slug="hdfc-bank",
            defaults={
                'name': "HDFC Bank",
                'category': BankCategoryChoices.PRIVATE_SECTOR,
                'min_interest_rate': Decimal("8.40"),
                'max_tenure_years': 30,
                'display_order': 1,
                'is_active': True
            }
        )
        self.sbi, _ = BankPartner.objects.get_or_create(
            slug="state-bank-of-india-sbi",
            defaults={
                'name': "State Bank of India (SBI)",
                'category': BankCategoryChoices.PUBLIC_SECTOR,
                'min_interest_rate': Decimal("8.40"),
                'max_tenure_years': 30,
                'display_order': 2,
                'is_active': True
            }
        )
        self.icici, _ = BankPartner.objects.get_or_create(
            slug="icici-bank",
            defaults={
                'name': "ICICI Bank",
                'category': BankCategoryChoices.PRIVATE_SECTOR,
                'min_interest_rate': Decimal("8.40"),
                'max_tenure_years': 30,
                'display_order': 3,
                'is_active': True
            }
        )

    def test_1_admin_adds_new_bank_kotak(self):
        """TEST 1: Admin adds Kotak Mahindra Bank -> appears automatically on public Bank Loans page."""
        self.client.force_login(self.admin_user)
        add_data = {
            'name': 'Kotak Mahindra Bank',
            'slug': 'kotak-mahindra-bank',
            'category': BankCategoryChoices.PRIVATE_SECTOR,
            'display_order': 5,
            'is_active': True,
            'min_interest_rate': '8.70',
            'max_tenure_years': '30',
            'processing_fee_info': '0.50% or ₹10,000 + GST',
            'benefits_raw': 'Instant digital sanction\nSpecial interest concessions'
        }
        response = self.client.post(reverse('services:admin-add-bank'), add_data)
        self.assertRedirects(response, reverse('services:admin-bank-management'))

        kotak = BankPartner.objects.get(slug='kotak-mahindra-bank')
        self.assertEqual(float(kotak.min_interest_rate), 8.70)
        self.assertIn("Instant digital sanction", kotak.get_benefits_list)

        public_res = self.client.get(reverse('services:bank-loans'))
        self.assertEqual(public_res.status_code, 200)
        self.assertContains(public_res, "Kotak Mahindra Bank")

    def test_2_admin_edits_hdfc_interest_rate(self):
        """TEST 2: Admin edits HDFC Bank interest rate -> updated rate appears on public page."""
        self.client.force_login(self.admin_user)
        edit_data = {
            'name': 'HDFC Bank',
            'slug': 'hdfc-bank',
            'category': BankCategoryChoices.PRIVATE_SECTOR,
            'display_order': 1,
            'is_active': True,
            'min_interest_rate': '8.75',
            'max_tenure_years': '30',
            'processing_fee_info': '0.50% of loan amount + GST',
            'benefits_raw': 'Instant digital sanction'
        }
        response = self.client.post(reverse('services:admin-edit-bank', kwargs={'pk': self.hdfc.id}), edit_data)
        self.assertRedirects(response, reverse('services:admin-bank-management'))

        self.hdfc.refresh_from_db()
        self.assertEqual(float(self.hdfc.min_interest_rate), 8.75)

    def test_3_admin_changes_sbi_processing_fee(self):
        """TEST 3: Admin changes SBI processing fee -> new processing fee appears publicly."""
        self.client.force_login(self.admin_user)
        edit_data = {
            'name': 'State Bank of India (SBI)',
            'slug': 'state-bank-of-india-sbi',
            'category': BankCategoryChoices.PUBLIC_SECTOR,
            'display_order': 2,
            'is_active': True,
            'min_interest_rate': '8.40',
            'max_tenure_years': '30',
            'processing_fee_info': 'Zero Processing Fee Offer',
            'benefits_raw': 'Concession on CIBIL score 750+'
        }
        response = self.client.post(reverse('services:admin-edit-bank', kwargs={'pk': self.sbi.id}), edit_data)
        self.assertRedirects(response, reverse('services:admin-bank-management'))

        self.sbi.refresh_from_db()
        self.assertEqual(self.sbi.processing_fee_info, "Zero Processing Fee Offer")

    def test_4_admin_deactivates_icici_bank(self):
        """TEST 4: Admin deactivates ICICI Bank -> disappears from public page but stays manageable in admin portal."""
        self.client.force_login(self.admin_user)
        toggle_res = self.client.post(reverse('services:admin-toggle-bank-active', kwargs={'pk': self.icici.id}))
        self.assertRedirects(toggle_res, reverse('services:admin-bank-management'))

        self.icici.refresh_from_db()
        self.assertFalse(self.icici.is_active)

        admin_res = self.client.get(reverse('services:admin-bank-management'))
        self.assertContains(admin_res, "ICICI Bank")

    def test_5_unauthorized_customer_admin_api_rejection(self):
        """TEST 5: Unauthorized customer attempts to access admin bank-management APIs -> 403 / Redirected."""
        self.client.force_login(self.customer_user)
        api_res = self.client.get(reverse('services:api-admin-banks-list'))
        self.assertIn(api_res.status_code, [302, 403])

        admin_view_res = self.client.get(reverse('services:admin-bank-management'))
        self.assertEqual(admin_view_res.status_code, 302)


class ServiceProviderSingleSourceOfTruthTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.admin_user = User.objects.create_superuser(
            username="admin_test",
            email="admin@example.com",
            password="AdminPassword123!",
            role=RoleChoices.ADMIN
        )
        self.cat_pest = ServiceCategory.objects.create(
            name="Pest Control & Cleaning",
            slug="pest-control-cleaning",
            description="Professional home pest control and deep cleaning services.",
            approval_status='APPROVED',
            is_published=True,
            is_active=True
        )

    def test_1_provider_registration_defaults_to_pending_and_hidden(self):
        """ServiceProvider registration defaults approval_status=PENDING, is_active=False, is_featured=False, is_published=False and remains hidden."""
        mail.outbox = []
        post_data = {
            'full_name': 'Karan Mehta',
            'mobile_number': '9822001122',
            'email': 'karan.mehta@apexservices.com',
            'business_name': 'Apex Facility Solutions Pvt Ltd',
            'business_type': 'PrivateLimited',
            'business_description': 'Professional property cleaning and maintenance.',
            'business_address': 'Plot 42, MIDC Industrial Area, Thane West',
            'pincode': '400601',
            'category': self.cat_pest.id
        }
        res = self.client.post(reverse('services:register-provider'), post_data)
        self.assertRedirects(res, reverse('services:register-provider'))

        provider = ServiceProvider.objects.filter(email='karan.mehta@apexservices.com').first()
        self.assertIsNotNone(provider)
        self.assertEqual(provider.approval_status, ProviderApprovalStatusChoices.PENDING)
        self.assertFalse(provider.is_active)
        self.assertFalse(provider.is_featured)
        self.assertFalse(provider.is_published)
        self.assertFalse(provider.is_publicly_visible)

        # Confirm not visible on public marketplace homepage or category page
        res_mp = self.client.get(reverse('services:partner-marketplace'))
        self.assertNotContains(res_mp, "Apex Facility Solutions Pvt Ltd")

    def test_2_admin_approves_activates_publishes_provider_makes_it_visible(self):
        """When admin approves (APPROVED), activates (is_active=True), and publishes (is_published=True) a provider, it appears publicly."""
        provider = ServiceProvider.objects.create(
            full_name="Rajesh Patel",
            mobile_number="9876543210",
            email="patel@apex.com",
            business_name="Apex Maintenance Corp",
            business_address="123 Main Street",
            category=self.cat_pest,
            approval_status=ProviderApprovalStatusChoices.APPROVED,
            is_active=True,
            is_published=True
        )
        self.assertTrue(provider.is_publicly_visible)

        res_mp = self.client.get(reverse('services:partner-marketplace') + '?tab=providers')
        self.assertEqual(res_mp.status_code, 200)
        self.assertContains(res_mp, "Apex Maintenance Corp")

        res_cat = self.client.get(reverse('services:service-category-detail', kwargs={'slug': self.cat_pest.slug}))
        self.assertEqual(res_cat.status_code, 200)
        self.assertContains(res_cat, "Apex Maintenance Corp")

    def test_3_rejected_or_unpublished_provider_disappears(self):
        """Rejecting or unpublishing a provider removes it from public frontend visibility immediately."""
        provider = ServiceProvider.objects.create(
            full_name="Suresh Verma",
            mobile_number="9112233445",
            email="verma@example.com",
            business_name="Verma Legal Services",
            business_address="45 Law Chambers",
            category=self.cat_pest,
            approval_status=ProviderApprovalStatusChoices.APPROVED,
            is_active=True,
            is_published=True
        )
        self.assertTrue(provider.is_publicly_visible)

        # Unpublish provider
        provider.is_published = False
        provider.save()
        self.assertFalse(provider.is_publicly_visible)

        res_mp = self.client.get(reverse('services:partner-marketplace') + '?tab=providers')
        self.assertNotContains(res_mp, "Verma Legal Services")

        # Reject provider
        provider.approval_status = ProviderApprovalStatusChoices.REJECTED
        provider.save()
        self.assertFalse(provider.is_publicly_visible)

    def test_4_featured_provider_visibility(self):
        """Featured providers appear in featured section when approved, active, and published."""
        provider = ServiceProvider.objects.create(
            full_name="Anita Sharma",
            mobile_number="9998887776",
            email="anita@star.com",
            business_name="Star Enterprise Solutions",
            business_address="78 Business Park",
            category=self.cat_pest,
            approval_status=ProviderApprovalStatusChoices.APPROVED,
            is_active=True,
            is_published=True,
            is_featured=True
        )
        self.assertTrue(provider.is_publicly_visible)

        res_mp = self.client.get(reverse('services:partner-marketplace'))
        self.assertContains(res_mp, "Star Enterprise Solutions")

    def test_5_customer_service_request_creates_lead(self):
        """Customer submitting a service request creates a ServiceEnquiry lead and sends email to connectthehomefirst@gmail.com."""
        mail.outbox = []

        post_data = {
            'category_slug': self.cat_pest.slug,
            'requested_service_name': 'Villa Deep Cleaning & Sanitization',
            'full_name': 'Deepak Joshi',
            'mobile_number': '9876500112',
            'email': 'deepak.joshi@example.com',
            'requirement_description': 'Need full villa deep cleaning service.'
        }
        res = self.client.post(reverse('services:submit-service-enquiry'), post_data)
        self.assertEqual(res.status_code, 302)

        lead = ServiceEnquiry.objects.filter(email='deepak.joshi@example.com').first()
        self.assertIsNotNone(lead)
        self.assertEqual(lead.category, self.cat_pest)
        self.assertEqual(lead.requested_service_name, 'Villa Deep Cleaning & Sanitization')
        self.assertEqual(lead.status, ServiceEnquiryStatusChoices.NEW)

        self.assertEqual(len(mail.outbox), 1)
        email_msg = mail.outbox[0]
        self.assertIn("connectthehomefirst@gmail.com", email_msg.to)
        self.assertIn("Villa Deep Cleaning & Sanitization", email_msg.subject)
        self.assertIn(lead.enquiry_id, email_msg.body)


class ServiceCatalogueTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        call_command('seed_services')

    def test_1_seed_services_creates_8_categories_and_92_services(self):
        """Verify that seed_services creates exactly 8 categories and 92 services."""
        self.assertEqual(ServiceCategory.objects.count(), 8)
        self.assertEqual(Service.objects.count(), 92)

    def test_2_category_detail_page_loads_services(self):
        """Category detail page displays individual services under that category."""
        category = ServiceCategory.objects.get(name="Business Management & CRM")
        url = reverse('services:service-category-detail', kwargs={'slug': category.slug})
        res = self.client.get(url)
        self.assertEqual(res.status_code, 200)
        self.assertContains(res, "Business Management")
        self.assertContains(res, "Real Estate CRM")
        self.assertContains(res, "Lead Management")

    def test_3_service_detail_page_loads(self):
        """Individual service detail page displays header, benefits, inclusions, FAQs, and Apply Now form."""
        service = Service.objects.get(name="Real Estate CRM")
        url = reverse('services:service-detail', kwargs={'slug': service.slug})
        res = self.client.get(url)
        self.assertEqual(res.status_code, 200)
        self.assertContains(res, service.name)
        self.assertContains(res, service.service_id)
        self.assertContains(res, "About This Service")
        self.assertContains(res, "Key Benefits")
        self.assertContains(res, "What is Included")
        self.assertContains(res, "How It Works")
        self.assertContains(res, "Request This Service")

    def test_4_visibility_rules_enforced(self):
        """Unpublished or non-approved services return 404 on direct URL access."""
        service = Service.objects.get(name="Real Estate CRM")
        service.is_published = False
        service.save()

        url = reverse('services:service-detail', kwargs={'slug': service.slug})
        res = self.client.get(url)
        self.assertEqual(res.status_code, 404)

        service.is_published = True
        service.approval_status = 'REJECTED'
        service.save()
        res = self.client.get(url)
        self.assertEqual(res.status_code, 404)

    def test_5_apply_now_workflow_creates_enquiry_and_sends_email(self):
        """Applying for a service creates a ServiceEnquiry lead in DB and triggers email to connectthehomefirst@gmail.com."""
        mail.outbox = []
        service = Service.objects.get(name="Home Loan for Customers")

        post_data = {
            'service_id': service.id,
            'service_slug': service.slug,
            'full_name': 'Rohan Mehta',
            'mobile_number': '9876543210',
            'email': 'rohan.mehta@example.com',
            'company_name': 'Mehta Enterprises',
            'requirement_description': 'Need 50 Lakh home loan for 3BHK flat in Bandra West.',
            'preferred_contact_method': 'WHATSAPP',
            'preferred_contact_time': 'Morning'
        }
        res = self.client.post(reverse('services:submit-service-enquiry'), post_data)
        self.assertEqual(res.status_code, 302)

        enquiry = ServiceEnquiry.objects.filter(email='rohan.mehta@example.com').first()
        self.assertIsNotNone(enquiry)
        self.assertEqual(enquiry.service, service)
        self.assertEqual(enquiry.category, service.category)
        self.assertTrue(enquiry.enquiry_id.startswith('ENQ-'))
        self.assertEqual(enquiry.status, ServiceEnquiryStatusChoices.NEW)

        # Verify Email Dispatch
        self.assertEqual(len(mail.outbox), 1)
        email_msg = mail.outbox[0]
        self.assertIn("connectthehomefirst@gmail.com", email_msg.to)
        self.assertIn("[THF] New Service Enquiry", email_msg.subject)
        self.assertIn(service.name, email_msg.subject)
        self.assertIn(enquiry.enquiry_id, email_msg.subject)
        self.assertIn("Rohan Mehta", email_msg.body)

    def test_6_seed_command_idempotency(self):
        """Running seed_services multiple times maintains exactly 8 categories and 92 services without duplicates."""
        call_command('seed_services')
        call_command('seed_services')
        self.assertEqual(ServiceCategory.objects.count(), 8)
        self.assertEqual(Service.objects.count(), 92)

