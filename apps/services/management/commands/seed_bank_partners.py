from django.core.management.base import BaseCommand
from apps.services.models import BankPartner, BankCategoryChoices, ProcessingFeeTypeChoices

INITIAL_BANKS = [
    {
        'name': 'HDFC Bank',
        'slug': 'hdfc-bank',
        'category': BankCategoryChoices.PRIVATE_SECTOR,
        'min_interest_rate': 8.50,
        'max_interest_rate': 9.15,
        'max_tenure_years': 30,
        'processing_fee_info': '0.50% of loan amount + GST',
        'processing_fee_type': ProcessingFeeTypeChoices.PERCENTAGE,
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
        'category': BankCategoryChoices.PUBLIC_SECTOR,
        'min_interest_rate': 8.40,
        'max_interest_rate': 9.05,
        'max_tenure_years': 30,
        'processing_fee_info': 'Nil to 0.35% + GST',
        'processing_fee_type': ProcessingFeeTypeChoices.RANGE,
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
        'category': BankCategoryChoices.PRIVATE_SECTOR,
        'min_interest_rate': 8.60,
        'max_interest_rate': 9.25,
        'max_tenure_years': 30,
        'processing_fee_info': '0.50% or ₹3,000 + GST',
        'processing_fee_type': ProcessingFeeTypeChoices.CUSTOM,
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
        'category': BankCategoryChoices.PRIVATE_SECTOR,
        'min_interest_rate': 8.55,
        'max_interest_rate': 9.10,
        'max_tenure_years': 30,
        'processing_fee_info': 'Up to 1% or ₹10,000',
        'processing_fee_type': ProcessingFeeTypeChoices.CUSTOM,
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

class Command(BaseCommand):
    help = 'Idempotently seeds initial Banking Partners (HDFC, SBI, ICICI, Axis)'

    def handle(self, *args, **options):
        self.stdout.write('🌱 Seeding initial Banking Partners...')

        created_count = 0
        updated_count = 0

        for bank_data in INITIAL_BANKS:
            slug = bank_data['slug']
            bank, created = BankPartner.objects.get_or_create(
                slug=slug,
                defaults=bank_data
            )

            if created:
                created_count += 1
            else:
                for field, val in bank_data.items():
                    setattr(bank, field, val)
                bank.save()
                updated_count += 1

        self.stdout.write(
            self.style.SUCCESS(
                f'✅ Successfully seeded Banking Partners! '
                f'Total: {BankPartner.objects.count()} (Created: {created_count}, Updated: {updated_count})'
            )
        )
