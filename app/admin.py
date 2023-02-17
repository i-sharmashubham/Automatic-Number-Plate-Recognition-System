from django.contrib import admin
from app.models import User,Challan,Transaction,Subscription
# Register your models here.

admin.site.register(User)
admin.site.register(Challan)
admin.site.register(Transaction)
admin.site.register(Subscription)