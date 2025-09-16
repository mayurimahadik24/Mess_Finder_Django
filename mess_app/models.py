# from django.db import models

# Create your models here.
from django.db import models
from django.contrib.auth.models import User


class Mess(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    address = models.TextField(default="Not provided")  # added default
    location = models.CharField(max_length=100, default="Unknown")
    pincode = models.CharField(max_length=6, default="000000")
    photo = models.ImageField(upload_to='mess_photos/', blank=True, null=True)
    contact = models.CharField(max_length=15)
    food_type = models.CharField(max_length=50)   # e.g., Veg, Non-Veg
    price = models.DecimalField(max_digits=8, decimal_places=2)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name



class MenuItem(models.Model):
    mess = models.ForeignKey(Mess, on_delete=models.CASCADE)
    name = models.CharField(max_length=200)
    price = models.DecimalField(max_digits=7, decimal_places=2)
    description = models.TextField(blank=True)
    photo = models.ImageField(upload_to="menu_photos/", blank=True, null=True)

    def __str__(self):
        return f"{self.name} ({self.mess.name})"

class MessBooking(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    mess = models.ForeignKey(Mess, on_delete=models.CASCADE)
    date = models.DateField()
    timing = models.CharField(max_length=10, choices=[('Lunch', 'Lunch'), ('Dinner', 'Dinner')])
    created_at = models.DateTimeField(auto_now_add=True)

# class Order(models.Model):
#     user = models.ForeignKey(User, on_delete=models.CASCADE)
#     mess = models.ForeignKey(Mess, on_delete=models.CASCADE)
#     items = models.ManyToManyField(MenuItem)
#     total_price = models.DecimalField(max_digits=6, decimal_places=2, default=0)
#     status = models.CharField(max_length=20, choices=[
#         ('Pending', 'Pending'),
#         ('Accepted', 'Accepted'),
#         ('Rejected', 'Rejected'),
#         ('Delivered', 'Delivered')
#     ], default='Pending')
#     created_at = models.DateTimeField(auto_now_add=True)


# models.py


class OwnerProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    mess_name = models.CharField(max_length=255)
    mess_location = models.CharField(max_length=255)

    def __str__(self):
        return f"{self.user.username} - {self.mess_name}"





class Cart(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    item = models.ForeignKey(MenuItem, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f"{self.quantity} x {self.item.name} for {self.user.username}"

    def get_total_price(self):
        return self.quantity * self.item.price



# class Order(models.Model):
#     user = models.ForeignKey(User, on_delete=models.CASCADE)
#     mess = models.ForeignKey(Mess, on_delete=models.CASCADE)
#     items = models.ManyToManyField(MenuItem)
#     total_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)

#     # NEW FIELDS
#     customer_name = models.CharField(max_length=200, default="Guest User")
#     phone = models.CharField(max_length=15, null=True, blank=True)  # 📱 added phone
#     address = models.CharField(max_length=255, null=True, blank=True)
#     pincode = models.CharField(max_length=10, null=True, blank=True)

#     payment_status = models.CharField(max_length=20, choices=[
#         ('Pending', 'Pending'),
#         ('Paid', 'Paid'),
#         ('Failed', 'Failed'),
#     ], default='Pending')

#     status = models.CharField(max_length=20, choices=[
#         ('Pending', 'Pending'),
#         ('Accepted', 'Accepted'),
#         ('Rejected', 'Rejected'),
#         ('Delivered', 'Delivered')
#     ], default='Pending')

#     created_at = models.DateTimeField(auto_now_add=True)

#     def __str__(self):
#         return f"Order {self.id} - {self.user.username}"

from django.db import models
from django.contrib.auth.models import User

class Order(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    mess = models.ForeignKey("Mess", on_delete=models.CASCADE)  # Link to the mess where order is placed
    items = models.ManyToManyField("MenuItem")  # All menu items in the order
    total_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    # Customer Details
    customer_name = models.CharField(max_length=200, default="Guest User")
    phone = models.CharField(max_length=15, null=True, blank=True)  # 📱 Mobile number
    address = models.CharField(max_length=255, null=True, blank=True)
    pincode = models.CharField(max_length=10, null=True, blank=True)

    # Payment Info
    payment_method = models.CharField(
        max_length=50,
        choices=[
            ('COD', 'Cash on Delivery'),
            ('Online', 'Online Payment'),
        ],
        default='COD'
    )
    payment_status = models.CharField(
        max_length=20,
        choices=[
            ('Pending', 'Pending'),
            ('Paid', 'Paid'),
            ('Failed', 'Failed'),
        ],
        default='Pending'
    )

    # Order Tracking Status
    status = models.CharField(
        max_length=20,
        choices=[
            ('Pending', 'Pending'),
            ('Accepted', 'Accepted'),
            ('Preparing', 'Preparing'),
            ('Out for Delivery', 'Out for Delivery'),
            ('Delivered', 'Delivered'),
            ('Rejected', 'Rejected'),
        ],
        default='Pending'
    )

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Order {self.id} - {self.user.username}"

    def get_status_display_color(self):
        """Return bootstrap/tailwind color based on status for UI."""
        status_colors = {
            'Pending': 'yellow',
            'Accepted': 'blue',
            'Preparing': 'orange',
            'Out for Delivery': 'purple',
            'Delivered': 'green',
            'Rejected': 'red',
        }
        return status_colors.get(self.status, 'gray')
