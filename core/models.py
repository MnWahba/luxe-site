from django.db import models


class SiteSettings(models.Model):
    """
    Single-row settings table — controls Home page content from Admin.
    """
    # ── Hero Section ──
    hero_title_en = models.CharField(max_length=100, default='Carry Your')
    hero_title_ar = models.CharField(max_length=100, default='احملي قصتك')
    hero_highlight_en = models.CharField(max_length=80, default='Story.')
    hero_highlight_ar = models.CharField(max_length=80, default='بأناقة.')
    hero_subtitle_en = models.TextField(default='Discover our curated collection of premium bags and accessories crafted for the modern woman.')
    hero_subtitle_ar = models.TextField(default='اكتشفي مجموعتنا المختارة من الحقائب والإكسسوارات الفاخرة للمرأة العصرية.')
    hero_image = models.ImageField(
        upload_to='site/', null=True, blank=True,
        help_text='Product/banner image for the hero section (recommended: 600×600px square)'
    )
    hero_bg_image = models.ImageField(
        upload_to='site/', null=True, blank=True,
        help_text='Full background cover image for the Hero section (replaces the dark gradient). Recommended: 1920×900px'
    )
    hero_bg_overlay = models.PositiveSmallIntegerField(
        default=70,
        help_text='Hero background overlay darkness 0-100 (default 70). Higher = darker text will be more readable.'
    )
    hero_badge_en = models.CharField(max_length=60, default='New Collection 2024')
    hero_badge_ar = models.CharField(max_length=60, default='مجموعة 2024 الجديدة')

    hero_bg_image = models.ImageField(
        upload_to='site/', null=True, blank=True,
        help_text='Full background cover image for the Hero section. Recommended: 1920×800px wide landscape'
    )
    hero_bg_overlay_opacity = models.PositiveSmallIntegerField(
        default=75,
        help_text='Dark overlay on top of hero background (0=transparent, 100=fully dark). Default: 75'
    )

    # ── Stats ──
    stat_products_label = models.CharField(max_length=20, default='Products',
        help_text='Leave blank to auto-count from DB')
    stat_customers = models.CharField(max_length=20, default='10K+',
        help_text='e.g. 10K+ — shown as "10K+ Customers"')
    stat_rating = models.CharField(max_length=10, default='4.9',
        help_text='e.g. 4.9 — shown as "★ 4.9 Rating"')

    # ── Promo Banner ──
    promo_active = models.BooleanField(default=True, help_text='Show/hide the promo banner')
    promo_discount_percentage = models.PositiveSmallIntegerField(
        default=40,
        help_text='Discount % shown on banner (e.g. 40 → "Up to 40% OFF")'
    )
    promo_title_en = models.CharField(max_length=100, default='New Arrivals')
    promo_title_ar = models.CharField(max_length=100, default='وصل جديد')
    promo_subtitle_en = models.CharField(max_length=200, default="Don't miss our latest collection at special prices.")
    promo_subtitle_ar = models.CharField(max_length=200, default='لا تفوتي مجموعتنا الجديدة بأسعار مميزة.')
    promo_coupon_code = models.CharField(max_length=30, default='WELCOME10',
        help_text='Coupon code shown on banner')
    promo_image = models.ImageField(
        upload_to='site/', null=True, blank=True,
        help_text='Promo banner side image (optional, recommended: 300×300px)'
    )
    promo_bg_image = models.ImageField(
        upload_to='site/', null=True, blank=True,
        help_text='Full background image for the promo banner (replaces the dark gradient). Recommended: 1280×400px'
    )
    promo_bg_overlay_opacity = models.PositiveSmallIntegerField(
        default=60,
        help_text='Dark overlay on top of bg image (0=none, 100=fully dark). Default: 60'
    )

    # ── Featured Section ──
    featured_title_en = models.CharField(max_length=100, default='Handpicked For You')
    featured_title_ar = models.CharField(max_length=100, default='مختارة لكِ بعناية')
    new_arrivals_title_en = models.CharField(max_length=100, default='New Arrivals')
    new_arrivals_title_ar = models.CharField(max_length=100, default='وصل حديثاً')

    # ── Contact/Social ──
    whatsapp_number = models.CharField(max_length=20, default='201212184205')
    facebook_url = models.URLField(default='https://facebook.com', blank=True)
    instagram_url = models.URLField(blank=True)
    instapay_number = models.CharField(max_length=20, default='01205951559', blank=True)
    orange_cash_number = models.CharField(max_length=20, default='01223184205', blank=True)

    class Meta:
        verbose_name = 'Site Settings'
        verbose_name_plural = 'Site Settings'

    def __str__(self):
        return 'Site Settings'

    @classmethod
    def get(cls):
        """Always returns the single settings instance, creating it if needed."""
        obj, _ = cls.objects.get_or_create(pk=1)
        return obj

    def save(self, *args, **kwargs):
        self.pk = 1  # enforce singleton
        super().save(*args, **kwargs)
