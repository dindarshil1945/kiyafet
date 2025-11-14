from django.db import models
from django.contrib.auth.models import User
# Create your models here.

class UserProfile(models.Model):
    USER_TYPES = (
        ('customer', 'Customer'),
        ('staff', 'Staff'),
    )

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    user_type = models.CharField(max_length=10, choices=USER_TYPES, default='customer')
    
    phone = models.CharField(max_length=15, blank=True, null=True)

    def __str__(self):
        return f"{self.user.username} - {self.user_type}"
    
CATEGORIES = (
    ("Kurti","Kurti"),
    ("Short Kurti","Short Kurti"),
    ("Top","Top"),
    ("Salwar","Salwar"),
    ("Churidar","Churidar"),
    ("Saree","Saree"),
)

class Product(models.Model):
    name = models.CharField(max_length=200)
    category = models.CharField(max_length=50, choices=CATEGORIES)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.TextField(blank=True, null=True)
    cover_image = models.ImageField(upload_to="products/cover/")

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


# Additional Gallery Images
class ProductImage(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="images")
    image = models.ImageField(upload_to="products/gallery/")

    def __str__(self):
        return f"{self.product.name} Image"
    
class CartItem(models.Model):
    SIZE_CHOICES = [
        ("S", "S"),
        ("M", "M"),
        ("L", "L"),
        ("XL", "XL"),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    size = models.CharField(max_length=5, choices=SIZE_CHOICES, default="M")
    quantity = models.PositiveIntegerField(default=1)

    def subtotal(self):
        return self.product.price * self.quantity

    def __str__(self):
        return f"{self.product.name} ({self.size}) x {self.quantity}"

class Address(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    full_name = models.CharField(max_length=100)
    phone = models.CharField(max_length=15)
    house = models.CharField(max_length=200)
    street = models.CharField(max_length=200)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    pincode = models.CharField(max_length=10)
    country = models.CharField(max_length=100, default="India")

    def __str__(self):
        return f"{self.house}, {self.city}"
