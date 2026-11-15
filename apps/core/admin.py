from django.contrib import admin
from django.utils.html import format_html
from django.utils.safestring import mark_safe
from apps.core.models import (
    CMSContent, FeatureFlag, SystemSetting, FAQCategory, FAQItem,
    SupportTicket, TicketMessage, ContactEnquiry, CompanyNotificationLog, SEOPage
)

@admin.register(SEOPage)
class SEOPageAdmin(admin.ModelAdmin):
    list_display = (
        'page_name', 'page_url', 'seo_title_summary', 'robots_badge',
        'is_in_sitemap', 'sitemap_priority', 'updated_at'
    )
    list_filter = ('robots_index', 'robots_follow', 'is_in_sitemap', 'og_type', 'twitter_card_type')
    search_fields = ('page_name', 'page_url', 'seo_title', 'meta_description', 'meta_keywords')
    ordering = ('page_name',)
    readonly_fields = ('seo_live_preview', 'created_at', 'updated_at')

    fieldsets = (
        ('1. Page Identification', {
            'fields': ('page_name', 'page_url', 'url_slug'),
            'description': 'Configure the target URL path and slug for this page record.'
        }),
        ('2. Search Engine Metadata (Google Search)', {
            'fields': (
                'seo_title', 'meta_description', 'meta_keywords',
                'canonical_url', 'robots_index', 'robots_follow'
            ),
            'description': 'Main title, description, canonical link and indexing directives for search engines.'
        }),
        ('3. Live SEO Preview Widget', {
            'fields': ('seo_live_preview',),
            'description': 'Real-time preview of how this page will appear in Google search and social media shares.'
        }),
        ('4. Open Graph Metadata (Facebook / LinkedIn / WhatsApp)', {
            'fields': ('og_title', 'og_description', 'og_image_file', 'og_image_url', 'og_type'),
            'classes': ('collapse',),
        }),
        ('5. Twitter / X Card Metadata', {
            'fields': ('twitter_card_type', 'twitter_title', 'twitter_description', 'twitter_image_file', 'twitter_image_url'),
            'classes': ('collapse',),
        }),
        ('6. Structured Data & Sitemap', {
            'fields': ('structured_data_json', 'is_in_sitemap', 'sitemap_priority'),
            'classes': ('collapse',),
        }),
        ('7. Record Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',),
        }),
    )

    def seo_title_summary(self, obj):
        return obj.seo_title[:50] + ('...' if len(obj.seo_title) > 50 else '')
    seo_title_summary.short_description = 'SEO Title'

    def robots_badge(self, obj):
        index_color = 'green' if obj.robots_index == 'index' else 'red'
        follow_color = 'blue' if obj.robots_follow == 'follow' else 'gray'
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>, '
            '<span style="color: {};">{}</span>',
            index_color, obj.robots_index, follow_color, obj.robots_follow
        )
    robots_badge.short_description = 'Robots Directives'

    def seo_live_preview(self, obj):
        if not obj or not obj.pk:
            return "Save the record first to display the live SEO snippet preview."

        title = obj.seo_title or "The Home First | Your Property. Your Possibilities."
        desc = obj.meta_description or "Explore residential and commercial properties with The Home First."
        url = f"https://www.thehomefirst.com{obj.page_url}"

        title_len = len(title)
        desc_len = len(desc)

        title_status = "Optimal" if 40 <= title_len <= 65 else ("Too Long" if title_len > 65 else "Too Short")
        title_color = "#16a34a" if title_status == "Optimal" else "#dc2626"

        desc_status = "Optimal" if 130 <= desc_len <= 165 else ("Too Long" if desc_len > 165 else "Too Short")
        desc_color = "#16a34a" if desc_status == "Optimal" else "#dc2626"

        og_img = obj.og_image_url or (obj.og_image_file.url if obj.og_image_file else "")

        html = f"""
        <div style="font-family: Arial, sans-serif; background: #f8fafc; border: 1px solid #e2e8f0; padding: 20px; border-radius: 12px; max-width: 750px;">
            <h3 style="margin-top: 0; color: #0f172a; font-size: 15px; border-bottom: 1px solid #e2e8f0; padding-bottom: 8px;">
                🔍 Google Search Snippet Preview
            </h3>
            <div style="background: white; border: 1px solid #dadce0; padding: 16px; border-radius: 8px; margin-bottom: 16px;">
                <div style="font-size: 14px; color: #202124; line-height: 1.3;">
                    <span style="font-size: 12px; color: #4d5156; display: block; margin-bottom: 2px;">{url}</span>
                    <a href="#" style="color: #1a0dab; text-decoration: none; font-size: 20px; font-weight: 400; line-height: 1.3; display: block; margin-bottom: 4px;">{title}</a>
                    <div style="color: #4d5156; font-size: 14px; line-height: 1.58;">{desc}</div>
                </div>
            </div>

            <div style="display: flex; gap: 20px; margin-bottom: 16px; font-size: 12px; color: #475569;">
                <div>
                    <strong>Title Length:</strong> {title_len} chars
                    <span style="color: {title_color}; font-weight: bold; background: #f1f5f9; padding: 2px 6px; border-radius: 4px;">({title_status})</span>
                </div>
                <div>
                    <strong>Meta Description Length:</strong> {desc_len} chars
                    <span style="color: {desc_color}; font-weight: bold; background: #f1f5f9; padding: 2px 6px; border-radius: 4px;">({desc_status})</span>
                </div>
            </div>

            <h3 style="margin-top: 16px; color: #0f172a; font-size: 15px; border-bottom: 1px solid #e2e8f0; padding-bottom: 8px;">
                📲 Social Share Preview (Open Graph & Twitter)
            </h3>
            <div style="background: white; border: 1px solid #e2e8f0; border-radius: 8px; overflow: hidden; max-width: 500px;">
                {'<img src="' + og_img + '" style="width: 100%; height: 200px; object-fit: cover;" />' if og_img else '<div style="background: #e2e8f0; height: 160px; display: flex; items-center; justify-content: center; color: #64748b; font-size: 13px;">No Open Graph Image Specified (Fallback image will be used)</div>'}
                <div style="padding: 12px; background: #f8fafc;">
                    <div style="font-size: 11px; color: #64748b; text-transform: uppercase; font-weight: bold;">www.thehomefirst.com</div>
                    <div style="font-weight: bold; font-size: 14px; color: #0f172a; margin: 4px 0;">{obj.og_title or title}</div>
                    <div style="font-size: 12px; color: #64748b; font-weight: normal;">{obj.og_description or desc}</div>
                </div>
            </div>
        </div>
        """
        return mark_safe(html)

    seo_live_preview.short_description = 'Live SEO Preview'


@admin.register(CMSContent)
class CMSContentAdmin(admin.ModelAdmin):
    list_display = ('title', 'slug', 'updated_at')
    search_fields = ('title', 'slug', 'content')


@admin.register(FeatureFlag)
class FeatureFlagAdmin(admin.ModelAdmin):
    list_display = ('key', 'is_enabled', 'description')
    list_filter = ('is_enabled',)
    search_fields = ('key', 'description')


@admin.register(SystemSetting)
class SystemSettingAdmin(admin.ModelAdmin):
    list_display = ('key', 'value')
    search_fields = ('key', 'value')


@admin.register(FAQCategory)
class FAQCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'display_order')
    prepopulated_fields = {'slug': ('name',)}


@admin.register(FAQItem)
class FAQItemAdmin(admin.ModelAdmin):
    list_display = ('question', 'category', 'display_order', 'is_published')
    list_filter = ('category', 'is_published')
    search_fields = ('question', 'answer')


@admin.register(SupportTicket)
class SupportTicketAdmin(admin.ModelAdmin):
    list_display = ('ticket_id', 'user', 'category', 'status', 'priority', 'created_at')
    list_filter = ('status', 'priority', 'category')
    search_fields = ('ticket_id', 'subject', 'user__username', 'user__email')


@admin.register(ContactEnquiry)
class ContactEnquiryAdmin(admin.ModelAdmin):
    list_display = ('reference_number', 'name', 'email', 'phone', 'status', 'created_at')
    list_filter = ('status',)
    search_fields = ('reference_number', 'name', 'email', 'phone')
