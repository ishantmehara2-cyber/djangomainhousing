from django.test import TestCase, Client
from django.urls import reverse

class PartnerMarketplaceTest(TestCase):
    def setUp(self):
        self.client = Client()

    def test_partner_marketplace_public_access(self):
        """Test that Partner Marketplace is publicly accessible and displays correct title."""
        response = self.client.get('/brokers/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Partner Marketplace')
