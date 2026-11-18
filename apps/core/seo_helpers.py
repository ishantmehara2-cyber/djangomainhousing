import json

def format_price_for_seo(property_item):
    """Formats property price or rent into readable currency format for SEO descriptions."""
    if property_item.listing_purpose == 'RENT' and property_item.rent:
        return f"₹{property_item.rent:,.0f} / month"
    elif property_item.price:
        val = float(property_item.price)
        if val >= 10000000:
            return f"₹{val / 10000000:.2f} Cr"
        elif val >= 100000:
            return f"₹{val / 100000:.2f} Lakhs"
        else:
            return f"₹{val:,.0f}"
    return "Contact for Price"

def build_property_seo_context(request, property_item, media_items=None):
    """
    Generates rich dynamic SEO metadata, Open Graph tags, Twitter card tags,
    and Schema.org JSON-LD structured data for a property detail page.
    """
    host = request.get_host() if hasattr(request, 'get_host') else 'www.thehomefirst.com'
    scheme = 'https' if request.is_secure() else 'http'
    base_url = f"{scheme}://{host}"

    canonical_url = f"{base_url}/property/{property_item.slug}/"

    locality_name = property_item.locality.name if property_item.locality else ""
    city_name = property_item.city.name if property_item.city else ""
    location_str = f"{locality_name}, {city_name}" if locality_name else city_name

    purpose_display = property_item.get_listing_purpose_display()

    if property_item.bhk:
        title = f"{property_item.bhk} BHK {property_item.property_type.name} for {purpose_display} in {location_str} | The Home First"
    else:
        title = f"{property_item.title} for {purpose_display} in {location_str} | The Home First"

    price_str = format_price_for_seo(property_item)
    area_str = f"{property_item.built_up_area or property_item.carpet_area:,.0f} {property_item.get_area_unit_display()}"

    description = (
        f"Explore this {property_item.title} for {purpose_display} in {location_str}. "
        f"Price: {price_str}, Built-up Area: {area_str}. "
        f"View verified details, available amenities, photos, and submit an enquiry through The Home First."
    )

    # Resolve Cover / Thumbnail image for social sharing
    main_image_url = f"{base_url}/static/images/thf-og-banner.png"
    images_list = []

    if property_item.thumbnail_media and property_item.thumbnail_media.file:
        main_image_url = request.build_absolute_uri(property_item.thumbnail_media.file.url)
        images_list.append(main_image_url)

    if media_items:
        for m in media_items:
            if m.file and hasattr(m, 'media_type') and m.media_type == 'IMAGE':
                img_url = request.build_absolute_uri(m.file.url)
                if img_url not in images_list:
                    images_list.append(img_url)
                    if main_image_url == f"{base_url}/static/images/thf-og-banner.png":
                        main_image_url = img_url

    if not images_list:
        images_list = [main_image_url]

    # Schema.org Structured Data
    schema_type = "Apartment" if (property_item.bhk or "apartment" in property_item.property_type.name.lower()) else "SingleFamilyResidence"

    price_val = float(property_item.price or property_item.rent or 0)

    structured_data = {
        "@context": "https://schema.org",
        "@graph": [
            {
                "@type": "BreadcrumbList",
                "@id": f"{canonical_url}#breadcrumb",
                "itemListElement": [
                    {"@type": "ListItem", "position": 1, "name": "Home", "item": base_url},
                    {"@type": "ListItem", "position": 2, "name": f"Properties in {city_name}", "item": f"{base_url}/search/?city={property_item.city.slug if property_item.city else ''}"},
                    {"@type": "ListItem", "position": 3, "name": property_item.title, "item": canonical_url}
                ]
            },
            {
                "@type": schema_type,
                "@id": f"{canonical_url}#property",
                "name": property_item.title,
                "description": description,
                "url": canonical_url,
                "image": images_list[:5],
                "address": {
                    "@type": "PostalAddress",
                    "streetAddress": property_item.address or "",
                    "addressLocality": locality_name,
                    "addressRegion": city_name,
                    "postalCode": property_item.pincode or "",
                    "addressCountry": "IN"
                },
                "geo": {
                    "@type": "GeoCoordinates",
                    "latitude": property_item.latitude or 19.0760,
                    "longitude": property_item.longitude or 72.8777
                },
                "offers": {
                    "@type": "Offer",
                    "price": price_val,
                    "priceCurrency": "INR",
                    "availability": "https://schema.org/InStock",
                    "url": canonical_url
                }
            }
        ]
    }

    return {
        'seo': {
            'title': title,
            'description': description,
            'keywords': f"{property_item.title}, property for sale in {location_str}, rent property in {location_str}, thf property",
            'canonical_url': canonical_url,
            'robots': "index, follow",
            'og_site_name': "The Home First",
            'og_title': title,
            'og_description': description,
            'og_image': main_image_url,
            'og_type': "article",
            'twitter_card': "summary_large_image",
            'twitter_title': title,
            'twitter_description': description,
            'twitter_image': main_image_url,
            'structured_data_json': json.dumps(structured_data, indent=2),
        }
    }
