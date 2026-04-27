from django.db import models
from django.utils.text import slugify
from django.core.validators import MinValueValidator, MaxValueValidator
import uuid


class Category(models.Model):
    name_en = models.CharField(max_length=100)
    name_ar = models.CharField(max_length=100)
    slug = models.SlugField(unique=True, blank=True)
    description_en = models.TextField(blank=True)
    description_ar = models.TextField(blank=True)
    image = models.ImageField(upload_to='categories/', null=True, blank=True)
    is_active = models.BooleanField(default=True)
    order = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Category'
        verbose_name_plural = 'Categories'
        ordering = ['order', 'name_en']

    def __str__(self):
        return self.name_en

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name_en)
        super().save(*args, **kwargs)

    def get_name(self, lang='en'):
        return self.name_ar if lang == 'ar' else self.name_en


class Product(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, related_name='products')
    name_en = models.CharField(max_length=200)
    name_ar = models.CharField(max_length=200)
    slug = models.SlugField(unique=True, blank=True, max_length=250)
    description_en = models.TextField()
    description_ar = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    discount_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, validators=[MinValueValidator(0)])
    stock = models.PositiveIntegerField(default=0)
    sku = models.CharField(max_length=100, unique=True, blank=True)
    is_active = models.BooleanField(default=True)
    is_featured = models.BooleanField(default=False)
    is_new_arrival = models.BooleanField(default=False)
    weight = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    dimensions = models.CharField(max_length=100, blank=True)
    material_en = models.CharField(max_length=200, blank=True)
    material_ar = models.CharField(max_length=200, blank=True)
    views_count = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Product'
        verbose_name_plural = 'Products'
        ordering = ['-created_at']

    def __str__(self):
        return self.name_en

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.name_en)
            slug = base_slug
            counter = 1
            while Product.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = slug
        if not self.sku:
            self.sku = f"LB-{str(uuid.uuid4())[:8].upper()}"
        super().save(*args, **kwargs)

    def get_name(self, lang='en'):
        return self.name_ar if lang == 'ar' else self.name_en

    def get_description(self, lang='en'):
        return self.description_ar if lang == 'ar' else self.description_en

    @property
    def effective_price(self):
        return self.discount_price if self.discount_price else self.price

    @property
    def discount_percentage(self):
        if self.discount_price and self.price > 0:
            return int(((self.price - self.discount_price) / self.price) * 100)
        return 0

    @property
    def is_in_stock(self):
        return self.stock > 0

    @property
    def average_rating(self):
        reviews = self.reviews.filter(is_approved=True)
        if reviews.exists():
            return round(sum(r.rating for r in reviews) / reviews.count(), 1)
        return 0

    @property
    def review_count(self):
        return self.reviews.filter(is_approved=True).count()

    def get_primary_image(self):
        img = self.images.filter(is_primary=True).first()
        if not img:
            img = self.images.first()
        return img


class ProductImage(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='products/')
    alt_text = models.CharField(max_length=200, blank=True)
    is_primary = models.BooleanField(default=False)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order', 'id']

    def __str__(self):
        return f"Image for {self.product.name_en}"

    def save(self, *args, **kwargs):
        if self.is_primary:
            ProductImage.objects.filter(product=self.product, is_primary=True).update(is_primary=False)
        super().save(*args, **kwargs)




class ProductColor(models.Model):
    """
    Color variants for a product.
    Each color can have its own stock quantity and optional image.
    """
    product = models.ForeignKey(
        Product, on_delete=models.CASCADE, related_name='colors'
    )
    name_en = models.CharField(max_length=50, help_text='e.g. Black, Rose Gold, Cream')
    name_ar = models.CharField(max_length=50, help_text='e.g. أسود، ذهبي وردي، كريم')
    hex_code = models.CharField(
        max_length=7, default='#000000',
        help_text='Color hex code e.g. #FF5733 — used as a color swatch'
    )
    stock = models.PositiveIntegerField(
        default=0,
        help_text='Stock for this color. 0 = unavailable'
    )
    image = models.ImageField(
        upload_to='products/colors/', null=True, blank=True,
        help_text='Optional: product image showing this color variant'
    )
    is_active = models.BooleanField(default=True)
    order = models.PositiveSmallIntegerField(default=0)

    class Meta:
        ordering = ['order', 'name_en']
        verbose_name = 'Product Color'
        verbose_name_plural = 'Product Colors'

    def __str__(self):
        return f"{self.product.name_en} — {self.name_en}"

    def get_name(self, lang='en'):
        return self.name_ar if lang == 'ar' else self.name_en

    @property
    def is_available(self):
        return self.is_active and self.stock > 0

class Wishlist(models.Model):
    user = models.ForeignKey('users.CustomUser', on_delete=models.CASCADE, related_name='wishlist')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['user', 'product']

    def __str__(self):
        return f"{self.user.email} - {self.product.name_en}"
