from django.contrib import admin
from store_app.models import UserProfile,Product,ProductImage

# Register your models here.
admin.site.register(UserProfile)
admin.site.register(Product)
admin.site.register(ProductImage)