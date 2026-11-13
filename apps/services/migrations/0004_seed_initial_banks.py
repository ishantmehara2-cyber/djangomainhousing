from django.db import migrations

INITIAL_BANKS = [
    {
        'name': 'HDFC Bank',
        'slug': 'hdfc-bank',
        'category': 'PRIVATE_SECTOR',
        'min_interest_rate': 8.50,
        'max_interest_rate': 9.15,
        'max_tenure_years': 30,
        'processing_fee_info': '0.50% of loan amount + GST',
        'processing_fee_type': 'PERCENTAGE',
        'benefits': [
            'Instant digital sanction',
            'Special rates for women borrowers',
            'Zero prepayment penalty'
        ],
        'display_order': 1,
        'short_description': 'India’s leading private bank offering fast home loan approvals and digital processing.',
        'website_url': 'https://www.hdfcbank.com',
        'application_url': 'https://www.hdfcbank.com/personal/borrow/popular-loans/home-loan',
    },
    {
        'name': 'State Bank of India (SBI)',
        'slug': 'state-bank-of-india-sbi',
        'category': 'PUBLIC_SECTOR',
        'min_interest_rate': 8.40,
        'max_interest_rate': 9.05,
        'max_tenure_years': 30,
        'processing_fee_info': 'Nil to 0.35% + GST',
        'processing_fee_type': 'RANGE',
        'benefits': [
            'Concession on CIBIL score 750+',
            'Overdraft facility available',
            'No hidden charges'
        ],
        'display_order': 2,
        'short_description': 'India’s largest public sector bank with lowest interest rates and widespread branch network.',
        'website_url': 'https://sbi.co.in',
        'application_url': 'https://homeloans.sbi',
    },
    {
        'name': 'ICICI Bank',
        'slug': 'icici-bank',
        'category': 'PRIVATE_SECTOR',
        'min_interest_rate': 8.60,
        'max_interest_rate': 9.25,
        'max_tenure_years': 30,
        'processing_fee_info': '0.50% or ₹3,000 + GST',
        'processing_fee_type': 'CUSTOM',
        'benefits': [
            'Pre-approved home loans',
            'Flexible repayment options',
            'Balance transfer benefits'
        ],
        'display_order': 3,
        'short_description': 'Technology-driven home loan solutions with instant pre-approval for existing customers.',
        'website_url': 'https://www.icicibank.com',
        'application_url': 'https://www.icicibank.com/personal-banking/loans/home-loan',
    },
    {
        'name': 'Axis Bank',
        'slug': 'axis-bank',
        'category': 'PRIVATE_SECTOR',
        'min_interest_rate': 8.55,
        'max_interest_rate': 9.10,
        'max_tenure_years': 30,
        'processing_fee_info': 'Up to 1% or ₹10,000',
        'processing_fee_type': 'CUSTOM',
        'benefits': [
            '12 EMI waiver on timely payments',
            '100% digital process',
            'Customized top-up loans'
        ],
        'display_order': 4,
        'short_description': 'Attractive home loan offers with EMI waivers on long-term home loans.',
        'website_url': 'https://www.axisbank.com',
        'application_url': 'https://www.axisbank.com/retail/loans/home-loan',
    }
]

def seed_banks(apps, schema_editor):
    BankPartner = apps.get_model('services', 'BankPartner')
    for b in INITIAL_BANKS:
        BankPartner.objects.get_or_create(slug=b['slug'], defaults=b)

def reverse_seed(apps, schema_editor):
    pass

class Migration(migrations.Migration):

    dependencies = [
        ('services', '0003_bankpartner_additional_charges_and_more'),
    ]

    operations = [
        migrations.RunPython(seed_banks, reverse_code=reverse_seed),
    ]
