import json
from decimal import Decimal
from django.test import TestCase, Client
from django.urls import reverse
from django.core.exceptions import ValidationError
from apps.accounts.models import User, RoleChoices
from apps.locations.models import State, District, City, Locality
from apps.properties.models import Property, PropertyType, PropertyCategoryChoices, ListingPurposeChoices, ListingStateChoices
from apps.core.models import SEOPage
from apps.core.seo_helpers import build_property_seo_context, format_price_for_seo

class SEOPageModelTestCase(TestCase):
    def test_seopage_creation_and_clean_validation(self):
        page = SEOPage.objects.create(
            page_name="Test Landing Page",
            page_url="test-landing", # Missing leading slash
            seo_title="Test Landing Page Title | THF",
            meta_description="This is a test landing page meta description for SEO testing.",
            structured_data_json=json.dumps({"@context": "https://schema.org", "@type": "WebPage"}),
            sitemap_priority=Decimal('0.7')
        )
        page.clean()
        self.assertEqual(page.page_url, "/test-landing")

    def test_invalid_json_ld_validation(self):
        page = SEOPage(
            page_name="Bad JSON Page",
            page_url="/bad-json/",
            seo_title="Title",
            meta_description="Desc",
            structured_data_json="{ invalid json format }"
        )
        with self.assertRaises(ValidationError):
            page.clean()

    def test_sitemap_priority_out_of_bounds(self):
        page = SEOPage(
            page_name="Priority Page",
            page_url="/priority/",
            seo_title="Title",
            meta_description="Desc",
            sitemap_priority=Decimal('1.5')
        )
        with self.assertRaises(ValidationError):
            page.clean()

class SEOTemplateAndViewsTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.state, _ = State.objects.get_or_create(state_code="MH", defaults={'name': "Maharashtra"})
        self.district, _ = District.objects.get_or_create(name="Thane", state=self.state)
        self.city, _ = City.objects.get_or_create(slug="thane", defaults={'name': "Thane", 'district': self.district, 'state': self.state})
        self.locality, _ = Locality.objects.get_or_create(slug="majiwada", defaults={'name': "Majiwada", 'city': self.city})

        self.owner = User.objects.create_user(
            username="seo_owner",
            email="seo_owner@example.com",
            password="Password123!",
            role=RoleChoices.OWNER
        )
        self.prop_type, _ = PropertyType.objects.get_or_create(slug="apartment", defaults={'name': "Apartment", 'category': PropertyCategoryChoices.RESIDENTIAL})

        self.active_property = Property.objects.create(
            title="Luxury 2 BHK Flat in Thane",
            slug="luxury-2-bhk-flat-in-thane",
            description="Spacious 2 BHK flat with modern amenities in Majiwada, Thane.",
            listing_purpose=ListingPurposeChoices.BUY,
            property_category=PropertyCategoryChoices.RESIDENTIAL,
            property_type=self.prop_type,
            owner=self.owner,
            posted_by_user=self.owner,
            price=Decimal('7500000.00'),
            bhk=2,
            carpet_area=Decimal('850.00'),
            built_up_area=Decimal('950.00'),
            address="101 Grand Tower, Majiwada",
            pincode="400601",
            city=self.city,
            locality=self.locality,
            listing_state=ListingStateChoices.ACTIVE
        )

        self.draft_property = Property.objects.create(
            title="Unpublished Draft Villa",
            slug="unpublished-draft-villa",
            description="Draft villa details.",
            listing_purpose=ListingPurposeChoices.BUY,
            property_category=PropertyCategoryChoices.RESIDENTIAL,
            property_type=self.prop_type,
            owner=self.owner,
            posted_by_user=self.owner,
            price=Decimal('15000000.00'),
            carpet_area=Decimal('2000.00'),
            address="Private Villa Area",
            city=self.city,
            locality=self.locality,
            listing_state=ListingStateChoices.DRAFT
        )

    def test_homepage_seo_head_tags_rendering(self):
        SEOPage.objects.update_or_create(
            page_url="/",
            defaults={
                "page_name": "Homepage",
                "seo_title": "The Home First | Buy, Rent & Explore Properties in India",
                "meta_description": "Explore residential and commercial properties with The Home First.",
                "canonical_url": "https://www.thehomefirst.com/"
            }
        )
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        content = response.content.decode('utf-8')

        self.assertIn('<title>The Home First | Buy, Rent &amp; Explore Properties in India</title>', content)
        self.assertIn('<meta name="description" content="Explore residential and commercial properties with The Home First.">', content)
        self.assertIn('<link rel="canonical" href="https://www.thehomefirst.com/">', content)
        self.assertIn('<meta name="robots" content="index, follow">', content)
        self.assertIn('<meta property="og:site_name" content="The Home First">', content)
        self.assertIn('<meta name="twitter:card" content="summary_large_image">', content)

    def test_private_dashboard_route_has_noindex_directive(self):
        response = self.client.get('/auth/login/')
        content = response.content.decode('utf-8')
        self.assertIn('<meta name="robots" content="noindex, nofollow">', content)

    def test_dynamic_property_seo_rendering(self):
        url = reverse('properties:detail', kwargs={'slug': self.active_property.slug})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        content = response.content.decode('utf-8')

        self.assertIn('2 BHK Apartment for Buy / Sale in Majiwada, Thane | The Home First', content)
        self.assertIn('Price: ₹75.00 Lakhs', content)
        self.assertIn('Built-up Area: 950 Sq. Ft.', content)
        self.assertIn(f'/property/{self.active_property.slug}/', content)
        self.assertIn('application/ld+json', content)
        self.assertIn('"@type": "Apartment"', content)

    def test_unpublished_property_excluded_from_indexing(self):
        url = reverse('properties:detail', kwargs={'slug': self.draft_property.slug})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_sitemap_xml_response_and_content(self):
        SEOPage.objects.create(
            page_name="Buy Properties",
            page_url="/properties/buy/",
            seo_title="Buy Title",
            meta_description="Buy Desc",
            is_in_sitemap=True,
            robots_index='index'
        )
        response = self.client.get('/sitemap.xml')
        self.assertEqual(response.status_code, 200)
        self.assertIn('application/xml', response['Content-Type'])
        content = response.content.decode('utf-8')

        self.assertIn('<?xml version="1.0" encoding="UTF-8"?>', content)
        self.assertIn('/properties/buy/', content)
        self.assertIn(f'/property/{self.active_property.slug}/', content)
        # Verify unpublished property is excluded
        self.assertNotIn(f'/property/{self.draft_property.slug}/', content)

    def test_robots_txt_response_and_content(self):
        response = self.client.get('/robots.txt')
        self.assertEqual(response.status_code, 200)
        self.assertIn('text/plain', response['Content-Type'])
        content = response.content.decode('utf-8')

        self.assertIn('User-agent: *', content)
        self.assertIn('Disallow: /admin/', content)
        self.assertIn('Disallow: /dashboard/', content)
        self.assertIn('Disallow: /auth/', content)
        self.assertIn('Sitemap:', content)
        self.assertIn('/sitemap.xml', content)

    def test_seo_price_formatter(self):
        self.assertEqual(format_price_for_seo(self.active_property), "₹75.00 Lakhs")
