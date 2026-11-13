from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from apps.accounts.models import RoleChoices
from apps.services.models import BankPartner, LoanInquiryLead, LoanInquiryNote, LoanInquiryStatusHistory, LoanInquiryStatusChoices, EmploymentTypeChoices

import django.test.client
django.test.client.store_rendered_templates = lambda *args, **kwargs: None

User = get_user_model()

class LoanInquiryLeadSystemTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.bank = BankPartner.objects.create(
            name='Test HDFC Bank',
            slug='test-hdfc-bank',
            min_interest_rate=8.50,
            is_active=True
        )

        self.admin_user = User.objects.create_superuser(
            username='admin_lead@housing.local',
            email='admin_lead@housing.local',
            password='AdminPassword123!',
            role=RoleChoices.ADMIN
        )

        self.normal_user = User.objects.create_user(
            username='customer_lead@housing.local',
            email='customer_lead@housing.local',
            password='CustomerPassword123!',
            role=RoleChoices.CUSTOMER
        )

    # 1. Submit callback form with valid information
    def test_01_submit_valid_callback_form(self):
        response = self.client.post(reverse('services:bank-loans'), {
            'full_name': 'Rahul Sharma',
            'mobile_number': '9876543210',
            'email_address': 'rahul@example.com',
            'employment_type': EmploymentTypeChoices.SALARIED,
            'net_monthly_income': '85000',
            'desired_loan_amount': '5000000',
            'preferred_bank': self.bank.id
        })
        self.assertRedirects(response, reverse('services:bank-loans'))

        self.assertTrue(LoanInquiryLead.objects.filter(email_address='rahul@example.com').exists())
        lead = LoanInquiryLead.objects.get(email_address='rahul@example.com')
        self.assertTrue(lead.lead_id.startswith('LL-'))
        self.assertEqual(lead.full_name, 'Rahul Sharma')
        self.assertEqual(float(lead.desired_loan_amount), 5000000.0)
        self.assertEqual(lead.status, LoanInquiryStatusChoices.NEW)

    # 2. Submit another enquiry creates separate unique lead ID
    def test_02_submit_second_enquiry_unique_lead_id(self):
        lead1 = LoanInquiryLead.objects.create(
            full_name='Applicant 1',
            mobile_number='9876543211',
            email_address='app1@example.com',
            net_monthly_income=60000,
            desired_loan_amount=3000000
        )
        lead2 = LoanInquiryLead.objects.create(
            full_name='Applicant 2',
            mobile_number='9876543212',
            email_address='app2@example.com',
            net_monthly_income=70000,
            desired_loan_amount=4000000
        )
        self.assertNotEqual(lead1.lead_id, lead2.lead_id)

    # 3. Open Admin Portal -> Loan Inquiry Leads
    def test_03_admin_portal_loan_inquiries_list(self):
        lead = LoanInquiryLead.objects.create(
            full_name='Priya Patel',
            mobile_number='9876543213',
            email_address='priya@example.com',
            net_monthly_income=90000,
            desired_loan_amount=6000000
        )

        self.client.login(username='admin_lead@housing.local', password='AdminPassword123!')
        response = self.client.get(reverse('services:admin-loan-inquiries'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Priya Patel')
        self.assertContains(response, lead.lead_id)

    # 4. Open individual lead -> every field visible
    def test_04_individual_lead_details_visibility(self):
        lead = LoanInquiryLead.objects.create(
            full_name='Vikram Malhotra',
            mobile_number='9876543214',
            email_address='vikram@example.com',
            employment_type=EmploymentTypeChoices.BUSINESS,
            net_monthly_income=120000,
            desired_loan_amount=7500000,
            preferred_bank=self.bank
        )

        self.client.login(username='admin_lead@housing.local', password='AdminPassword123!')
        response = self.client.get(reverse('services:admin-loan-inquiry-detail', kwargs={'lead_id': lead.id}))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Vikram Malhotra')
        self.assertContains(response, 'vikram@example.com')
        self.assertContains(response, '7500000')
        self.assertContains(response, 'Test HDFC Bank')

    # 5. Change lead status records audit trail
    def test_05_status_change_and_history_audit(self):
        lead = LoanInquiryLead.objects.create(
            full_name='Anita Desai',
            mobile_number='9876543215',
            email_address='anita@example.com',
            net_monthly_income=50000,
            desired_loan_amount=2500000
        )

        self.client.login(username='admin_lead@housing.local', password='AdminPassword123!')
        response = self.client.post(reverse('services:admin-loan-inquiry-detail', kwargs={'lead_id': lead.id}), {
            'action': 'update_lead',
            'status': LoanInquiryStatusChoices.UNDER_BANK_EVALUATION
        })
        self.assertRedirects(response, reverse('services:admin-loan-inquiry-detail', kwargs={'lead_id': lead.id}))

        lead.refresh_from_db()
        self.assertEqual(lead.status, LoanInquiryStatusChoices.UNDER_BANK_EVALUATION)
        self.assertTrue(LoanInquiryStatusHistory.objects.filter(lead=lead, new_status=LoanInquiryStatusChoices.UNDER_BANK_EVALUATION).exists())

    # 6. Add admin note
    def test_06_add_internal_admin_note(self):
        lead = LoanInquiryLead.objects.create(
            full_name='Suresh Kumar',
            mobile_number='9876543216',
            email_address='suresh@example.com',
            net_monthly_income=70000,
            desired_loan_amount=4000000
        )

        self.client.login(username='admin_lead@housing.local', password='AdminPassword123!')
        response = self.client.post(reverse('services:admin-loan-inquiry-detail', kwargs={'lead_id': lead.id}), {
            'action': 'add_note',
            'note_text': 'Called applicant. Requested salary slips and ITR.'
        })
        self.assertRedirects(response, reverse('services:admin-loan-inquiry-detail', kwargs={'lead_id': lead.id}))
        self.assertTrue(LoanInquiryNote.objects.filter(lead=lead, note_text__contains='salary slips').exists())

    # 7. Unauthenticated admin API access denied
    def test_07_unauthenticated_api_access_denied(self):
        response = self.client.get(reverse('services:api-admin-loan-inquiries-list'))
        self.assertNotEqual(response.status_code, 200)

    # 8. Submit invalid information -> rejected
    def test_08_submit_invalid_information_rejected(self):
        response = self.client.post(reverse('services:bank-loans'), {
            'full_name': '',  # Invalid empty name
            'email_address': 'invalid-email',
            'net_monthly_income': 'abc'
        })
        self.assertEqual(response.status_code, 200) # Form re-renders with error
        self.assertFalse(LoanInquiryLead.objects.filter(email_address='invalid-email').exists())

    # 9. Test duplicate submission prevention
    def test_09_duplicate_submission_prevention(self):
        # First submission
        self.client.post(reverse('services:bank-loans'), {
            'full_name': 'Dup Check',
            'mobile_number': '9998887770',
            'email_address': 'dup@example.com',
            'employment_type': EmploymentTypeChoices.SALARIED,
            'net_monthly_income': '50000',
            'desired_loan_amount': '3000000'
        })

        # Second submission immediately
        self.client.post(reverse('services:bank-loans'), {
            'full_name': 'Dup Check',
            'mobile_number': '9998887770',
            'email_address': 'dup@example.com',
            'employment_type': EmploymentTypeChoices.SALARIED,
            'net_monthly_income': '50000',
            'desired_loan_amount': '3000000'
        })

        count = LoanInquiryLead.objects.filter(email_address='dup@example.com').count()
        self.assertEqual(count, 1)
