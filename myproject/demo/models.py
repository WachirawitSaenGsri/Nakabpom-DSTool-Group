# models.py
from django.db import models
from django.contrib.auth.models import User

# Custom User Model เพื่อรองรับบทบาท (Roles)
class Member(models.Model):
    ROLE_CHOICES = [
        ('customer', 'ลูกค้า'),
        ('staff', 'พนักงาน'),
        ('owner', 'เจ้าของร้าน'),
    ]
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='customer')
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='member_profile')

    def __str__(self):
        return f"{self.user.first_name} {self.user.last_name} ({self.user.username}) - {self.role}"

# หมวดหมู่สินค้า
class Category(models.Model):
    name = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return self.name
# Model สำหรับสินค้า
class Product(models.Model):
    name = models.CharField(max_length=255)
    img_product = models.ImageField(upload_to='img/', null=True, blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.IntegerField()
    description = models.TextField()
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return self.name

# คำสั่งซื้อ
class Order(models.Model):
    STATUS_CHOICES = [
        ("Preparation", "Preparation"),
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('canceled', 'Canceled'),
    ]
    customer = models.ForeignKey(User, on_delete=models.CASCADE, limit_choices_to={'role': 'customer'})
    date_ordered = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Preparation')

    def __str__(self):
        return f"Order {self.id} - {self.status}"

# รายละเอียดคำสั่งซื้อ
class OrderDetail(models.Model):
    order = models.ForeignKey(Order, related_name="order_details", on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=1)

    def __str__(self):
        return f"{self.product.name} x {self.quantity}"

# การชำระเงิน
class Payment(models.Model):
    PAYMENT_METHOD_CHOICES = [
        ('cash', 'Cash'),
    ]
    order = models.OneToOneField(Order, on_delete=models.CASCADE)
    method = models.CharField(max_length=10, choices=PAYMENT_METHOD_CHOICES)
    paid_amount = models.DecimalField(max_digits=10, decimal_places=2)
    date_paid = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Payment for Order {self.order.id} - {self.method}"

