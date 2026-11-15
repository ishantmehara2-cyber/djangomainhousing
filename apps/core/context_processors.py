import urllib.parse
from apps.core.models import SEOPage

def global_settings(request):
    """
    Global context processor injecting platform settings and brand constants into all Django templates.
    """
    return {
        'PLATFORM_NAME': 'The Home First',
        'PLATFORM_SHORT_NAME': 'THF',
        'PLATFORM_TAGLINE': 'Your Property. Your Possibilities.',
        'COMPANY_NAME': 'AINexTech LLP',
        'COMPANY_ADDRESS': 'Shop 10, Bhoomi Acres, Phase 2, Waghbil Road, Hiranandani Estate, Thane West, Thane - 400615',
        'SUPPORT_EMAIL': 'connectthehomefirst@gmail.com',
        'SUPPORT_PHONE': '+91-77382 30656',
        'SUPPORT_PHONE_RAW': '+917738230656',
        'COMPANY_RELATIONSHIP': 'The Home First is a real estate platform operated by AINexTech LLP.',
        'CURRENCY_SYMBOL': '₹',
    }

def seo_context(request):
    """
    Dynamic context processor retrieving SEO metadata for the current request path.
    Supports SEOPage database configurations with robust fallback values.
    """
    host = request.get_host() if hasattr(request, 'get_host') else 'www.thehomefirst.com'
    scheme = 'https' if (hasattr(request, 'is_secure') and request.is_secure()) or (hasattr(request, 'META') and request.META.get('HTTP_X_FORWARDED_PROTO') == 'https') else 'http'
    base_url = f"{scheme}://{host}"

    # Strip query parameters for canonical path determination
    clean_path = request.path if hasattr(request, 'path') else '/'
    if clean_path != '/' and clean_path.endswith('/'):
        alt_path = clean_path[:-1]
    else:
        alt_path = clean_path + '/'

    # Default fallback values
    default_title = "The Home First | Buy, Rent & Explore Properties in India"
    default_description = "Explore residential and commercial properties with The Home First (THF). Discover properties, home loan options, and online rental agreement services."
    default_keywords = "the home first, thf, buy property india, rent apartment india, commercial real estate, home loans, rental agreement"
    default_og_image = f"{base_url}/static/images/thf-og-banner.png"

    # Private route check
    is_private_route = False
    private_prefixes = ('/admin/', '/admin-panel/', '/dashboard/', '/auth/', '/billing/', '/leads/', '/api/')
    if any(clean_path.startswith(prefix) for prefix in private_prefixes):
        is_private_route = True

    default_robots_index = 'noindex' if is_private_route else 'index'
    default_robots_follow = 'nofollow' if is_private_route else 'follow'

    seo_page = None
    try:
        seo_page = SEOPage.objects.filter(page_url=clean_path).first()
        if not seo_page:
            seo_page = SEOPage.objects.filter(page_url=alt_path).first()
    except Exception:
        seo_page = None

    if seo_page:
        title = seo_page.seo_title or default_title
        description = seo_page.meta_description or default_description
        keywords = seo_page.meta_keywords or default_keywords

        canonical_url = seo_page.canonical_url.strip() if seo_page.canonical_url else f"{base_url}{clean_path}"
        robots = f"{seo_page.robots_index}, {seo_page.robots_follow}"

        og_title = seo_page.og_title or title
        og_description = seo_page.og_description or description

        if seo_page.og_image_url:
            og_image = seo_page.og_image_url
        elif seo_page.og_image_file:
            og_image = request.build_absolute_uri(seo_page.og_image_file.url)
        else:
            og_image = default_og_image

        og_type = seo_page.og_type or "website"

        twitter_card = seo_page.twitter_card_type or "summary_large_image"
        twitter_title = seo_page.twitter_title or og_title
        twitter_description = seo_page.twitter_description or og_description

        if seo_page.twitter_image_url:
            twitter_image = seo_page.twitter_image_url
        elif seo_page.twitter_image_file:
            twitter_image = request.build_absolute_uri(seo_page.twitter_image_file.url)
        else:
            twitter_image = og_image

        structured_data_json = seo_page.structured_data_json
    else:
        title = default_title
        description = default_description
        keywords = default_keywords
        canonical_url = f"{base_url}{clean_path}"
        robots = f"{default_robots_index}, {default_robots_follow}"
        og_title = default_title
        og_description = default_description
        og_image = default_og_image
        og_type = "website"
        twitter_card = "summary_large_image"
        twitter_title = default_title
        twitter_description = default_description
        twitter_image = default_og_image
        structured_data_json = None

    return {
        'seo': {
            'title': title,
            'description': description,
            'keywords': keywords,
            'canonical_url': canonical_url,
            'robots': robots,
            'og_site_name': 'The Home First',
            'og_title': og_title,
            'og_description': og_description,
            'og_image': og_image,
            'og_type': og_type,
            'twitter_card': twitter_card,
            'twitter_title': twitter_title,
            'twitter_description': twitter_description,
            'twitter_image': twitter_image,
            'structured_data_json': structured_data_json,
        }
    }
