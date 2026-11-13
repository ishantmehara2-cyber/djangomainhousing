import os
import io
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.conf import settings

from apps.accounts.models import RoleChoices, PartnerApprovalStatusChoices, PartnerDocumentTypeChoices, PartnerDocument
from apps.accounts.permissions import can_post_property
from apps.locations.models import State, District, City, Locality
from apps.properties.models import Property, PropertyType, PropertyMedia, ListingPurposeChoices, ListingStateChoices
from apps.services.models import BankPartner, BankCategoryChoices, ProcessingFeeTypeChoices
from apps.core.validators import MAX_UPLOAD_SIZE_BYTES, validate_file_size_5mb

import django.test.client
django.test.client.store_rendered_templates = lambda *args, **kwargs: None

User = get_user_model()


class HousingModulesTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.state, _ = State.objects.get_or_create(code='MH', defaults={'name': 'Maharashtra'})
        self.district, _ = District.objects.get_or_create(state=self.state, name='Mumbai Suburban')
        self.city, _ = City.objects.get_or_create(state=self.state, district=self.district, name='Mumbai', defaults={'slug': 'mumbai'})
        self.locality, _ = Locality.objects.get_or_create(city=self.city, name='Andheri West', defaults={'slug': 'andheri-west'})
        self.prop_type, _ = PropertyType.objects.get_or_create(name='Apartment', defaults={'slug': 'apartment'})

        # Admin user
        self.admin_user = User.objects.create_superuser(
            username='admin@housing.local',
            email='admin@housing.local',
            password='AdminPassword123!',
            role=RoleChoices.ADMIN
        )

        # Customer user
        self.customer_user = User.objects.create_user(
            username='customer@housing.local',
            email='customer@housing.local',
            password='CustomerPassword123!',
            role=RoleChoices.CUSTOMER,
            first_name='Customer',
            last_name='User'
        )

        # Partner user (Pending)
        self.pending_partner = User.objects.create_user(
            username='pending_partner@housing.local',
            email='pending_partner@housing.local',
            password='PartnerPassword123!',
            role=RoleChoices.PARTNER,
            first_name='Pending',
            last_name='Partner',
            agency_name='Apex Realty',
            business_address='123 Commercial Street',
            business_state='Maharashtra',
            business_city='Mumbai',
            business_pincode='400050',
            partner_approval_status=PartnerApprovalStatusChoices.PENDING,
            declaration_accepted=True
        )

        # Partner user (Approved)
        self.approved_partner = User.objects.create_user(
            username='approved_partner@housing.local',
            email='approved_partner@housing.local',
            password='PartnerPassword123!',
            role=RoleChoices.PARTNER,
            first_name='Approved',
            last_name='Partner',
            agency_name='Prime Estate',
            business_address='456 Business Hub',
            business_state='Maharashtra',
            business_city='Mumbai',
            business_pincode='400051',
            partner_approval_status=PartnerApprovalStatusChoices.APPROVED,
            declaration_accepted=True
        )

        # Partner user (Rejected)
        self.rejected_partner = User.objects.create_user(
            username='rejected_partner@housing.local',
            email='rejected_partner@housing.local',
            password='PartnerPassword123!',
            role=RoleChoices.PARTNER,
            first_name='Rejected',
            last_name='Partner',
            partner_approval_status=PartnerApprovalStatusChoices.REJECTED,
            partner_rejection_reason='Incomplete document verification'
        )

    # ==========================================================================
    # REGISTRATION & PERMISSION TESTS (Scenarios 1 - 7)
    # ==========================================================================

    def test_01_customer_cannot_post_properties(self):
        can_post, msg = can_post_property(self.customer_user)
        self.assertFalse(can_post)
        self.assertIn("Customer accounts are not permitted to post properties", msg)

        self.client.login(username='customer@housing.local', password='CustomerPassword123!')
        res = self.client.get(reverse('properties:post-property'))
        self.assertEqual(res.status_code, 302)
        self.assertIn(reverse('accounts:dashboard'), res.url)

    def test_02_partner_registration_without_document_rejected(self):
        res = self.client.post(reverse('accounts:register'), {
            'first_name': 'New',
            'last_name': 'Partner',
            'email': 'newpartner1@example.com',
            'phone': '9988776655',
            'role': RoleChoices.PARTNER,
            'password': 'Password123!',
            'confirm_password': 'Password123!',
            'agency_name': 'New Agency',
            'business_address': '789 Trade Tower',
            'business_state': 'Maharashtra',
            'business_city': 'Mumbai',
            'business_pincode': '400052',
            'declaration_accepted': 'on'
        })
        self.assertEqual(res.status_code, 200) # Form re-renders with error
        self.assertFalse(User.objects.filter(email='newpartner1@example.com').exists())

    def test_03_partner_registration_with_udyam_certificate_success(self):
        udyam_doc = SimpleUploadedFile("udyam_cert.pdf", b"%PDF-1.4 test certificate content", content_type="application/pdf")
        res = self.client.post(reverse('accounts:register'), {
            'first_name': 'New',
            'last_name': 'Partner',
            'email': 'newpartner2@example.com',
            'phone': '9988776654',
            'role': RoleChoices.PARTNER,
            'password': 'Password123!',
            'confirm_password': 'Password123!',
            'agency_name': 'New Agency',
            'business_address': '789 Trade Tower',
            'business_state': 'Maharashtra',
            'business_city': 'Mumbai',
            'business_pincode': '400052',
            'declaration_accepted': 'on',
            'doc_category_1': 'UDYAM',
            'doc_file_1': udyam_doc
        })
        self.assertRedirects(res, reverse('accounts:verify_otp'))

        # Verify OTP
        from apps.services.models import EmailOTP, OTPPurposeChoices
        otp_obj, otp_code = EmailOTP.generate_otp('newpartner2@example.com', purpose=OTPPurposeChoices.REGISTER, bypass_cooldown=True)
        verify_res = self.client.post(reverse('accounts:verify_otp'), {'otp': otp_code})
        self.assertEqual(verify_res.status_code, 302)
        follow_res = self.client.get(verify_res.url, follow=True)
        self.assertEqual(follow_res.status_code, 200)

    def test_04_partner_registration_without_declaration_rejected(self):
        udyam_doc = SimpleUploadedFile("udyam_cert.pdf", b"%PDF-1.4 test certificate content", content_type="application/pdf")
        res = self.client.post(reverse('accounts:register'), {
            'first_name': 'New',
            'last_name': 'Partner',
            'email': 'nodecl@example.com',
            'phone': '9988776653',
            'role': RoleChoices.PARTNER,
            'password': 'Password123!',
            'confirm_password': 'Password123!',
            'agency_name': 'Agency No Decl',
            'business_address': '101 Street',
            'business_state': 'Maharashtra',
            'business_city': 'Mumbai',
            'business_pincode': '400052',
            'doc_file_1': udyam_doc
            # declaration_accepted omitted
        })
        self.assertEqual(res.status_code, 200)
        self.assertFalse(User.objects.filter(email='nodecl@example.com').exists())

    def test_05_pending_partner_cannot_post_properties(self):
        can_post, msg = can_post_property(self.pending_partner)
        self.assertFalse(can_post)
        self.assertIn("pending admin verification", msg)

        self.client.login(username='pending_partner@housing.local', password='PartnerPassword123!')
        res = self.client.get(reverse('properties:post-property'))
        self.assertEqual(res.status_code, 302)
        self.assertIn(reverse('accounts:dashboard'), res.url)

    def test_06_admin_approves_partner_enables_posting(self):
        self.client.login(username='admin@housing.local', password='AdminPassword123!')
        res = self.client.post(reverse('accounts:admin_partner_detail', kwargs={'user_id': self.pending_partner.id}), {
            'action': 'approve',
            'status': PartnerApprovalStatusChoices.APPROVED
        })
        self.pending_partner.refresh_from_db()
        self.assertEqual(self.pending_partner.partner_approval_status, PartnerApprovalStatusChoices.APPROVED)

        can_post, _ = can_post_property(self.pending_partner)
        self.assertTrue(can_post)

    def test_07_rejected_partner_cannot_post_properties(self):
        can_post, msg = can_post_property(self.rejected_partner)
        self.assertFalse(can_post)
        self.assertIn("rejected", msg)

        self.client.login(username='rejected_partner@housing.local', password='PartnerPassword123!')
        res = self.client.get(reverse('properties:post-property'))
        self.assertEqual(res.status_code, 302)
        self.assertIn(reverse('accounts:dashboard'), res.url)

    # ==========================================================================
    # PROPERTY THUMBNAIL TESTS (Scenarios 8 - 14)
    # ==========================================================================

    def test_08_to_12_property_thumbnail_upload_selection_and_public_display(self):
        self.client.login(username='approved_partner@housing.local', password='PartnerPassword123!')

        prop = Property.objects.create(
            title='Sample Villa for Cover Test',
            slug='sample-villa-cover-test',
            description='Gorgeous villa in Mumbai',
            listing_purpose=ListingPurposeChoices.BUY,
            property_type=self.prop_type,
            owner=self.approved_partner,
            posted_by_user=self.approved_partner,
            price=25000000.0,
            carpet_area=2000.0,
            city=self.city,
            locality=self.locality,
            address='Villa Road 1',
            listing_state=ListingStateChoices.ACTIVE
        )

        img1 = PropertyMedia.objects.create(property=prop, file=SimpleUploadedFile("img1.jpg", b"fakejpg1"), display_order=0)
        img2 = PropertyMedia.objects.create(property=prop, file=SimpleUploadedFile("img2.jpg", b"fakejpg2"), display_order=1)
        img3 = PropertyMedia.objects.create(property=prop, file=SimpleUploadedFile("img3.jpg", b"fakejpg3"), display_order=2)

        # Select img3 as main cover thumbnail
        prop.thumbnail_media = img3
        prop.save()

        # Public Card check: returns img3 URL
        self.assertEqual(prop.get_main_thumbnail_url, img3.file.url)
        self.assertNotEqual(prop.get_main_thumbnail_url, img1.file.url)

        # Change thumbnail to img2
        prop.thumbnail_media = img2
        prop.save()
        self.assertEqual(prop.get_main_thumbnail_url, img2.file.url)

    def test_13_delete_selected_thumbnail_reassigns_media(self):
        prop = Property.objects.create(
            title='Delete Thumbnail Test',
            slug='delete-thumbnail-test',
            description='Test property description',
            property_type=self.prop_type,
            owner=self.approved_partner,
            posted_by_user=self.approved_partner,
            carpet_area=1000.0,
            city=self.city,
            locality=self.locality,
            address='Street 5'
        )
        img1 = PropertyMedia.objects.create(property=prop, file=SimpleUploadedFile("pic1.jpg", b"pic1"), display_order=0)
        img2 = PropertyMedia.objects.create(property=prop, file=SimpleUploadedFile("pic2.jpg", b"pic2"), display_order=1)
        prop.thumbnail_media = img1
        prop.save()

        # Simulate deletion via edit view
        self.client.login(username='approved_partner@housing.local', password='PartnerPassword123!')
        res = self.client.post(reverse('properties:edit', kwargs={'slug': prop.slug}), {
            'delete_media_id': img1.id
        })
        prop.refresh_from_db()
        self.assertFalse(PropertyMedia.objects.filter(id=img1.id).exists())
        self.assertEqual(prop.thumbnail_media_id, img2.id)

    def test_14_cannot_set_other_property_media_as_thumbnail(self):
        propA = Property.objects.create(title='Prop A', slug='prop-a', property_type=self.prop_type, owner=self.approved_partner, posted_by_user=self.approved_partner, carpet_area=500, city=self.city, locality=self.locality)
        propB = Property.objects.create(title='Prop B', slug='prop-b', property_type=self.prop_type, owner=self.approved_partner, posted_by_user=self.approved_partner, carpet_area=500, city=self.city, locality=self.locality)

        imgB = PropertyMedia.objects.create(property=propB, file=SimpleUploadedFile("b.jpg", b"b"), display_order=0)

        # Attempt to set imgB as propA thumbnail via edit view
        self.client.login(username='approved_partner@housing.local', password='PartnerPassword123!')
        res = self.client.post(reverse('properties:edit', kwargs={'slug': propA.slug}), {
            'selected_thumbnail_id': imgB.id
        })
        propA.refresh_from_db()
        self.assertNotEqual(propA.thumbnail_media_id, imgB.id)

    # ==========================================================================
    # FILE SIZE RESTRICTION TESTS (Scenarios 15 - 21)
    # ==========================================================================

    def test_15_to_21_global_5mb_upload_restrictions(self):
        # 4 MB file (valid)
        valid_4mb = SimpleUploadedFile("photo_4mb.jpg", b"x" * (4 * 1024 * 1024), content_type="image/jpeg")
        self.assertEqual(validate_file_size_5mb(valid_4mb), valid_4mb)

        # 6 MB file (invalid)
        invalid_6mb = SimpleUploadedFile("photo_6mb.jpg", b"x" * (6 * 1024 * 1024), content_type="image/jpeg")
        from django.core.exceptions import ValidationError
        with self.assertRaises(ValidationError):
            validate_file_size_5mb(invalid_6mb)

    # ==========================================================================
    # BANK MANAGEMENT TESTS (Scenarios 22 - 26)
    # ==========================================================================

    def test_22_to_26_bank_management_crud_and_public_reflection(self):
        # 22. Admin adds a new bank
        self.client.login(username='admin@housing.local', password='AdminPassword123!')
        res_create = self.client.post(reverse('services:admin-add-bank'), {
            'name': 'Kotak Mahindra Bank',
            'slug': 'kotak-mahindra-bank',
            'category': BankCategoryChoices.PRIVATE_SECTOR,
            'min_interest_rate': '8.75',
            'max_interest_rate': '9.20',
            'max_tenure_years': 30,
            'processing_fee_info': '0.50% + GST',
            'processing_fee_type': ProcessingFeeTypeChoices.PERCENTAGE,
            'benefits_raw': 'Instant online approval\nSpecial NRI home loan schemes',
            'display_order': 5,
            'is_active': 'on'
        })
        self.assertRedirects(res_create, reverse('services:admin-bank-management'))
        self.assertTrue(BankPartner.objects.filter(slug='kotak-mahindra-bank').exists())

        # Public page reflects new bank
        public_res = self.client.get(reverse('services:bank-loans'))
        self.assertContains(public_res, 'Kotak Mahindra Bank')
        self.assertContains(public_res, '8.75%')

        # 23 & 24. Admin edits interest rate and processing fee
        kotak = BankPartner.objects.get(slug='kotak-mahindra-bank')
        edit_res = self.client.post(reverse('services:admin-edit-bank', kwargs={'pk': kotak.id}), {
            'name': 'Kotak Mahindra Bank',
            'slug': 'kotak-mahindra-bank',
            'category': BankCategoryChoices.PRIVATE_SECTOR,
            'min_interest_rate': '8.35',  # Updated rate
            'max_interest_rate': '9.00',
            'max_tenure_years': 30,
            'processing_fee_info': 'Nil processing fee offer',  # Updated fee
            'processing_fee_type': ProcessingFeeTypeChoices.CUSTOM,
            'display_order': 5,
            'is_active': 'on'
        })
        self.assertRedirects(edit_res, reverse('services:admin-bank-management'))

        public_res_updated = self.client.get(reverse('services:bank-loans'))
        self.assertContains(public_res_updated, 'From 8.35%')
        self.assertContains(public_res_updated, 'Nil processing fee offer')

        # 25. Admin deactivates bank: disappears publicly
        toggle_res = self.client.post(reverse('services:admin-toggle-bank-active', kwargs={'pk': kotak.id}))
        self.assertRedirects(toggle_res, reverse('services:admin-bank-management'))

        public_res_deactivated = self.client.get(reverse('services:bank-loans'))
        self.assertNotContains(public_res_deactivated, 'Kotak Mahindra Bank')

        # 26. Unauthorized user cannot access bank management APIs
        self.client.logout()
        unauth_api_res = self.client.get(reverse('services:api-admin-banks-list'))
        self.assertNotEqual(unauth_api_res.status_code, 200)
