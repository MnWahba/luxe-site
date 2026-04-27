from django.contrib import admin
from django.utils.html import format_html
from django.db.models import Sum, Count, Avg
from django.utils import timezone
from datetime import timedelta
from .models import SiteSettings


@admin.register(SiteSettings)
class SiteSettingsAdmin(admin.ModelAdmin):
    # No list view — go straight to the single instance
    change_list_template = None

    fieldsets = (
        ('🏠 Hero Section — القسم الرئيسي', {
            'description': 'Controls the main banner at the top of the homepage.',
            'fields': (
                'hero_badge_en', 'hero_badge_ar',
                'hero_title_en', 'hero_title_ar',
                'hero_highlight_en', 'hero_highlight_ar',
                'hero_subtitle_en', 'hero_subtitle_ar',
                'hero_image',
                'hero_bg_image',
                'hero_bg_overlay',
            )
        }),
        ('📊 Stats — الإحصائيات', {
            'description': 'Numbers shown below the hero buttons. Product count is auto-calculated.',
            'fields': ('stat_customers', 'stat_rating'),
        }),
        ('🏷️ Promo Banner — بانر العروض', {
            'description': 'The "Up to X% OFF" banner in the middle of the homepage.',
            'fields': (
                'promo_active',
                'promo_discount_percentage',
                'promo_coupon_code',
                'promo_title_en', 'promo_title_ar',
                'promo_subtitle_en', 'promo_subtitle_ar',
                'promo_image',
                'promo_bg_image',
                'promo_bg_overlay_opacity',
            )
        }),
        ('📦 Section Titles — عناوين الأقسام', {
            'classes': ('collapse',),
            'fields': (
                'featured_title_en', 'featured_title_ar',
                'new_arrivals_title_en', 'new_arrivals_title_ar',
            )
        }),
        ('📱 Contact & Social — التواصل', {
            'classes': ('collapse',),
            'fields': (
                'whatsapp_number', 'facebook_url', 'instagram_url',
                'instapay_number', 'orange_cash_number',
            )
        }),
    )

    def has_add_permission(self, request):
        return not SiteSettings.objects.exists()

    def has_delete_permission(self, request, obj=None):
        return False

    def changelist_view(self, request, extra_context=None):
        # Redirect directly to the single instance
        from django.shortcuts import redirect
        obj = SiteSettings.get()
        return redirect(f'/admin/core/sitesettings/{obj.pk}/change/')

    def save_model(self, request, obj, form, change):
        obj.pk = 1
        super().save_model(request, obj, form, change)
        from django.contrib import messages
        self.message_user(request, '✓ Site settings saved successfully!', messages.SUCCESS)
