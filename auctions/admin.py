from django.contrib import admin

# Register your models here.
from auctions.models import *
admin.site.register(User)
admin.site.register(listings)
admin.site.register(categories)
