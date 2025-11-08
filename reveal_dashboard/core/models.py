from django.db import models

class Product(models.Model):
    name = models.CharField(max_length=100, verbose_name="اسم المنتج")
    description = models.TextField(blank=True, null=True, verbose_name="الوصف")
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="السعر")
    image = models.ImageField(upload_to='products/', blank=True, null=True, verbose_name="صورة المنتج")
    is_available = models.BooleanField(default=True, verbose_name="متوفر؟")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name
