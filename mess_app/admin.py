# from django.contrib import admin

# # Register your models here.
from django.contrib import admin
from .models import Mess, MenuItem, MessBooking, Order

admin.site.register(Mess)
admin.site.register(MenuItem)
admin.site.register(MessBooking)
admin.site.register(Order)
