from django.contrib import admin

from .models import *
from .models import Video

admin.site.register(Customer)
admin.site.register(Product)
admin.site.register(Order)
admin.site.register(OrderItem)
admin.site.register(ShippingAddress)

class VideoAdmin(admin.ModelAdmin):
    list_display = ('title', 'description')
