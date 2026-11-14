def global_settings(request):
    """
    Global context processor injecting platform settings and brand constants into all Django templates.
    """
    return {
        'PLATFORM_NAME': 'The Home First',
        'PLATFORM_SHORT_NAME': 'THF',
        'PLATFORM_TAGLINE': 'Your Property. Your Possibilities.',
        'SUPPORT_EMAIL': 'support@thehomefirst.com',
        'SUPPORT_PHONE': '+91 1800 123 4567',
        'CURRENCY_SYMBOL': '₹',
    }
