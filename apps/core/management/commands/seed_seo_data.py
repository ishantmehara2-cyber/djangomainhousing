import json
from django.core.management.base import BaseCommand
from apps.core.models import SEOPage

class Command(BaseCommand):
    help = 'Seeds initial professional SEO records for public pages of The Home First including real estate agent & broker keywords'

    def handle(self, *args, **options):
        self.stdout.write("Seeding initial SEO records for The Home First (THF)...")

        site_url = "https://www.thehomefirst.com"
        default_logo = f"{site_url}/static/images/thf-og-banner.png"

        seo_records = [
            {
                "page_name": "Homepage",
                "page_url": "/",
                "url_slug": "homepage",
                "seo_title": "The Home First | Buy, Rent & Explore Properties in India",
                "meta_description": "Explore residential and commercial properties with The Home First (THF). Discover properties, real estate agents, property brokers, home loan options, and online rental agreement services.",
                "meta_keywords": "the home first, thf, buy property india, rent apartment india, commercial real estate, home loans, rental agreement, real estate agents india, property brokers india, property dealers india, local property agents, real estate consultants, property buying consultants, property brokers mumbai, property dealers thane, real estate agents navi mumbai, property agents near me",
                "canonical_url": f"{site_url}/",
                "robots_index": "index",
                "robots_follow": "follow",
                "og_title": "The Home First | Your Property. Your Possibilities.",
                "og_description": "Discover 100% verified residential properties, commercial spaces, plots, home loans, and rental agreements on The Home First.",
                "og_image_url": default_logo,
                "og_type": "website",
                "twitter_card_type": "summary_large_image",
                "twitter_title": "The Home First | Your Property. Your Possibilities.",
                "twitter_description": "Discover 100% verified residential properties, commercial spaces, plots, home loans, and rental agreements on The Home First.",
                "twitter_image_url": default_logo,
                "is_in_sitemap": True,
                "sitemap_priority": 1.0,
                "structured_data_json": json.dumps({
                    "@context": "https://schema.org",
                    "@graph": [
                        {
                            "@type": "Organization",
                            "@id": f"{site_url}/#organization",
                            "name": "The Home First",
                            "legalName": "AINexTech LLP",
                            "alternateName": "THF",
                            "url": site_url,
                            "logo": f"{site_url}/static/images/logo.png",
                            "slogan": "Your Property. Your Possibilities.",
                            "contactPoint": {
                                "@type": "ContactPoint",
                                "telephone": "+91-77382 30656",
                                "contactType": "customer service",
                                "email": "connectthehomefirst@gmail.com",
                                "availableLanguage": ["English", "Hindi"]
                            }
                        },
                        {
                            "@type": "WebSite",
                            "@id": f"{site_url}/#website",
                            "url": site_url,
                            "name": "The Home First",
                            "description": "Buy, Rent & Explore Verified Properties in India",
                            "publisher": {"@id": f"{site_url}/#organization"},
                            "potentialAction": {
                                "@type": "SearchAction",
                                "target": {
                                    "@type": "EntryPoint",
                                    "urlTemplate": f"{site_url}/search/?q={{search_term_string}}"
                                },
                                "query-input": "required name=search_term_string"
                            }
                        }
                    ]
                }, indent=2)
            },
            {
                "page_name": "Buy Properties",
                "page_url": "/properties/buy/",
                "url_slug": "properties-buy",
                "seo_title": "Buy Properties in India | The Home First",
                "meta_description": "Find residential flats, luxury apartments, independent villas, and plots for sale in top cities across India with verified partner listings on The Home First.",
                "meta_keywords": "buy flats india, buy apartments, residential property for sale, property buy thf, property buying consultants, residential real estate brokers, property dealers mumbai, property brokers thane",
                "canonical_url": f"{site_url}/properties/buy/",
                "robots_index": "index",
                "robots_follow": "follow",
                "og_title": "Buy Properties in India | The Home First",
                "og_description": "Explore thousands of verified residential flats, apartments, villas, and plots for sale across India.",
                "og_image_url": default_logo,
                "og_type": "website",
                "twitter_card_type": "summary_large_image",
                "twitter_title": "Buy Properties in India | The Home First",
                "twitter_description": "Explore thousands of verified residential flats, apartments, villas, and plots for sale across India.",
                "twitter_image_url": default_logo,
                "is_in_sitemap": True,
                "sitemap_priority": 0.9,
                "structured_data_json": json.dumps({
                    "@context": "https://schema.org",
                    "@type": "BreadcrumbList",
                    "itemListElement": [
                        {"@type": "ListItem", "position": 1, "name": "Home", "item": site_url},
                        {"@type": "ListItem", "position": 2, "name": "Buy Properties", "item": f"{site_url}/properties/buy/"}
                    ]
                }, indent=2)
            },
            {
                "page_name": "Rent Properties",
                "page_url": "/properties/rent/",
                "url_slug": "properties-rent",
                "seo_title": "Properties for Rent in India | The Home First",
                "meta_description": "Discover rental flats, fully furnished apartments, PG accommodations, and rental houses with zero brokerage options on The Home First.",
                "meta_keywords": "properties for rent, rental flats, rent apartment, zero brokerage rent thf, rental property brokers, residential property agents, local rental brokers",
                "canonical_url": f"{site_url}/properties/rent/",
                "robots_index": "index",
                "robots_follow": "follow",
                "og_title": "Properties for Rent in India | The Home First",
                "og_description": "Discover rental flats, fully furnished apartments, and houses for rent in top Indian cities.",
                "og_image_url": default_logo,
                "og_type": "website",
                "twitter_card_type": "summary_large_image",
                "twitter_title": "Properties for Rent in India | The Home First",
                "twitter_description": "Discover rental flats, fully furnished apartments, and houses for rent in top Indian cities.",
                "twitter_image_url": default_logo,
                "is_in_sitemap": True,
                "sitemap_priority": 0.9,
                "structured_data_json": json.dumps({
                    "@context": "https://schema.org",
                    "@type": "BreadcrumbList",
                    "itemListElement": [
                        {"@type": "ListItem", "position": 1, "name": "Home", "item": site_url},
                        {"@type": "ListItem", "position": 2, "name": "Rent Properties", "item": f"{site_url}/properties/rent/"}
                    ]
                }, indent=2)
            },
            {
                "page_name": "Commercial Properties",
                "page_url": "/properties/commercial/",
                "url_slug": "properties-commercial",
                "seo_title": "Commercial Properties for Sale and Rent | THF",
                "meta_description": "Browse commercial office spaces, retail shops, showrooms, and warehouses for sale or lease across India with verified partner listings on THF.",
                "meta_keywords": "commercial property sale, office space lease, commercial shops rent, thf commercial, commercial real estate brokers, commercial property consultants, commercial property agents",
                "canonical_url": f"{site_url}/properties/commercial/",
                "robots_index": "index",
                "robots_follow": "follow",
                "og_title": "Commercial Properties for Sale & Rent | THF",
                "og_description": "Browse commercial office spaces, retail shops, showrooms, and warehouses for sale or lease across India.",
                "og_image_url": default_logo,
                "og_type": "website",
                "twitter_card_type": "summary_large_image",
                "twitter_title": "Commercial Properties for Sale & Rent | THF",
                "twitter_description": "Browse commercial office spaces, retail shops, showrooms, and warehouses for sale or lease across India.",
                "twitter_image_url": default_logo,
                "is_in_sitemap": True,
                "sitemap_priority": 0.8,
                "structured_data_json": json.dumps({
                    "@context": "https://schema.org",
                    "@type": "BreadcrumbList",
                    "itemListElement": [
                        {"@type": "ListItem", "position": 1, "name": "Home", "item": site_url},
                        {"@type": "ListItem", "position": 2, "name": "Commercial Properties", "item": f"{site_url}/properties/commercial/"}
                    ]
                }, indent=2)
            },
            {
                "page_name": "Residential Properties",
                "page_url": "/properties/residential/",
                "url_slug": "properties-residential",
                "seo_title": "Residential Properties for Sale & Rent | The Home First",
                "meta_description": "Explore 100% verified residential apartments, builder floors, and luxury villas for sale and rent across major Indian cities on The Home First.",
                "meta_keywords": "residential properties, apartments for sale, residential flats rent, thf residential, residential real estate brokers, residential property agents, local property dealers",
                "canonical_url": f"{site_url}/properties/residential/",
                "robots_index": "index",
                "robots_follow": "follow",
                "og_title": "Residential Properties | The Home First",
                "og_description": "Explore verified residential apartments, builder floors, and luxury villas for sale and rent on The Home First.",
                "og_image_url": default_logo,
                "og_type": "website",
                "twitter_card_type": "summary_large_image",
                "twitter_title": "Residential Properties | The Home First",
                "twitter_description": "Explore verified residential apartments, builder floors, and luxury villas for sale and rent on The Home First.",
                "twitter_image_url": default_logo,
                "is_in_sitemap": True,
                "sitemap_priority": 0.8,
                "structured_data_json": json.dumps({
                    "@context": "https://schema.org",
                    "@type": "BreadcrumbList",
                    "itemListElement": [
                        {"@type": "ListItem", "position": 1, "name": "Home", "item": site_url},
                        {"@type": "ListItem", "position": 2, "name": "Residential Properties", "item": f"{site_url}/properties/residential/"}
                    ]
                }, indent=2)
            },
            {
                "page_name": "Home Loans",
                "page_url": "/bank-loans/",
                "url_slug": "home-loans",
                "seo_title": "Home Loan Enquiry and Banking Partners | THF",
                "meta_description": "Apply for home loans with leading banking partners. Check competitive interest rates, calculate EMI, and check eligibility through The Home First.",
                "meta_keywords": "home loan enquiry, bank loan partner, home loan EMI calculator, real estate loan thf",
                "canonical_url": f"{site_url}/bank-loans/",
                "robots_index": "index",
                "robots_follow": "follow",
                "og_title": "Home Loans & Banking Partners | THF",
                "og_description": "Apply for home loans with top banking partners through The Home First. Fast approval assistance and low interest rates.",
                "og_image_url": default_logo,
                "og_type": "website",
                "twitter_card_type": "summary_large_image",
                "twitter_title": "Home Loans & Banking Partners | THF",
                "twitter_description": "Apply for home loans with top banking partners through The Home First. Fast approval assistance and low interest rates.",
                "twitter_image_url": default_logo,
                "is_in_sitemap": True,
                "sitemap_priority": 0.8,
                "structured_data_json": json.dumps({
                    "@context": "https://schema.org",
                    "@type": "FinancialProduct",
                    "name": "Home Loans Assistance - The Home First",
                    "provider": {"@type": "Organization", "name": "The Home First", "legalName": "AINexTech LLP"},
                    "description": "Comprehensive home loan assistance and banking partner integration for homebuyers in India."
                }, indent=2)
            },
            {
                "page_name": "Home Loan Calculator",
                "page_url": "/home-loan-calculator/",
                "url_slug": "home-loan-calculator",
                "seo_title": "Home Loan EMI & Eligibility Calculator | The Home First",
                "meta_description": "Calculate your home loan EMI, total interest payable, and loan eligibility instantly with The Home First online loan calculator.",
                "meta_keywords": "home loan calculator, EMI calculator, property loan calculator thf",
                "canonical_url": f"{site_url}/home-loan-calculator/",
                "robots_index": "index",
                "robots_follow": "follow",
                "og_title": "Home Loan EMI & Eligibility Calculator | The Home First",
                "og_description": "Calculate your home loan EMI, interest rates, and loan repayment schedule instantly.",
                "og_image_url": default_logo,
                "og_type": "website",
                "twitter_card_type": "summary_large_image",
                "twitter_title": "Home Loan EMI & Eligibility Calculator | The Home First",
                "twitter_description": "Calculate your home loan EMI, interest rates, and loan repayment schedule instantly.",
                "twitter_image_url": default_logo,
                "is_in_sitemap": True,
                "sitemap_priority": 0.7,
                "structured_data_json": json.dumps({
                    "@context": "https://schema.org",
                    "@type": "WebApplication",
                    "name": "Home Loan EMI Calculator - The Home First",
                    "url": f"{site_url}/home-loan-calculator/",
                    "applicationCategory": "FinanceApplication",
                    "operatingSystem": "All"
                }, indent=2)
            },
            {
                "page_name": "Rental Agreement",
                "page_url": "/rental-agreement/",
                "url_slug": "rental-agreement",
                "seo_title": "Rental Agreement Services | The Home First",
                "meta_description": "Create legally binding online rental agreements with digital e-stamping and doorstep execution assistance through The Home First.",
                "meta_keywords": "rental agreement online, e-stamping rental agreement, tenant agreement service thf",
                "canonical_url": f"{site_url}/rental-agreement/",
                "robots_index": "index",
                "robots_follow": "follow",
                "og_title": "Online Rental Agreement Services | The Home First",
                "og_description": "Create legally compliant online rental agreements with digital e-stamping and doorstep delivery.",
                "og_image_url": default_logo,
                "og_type": "website",
                "twitter_card_type": "summary_large_image",
                "twitter_title": "Online Rental Agreement Services | The Home First",
                "twitter_description": "Create legally compliant online rental agreements with digital e-stamping and doorstep delivery.",
                "twitter_image_url": default_logo,
                "is_in_sitemap": True,
                "sitemap_priority": 0.8,
                "structured_data_json": json.dumps({
                    "@context": "https://schema.org",
                    "@type": "Service",
                    "name": "Online Rental Agreement Assistance",
                    "provider": {"@type": "Organization", "name": "The Home First", "legalName": "AINexTech LLP"},
                    "description": "Legally compliant e-stamped rental agreement execution and verification services."
                }, indent=2)
            },
            {
                "page_name": "Partner Registration",
                "page_url": "/auth/register/",
                "url_slug": "partner-registration",
                "seo_title": "Register as a Real Estate Partner | THF",
                "meta_description": "Join The Home First as a verified real estate partner, property agent, or developer. Manage listings, access buyer leads, and scale your property business.",
                "meta_keywords": "real estate partner registration, property agent registration, become a real estate partner, register as property agent, real estate partner network, property listing agents, list property online, post property online",
                "canonical_url": f"{site_url}/auth/register/",
                "robots_index": "index",
                "robots_follow": "follow",
                "og_title": "Register as a Real Estate Partner | THF",
                "og_description": "Partner with The Home First to publish verified listings and connect with active buyers and tenants.",
                "og_image_url": default_logo,
                "og_type": "website",
                "twitter_card_type": "summary_large_image",
                "twitter_title": "Register as a Real Estate Partner | THF",
                "twitter_description": "Partner with The Home First to publish verified listings and connect with active buyers and tenants.",
                "twitter_image_url": default_logo,
                "is_in_sitemap": True,
                "sitemap_priority": 0.7,
            },
            {
                "page_name": "Partners & Agents",
                "page_url": "/brokers/",
                "url_slug": "brokers-list",
                "seo_title": "Verified Real Estate Partners & Brokers | The Home First",
                "meta_description": "Connect with verified real estate partners, property consultants, and top brokers across India on The Home First.",
                "meta_keywords": "real estate brokers, verified property agents, real estate consultants, property brokers india, real estate brokers india, property dealers india, property broker near me, local property agents, property brokers mumbai, property dealers thane, real estate agents navi mumbai, property brokerage services",
                "canonical_url": f"{site_url}/brokers/",
                "robots_index": "index",
                "robots_follow": "follow",
                "og_title": "Verified Real Estate Partners & Brokers | The Home First",
                "og_description": "Connect with verified real estate partners and professional agents on The Home First.",
                "og_image_url": default_logo,
                "og_type": "website",
                "twitter_card_type": "summary_large_image",
                "twitter_title": "Verified Real Estate Partners & Brokers | The Home First",
                "twitter_description": "Connect with verified real estate partners and professional agents on The Home First.",
                "twitter_image_url": default_logo,
                "is_in_sitemap": True,
                "sitemap_priority": 0.7,
                "structured_data_json": json.dumps({
                    "@context": "https://schema.org",
                    "@type": "BreadcrumbList",
                    "itemListElement": [
                        {"@type": "ListItem", "position": 1, "name": "Home", "item": site_url},
                        {"@type": "ListItem", "position": 2, "name": "Real Estate Partners", "item": f"{site_url}/brokers/"}
                    ]
                }, indent=2)
            },
            {
                "page_name": "About Us",
                "page_url": "/about/",
                "url_slug": "about-us",
                "seo_title": "About The Home First | Our Mission and Services",
                "meta_description": "Learn about The Home First (THF), India's modern real estate platform operated by AINexTech LLP connecting buyers, tenants, owners, and verified partners.",
                "meta_keywords": "about the home first, thf mission, real estate platform india, ainextech llp, real estate agents india, property consultants india, real estate partner network",
                "canonical_url": f"{site_url}/about/",
                "robots_index": "index",
                "robots_follow": "follow",
                "og_title": "About The Home First | Our Mission and Services",
                "og_description": "Learn about The Home First (THF) — Your Property. Your Possibilities.",
                "og_image_url": default_logo,
                "og_type": "website",
                "twitter_card_type": "summary_large_image",
                "twitter_title": "About The Home First | Our Mission and Services",
                "twitter_description": "Learn about The Home First (THF) — Your Property. Your Possibilities.",
                "twitter_image_url": default_logo,
                "is_in_sitemap": True,
                "sitemap_priority": 0.6,
                "structured_data_json": json.dumps({
                    "@context": "https://schema.org",
                    "@type": "AboutPage",
                    "name": "About The Home First",
                    "url": f"{site_url}/about/",
                    "publisher": {
                        "@type": "Organization",
                        "name": "The Home First",
                        "legalName": "AINexTech LLP",
                        "url": site_url
                    }
                }, indent=2)
            },
            {
                "page_name": "Contact Us",
                "page_url": "/contact/",
                "url_slug": "contact-us",
                "seo_title": "Contact The Home First | Property Enquiries",
                "meta_description": "Get in touch with The Home First support team for property listings, home loan enquiries, partnership opportunities, and customer care.",
                "meta_keywords": "contact the home first, thf support, property enquiry contact, real estate agent contact, property broker inquiry",
                "canonical_url": f"{site_url}/contact/",
                "robots_index": "index",
                "robots_follow": "follow",
                "og_title": "Contact The Home First | Property Enquiries",
                "og_description": "Contact The Home First support team for assistance with property listings, home loans, and enquiries.",
                "og_image_url": default_logo,
                "og_type": "website",
                "twitter_card_type": "summary_large_image",
                "twitter_title": "Contact The Home First | Property Enquiries",
                "twitter_description": "Contact The Home First support team for assistance with property listings, home loans, and enquiries.",
                "twitter_image_url": default_logo,
                "is_in_sitemap": True,
                "sitemap_priority": 0.6,
                "structured_data_json": json.dumps({
                    "@context": "https://schema.org",
                    "@type": "ContactPage",
                    "name": "Contact The Home First",
                    "url": f"{site_url}/contact/",
                    "mainEntity": {
                        "@type": "Organization",
                        "name": "The Home First",
                        "legalName": "AINexTech LLP",
                        "telephone": "+91-77382 30656",
                        "email": "connectthehomefirst@gmail.com",
                        "address": {
                            "@type": "PostalAddress",
                            "streetAddress": "Shop 10, Bhoomi Acres, Phase 2, Waghbil Road, Hiranandani Estate",
                            "addressLocality": "Thane West",
                            "addressRegion": "Maharashtra",
                            "postalCode": "400615",
                            "addressCountry": "IN"
                        }
                    }
                }, indent=2)
            },
            {
                "page_name": "Privacy Policy",
                "page_url": "/privacy/",
                "url_slug": "privacy-policy",
                "seo_title": "Privacy Policy | The Home First",
                "meta_description": "Read The Home First Privacy Policy to understand how we collect, protect, and process user information, listing data, and personal details.",
                "meta_keywords": "privacy policy, data privacy, thf privacy policy",
                "canonical_url": f"{site_url}/privacy/",
                "robots_index": "index",
                "robots_follow": "follow",
                "og_title": "Privacy Policy | The Home First",
                "og_description": "Read the official Privacy Policy for The Home First.",
                "og_image_url": default_logo,
                "og_type": "website",
                "twitter_card_type": "summary_large_image",
                "twitter_title": "Privacy Policy | The Home First",
                "twitter_description": "Read the official Privacy Policy for The Home First.",
                "twitter_image_url": default_logo,
                "is_in_sitemap": True,
                "sitemap_priority": 0.4,
                "structured_data_json": json.dumps({
                    "@context": "https://schema.org",
                    "@type": "WebPage",
                    "name": "Privacy Policy - The Home First",
                    "url": f"{site_url}/privacy/"
                }, indent=2)
            },
            {
                "page_name": "Terms and Conditions",
                "page_url": "/terms/",
                "url_slug": "terms-and-conditions",
                "seo_title": "Terms and Conditions | The Home First",
                "meta_description": "Read the Terms and Conditions governing the use of The Home First website, property portal services, and user accounts.",
                "meta_keywords": "terms and conditions, user agreement, thf terms",
                "canonical_url": f"{site_url}/terms/",
                "robots_index": "index",
                "robots_follow": "follow",
                "og_title": "Terms and Conditions | The Home First",
                "og_description": "Read the official Terms and Conditions for The Home First.",
                "og_image_url": default_logo,
                "og_type": "website",
                "twitter_card_type": "summary_large_image",
                "twitter_title": "Terms and Conditions | The Home First",
                "twitter_description": "Read the official Terms and Conditions for The Home First.",
                "twitter_image_url": default_logo,
                "is_in_sitemap": True,
                "sitemap_priority": 0.4,
                "structured_data_json": json.dumps({
                    "@context": "https://schema.org",
                    "@type": "WebPage",
                    "name": "Terms and Conditions - The Home First",
                    "url": f"{site_url}/terms/"
                }, indent=2)
            },
            {
                "page_name": "Refund Policy",
                "page_url": "/refund-policy/",
                "url_slug": "refund-policy",
                "seo_title": "Refund Policy | The Home First",
                "meta_description": "Understand the refund policies and terms for paid property promotions and subscription packages on The Home First.",
                "meta_keywords": "refund policy, property promotion refund, thf refund terms",
                "canonical_url": f"{site_url}/refund-policy/",
                "robots_index": "index",
                "robots_follow": "follow",
                "og_title": "Refund Policy | The Home First",
                "og_description": "Read the official Refund Policy for property packages on The Home First.",
                "og_image_url": default_logo,
                "og_type": "website",
                "twitter_card_type": "summary_large_image",
                "twitter_title": "Refund Policy | The Home First",
                "twitter_description": "Read the official Refund Policy for property packages on The Home First.",
                "twitter_image_url": default_logo,
                "is_in_sitemap": True,
                "sitemap_priority": 0.4,
                "structured_data_json": json.dumps({
                    "@context": "https://schema.org",
                    "@type": "WebPage",
                    "name": "Refund Policy - The Home First",
                    "url": f"{site_url}/refund-policy/"
                }, indent=2)
            },
            {
                "page_name": "Return Policy",
                "page_url": "/return-policy/",
                "url_slug": "return-policy",
                "seo_title": "Return Policy | The Home First",
                "meta_description": "Read the Return Policy regarding property listings, digital enquiries, and documentation services on The Home First.",
                "meta_keywords": "return policy, digital service return, thf return policy",
                "canonical_url": f"{site_url}/return-policy/",
                "robots_index": "index",
                "robots_follow": "follow",
                "og_title": "Return Policy | The Home First",
                "og_description": "Read the official Return Policy for digital services on The Home First.",
                "og_image_url": default_logo,
                "og_type": "website",
                "twitter_card_type": "summary_large_image",
                "twitter_title": "Return Policy | The Home First",
                "twitter_description": "Read the official Return Policy for digital services on The Home First.",
                "twitter_image_url": default_logo,
                "is_in_sitemap": True,
                "sitemap_priority": 0.4,
                "structured_data_json": json.dumps({
                    "@context": "https://schema.org",
                    "@type": "WebPage",
                    "name": "Return Policy - The Home First",
                    "url": f"{site_url}/return-policy/"
                }, indent=2)
            },
            {
                "page_name": "Cancellation Policy",
                "page_url": "/cancellation-policy/",
                "url_slug": "cancellation-policy",
                "seo_title": "Cancellation Policy | The Home First",
                "meta_description": "Review the Cancellation Policy for property enquiries, rental agreement assistance, and promotional services on The Home First.",
                "meta_keywords": "cancellation policy, service cancellation, thf cancellation policy",
                "canonical_url": f"{site_url}/cancellation-policy/",
                "robots_index": "index",
                "robots_follow": "follow",
                "og_title": "Cancellation Policy | The Home First",
                "og_description": "Review the official Cancellation Policy for services on The Home First.",
                "og_image_url": default_logo,
                "og_type": "website",
                "twitter_card_type": "summary_large_image",
                "twitter_title": "Cancellation Policy | The Home First",
                "twitter_description": "Review the official Cancellation Policy for services on The Home First.",
                "twitter_image_url": default_logo,
                "is_in_sitemap": True,
                "sitemap_priority": 0.4,
                "structured_data_json": json.dumps({
                    "@context": "https://schema.org",
                    "@type": "WebPage",
                    "name": "Cancellation Policy - The Home First",
                    "url": f"{site_url}/cancellation-policy/"
                }, indent=2)
            },
            {
                "page_name": "Grievance Redressal",
                "page_url": "/grievance/",
                "url_slug": "grievance",
                "seo_title": "Grievance & Complaint Contact | The Home First",
                "meta_description": "Contact our Grievance Redressal Desk for issues regarding property listings, platform conduct, or user complaints on The Home First.",
                "meta_keywords": "grievance officer, complaint redressal, thf grievance",
                "canonical_url": f"{site_url}/grievance/",
                "robots_index": "index",
                "robots_follow": "follow",
                "og_title": "Grievance & Complaint Contact | The Home First",
                "og_description": "Contact our Grievance Redressal Desk for issues regarding property listings or platform conduct.",
                "og_image_url": default_logo,
                "og_type": "website",
                "twitter_card_type": "summary_large_image",
                "twitter_title": "Grievance & Complaint Contact | The Home First",
                "twitter_description": "Contact our Grievance Redressal Desk for issues regarding property listings or platform conduct.",
                "twitter_image_url": default_logo,
                "is_in_sitemap": True,
                "sitemap_priority": 0.4,
                "structured_data_json": json.dumps({
                    "@context": "https://schema.org",
                    "@type": "ContactPage",
                    "name": "Grievance Redressal Desk - The Home First",
                    "url": f"{site_url}/grievance/"
                }, indent=2)
            },
            {
                "page_name": "Legal Disclaimer",
                "page_url": "/disclaimer/",
                "url_slug": "disclaimer",
                "seo_title": "Legal Disclaimer | The Home First",
                "meta_description": "Read the Legal Disclaimer regarding property information, third-party listings, and financial options on The Home First.",
                "meta_keywords": "legal disclaimer, property disclaimer, thf disclaimer",
                "canonical_url": f"{site_url}/disclaimer/",
                "robots_index": "index",
                "robots_follow": "follow",
                "og_title": "Legal Disclaimer | The Home First",
                "og_description": "Read the official Legal Disclaimer for property information on The Home First.",
                "og_image_url": default_logo,
                "og_type": "website",
                "twitter_card_type": "summary_large_image",
                "twitter_title": "Legal Disclaimer | The Home First",
                "twitter_description": "Read the official Legal Disclaimer for property information on The Home First.",
                "twitter_image_url": default_logo,
                "is_in_sitemap": True,
                "sitemap_priority": 0.4,
                "structured_data_json": json.dumps({
                    "@context": "https://schema.org",
                    "@type": "WebPage",
                    "name": "Legal Disclaimer - The Home First",
                    "url": f"{site_url}/disclaimer/"
                }, indent=2)
            },
            {
                "page_name": "Payment Terms",
                "page_url": "/payment-terms/",
                "url_slug": "payment-terms",
                "seo_title": "Payment Terms & Conditions | The Home First",
                "meta_description": "Review the payment conditions, pricing, taxes, and transaction terms for paid services on The Home First.",
                "meta_keywords": "payment terms, transaction terms, thf payment policy",
                "canonical_url": f"{site_url}/payment-terms/",
                "robots_index": "index",
                "robots_follow": "follow",
                "og_title": "Payment Terms | The Home First",
                "og_description": "Review the payment terms and transaction conditions on The Home First.",
                "og_image_url": default_logo,
                "og_type": "website",
                "twitter_card_type": "summary_large_image",
                "twitter_title": "Payment Terms | The Home First",
                "twitter_description": "Review the payment terms and transaction conditions on The Home First.",
                "twitter_image_url": default_logo,
                "is_in_sitemap": True,
                "sitemap_priority": 0.4,
                "structured_data_json": json.dumps({
                    "@context": "https://schema.org",
                    "@type": "WebPage",
                    "name": "Payment Terms - The Home First",
                    "url": f"{site_url}/payment-terms/"
                }, indent=2)
            },
            {
                "page_name": "Help Centre",
                "page_url": "/help/",
                "url_slug": "help-centre",
                "seo_title": "Help Centre & FAQs | The Home First",
                "meta_description": "Find answers to frequently asked questions about posting properties, home loan eligibility, rental agreements, and account management on THF.",
                "meta_keywords": "help centre, faqs, real estate help, property search support thf",
                "canonical_url": f"{site_url}/help/",
                "robots_index": "index",
                "robots_follow": "follow",
                "og_title": "Help Centre & FAQs | The Home First",
                "og_description": "Find answers to frequently asked questions on The Home First.",
                "og_image_url": default_logo,
                "og_type": "website",
                "twitter_card_type": "summary_large_image",
                "twitter_title": "Help Centre & FAQs | The Home First",
                "twitter_description": "Find answers to frequently asked questions on The Home First.",
                "twitter_image_url": default_logo,
                "is_in_sitemap": True,
                "sitemap_priority": 0.6,
                "structured_data_json": json.dumps({
                    "@context": "https://schema.org",
                    "@type": "FAQPage",
                    "name": "Help Centre & FAQs - The Home First",
                    "url": f"{site_url}/help/"
                }, indent=2)
            },
            {
                "page_name": "Property Search",
                "page_url": "/search/",
                "url_slug": "property-search",
                "seo_title": "Advanced Property Search & Catalog | The Home First",
                "meta_description": "Search verified residential flats, commercial spaces, plots, and land across top Indian cities with advanced filters on The Home First.",
                "meta_keywords": "property search, search flats, filter properties india, thf search, property brokers near me, real estate agents search",
                "canonical_url": f"{site_url}/search/",
                "robots_index": "index",
                "robots_follow": "follow",
                "og_title": "Advanced Property Search | The Home First",
                "og_description": "Search verified residential and commercial properties across India on The Home First.",
                "og_image_url": default_logo,
                "og_type": "website",
                "twitter_card_type": "summary_large_image",
                "twitter_title": "Advanced Property Search | The Home First",
                "twitter_description": "Search verified residential and commercial properties across India on The Home First.",
                "twitter_image_url": default_logo,
                "is_in_sitemap": True,
                "sitemap_priority": 0.9,
                "structured_data_json": json.dumps({
                    "@context": "https://schema.org",
                    "@type": "SearchResultsPage",
                    "name": "Property Search & Catalog - The Home First",
                    "url": f"{site_url}/search/"
                }, indent=2)
            },
            {
                "page_name": "Featured Projects",
                "page_url": "/projects/",
                "url_slug": "featured-projects",
                "seo_title": "Featured Developer Projects & Real Estate | The Home First",
                "meta_description": "Explore RERA-registered new real estate projects, developer launches, and residential townships across India on The Home First.",
                "meta_keywords": "new projects, RERA registered projects, builder projects thf",
                "canonical_url": f"{site_url}/projects/",
                "robots_index": "index",
                "robots_follow": "follow",
                "og_title": "Featured Developer Projects | The Home First",
                "og_description": "Explore new RERA-registered builder projects and residential townships on The Home First.",
                "og_image_url": default_logo,
                "og_type": "website",
                "twitter_card_type": "summary_large_image",
                "twitter_title": "Featured Developer Projects | The Home First",
                "twitter_description": "Explore new RERA-registered builder projects and residential townships on The Home First.",
                "twitter_image_url": default_logo,
                "is_in_sitemap": True,
                "sitemap_priority": 0.7,
                "structured_data_json": json.dumps({
                    "@context": "https://schema.org",
                    "@type": "BreadcrumbList",
                    "itemListElement": [
                        {"@type": "ListItem", "position": 1, "name": "Home", "item": site_url},
                        {"@type": "ListItem", "position": 2, "name": "Featured Projects", "item": f"{site_url}/projects/"}
                    ]
                }, indent=2)
            }
        ]

        created_count = 0
        updated_count = 0

        for item in seo_records:
            page_url = item.pop("page_url")
            obj, created = SEOPage.objects.update_or_create(
                page_url=page_url,
                defaults=item
            )
            if created:
                created_count += 1
            else:
                updated_count += 1

        self.stdout.write(self.style.SUCCESS(
            f"✅ SEO Seeding complete: {created_count} records created, {updated_count} records updated."
        ))
