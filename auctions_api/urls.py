from django.urls import path
from rest_framework import routers
from django.conf.urls import include
from . import views

router = routers.DefaultRouter()
router.register('listings',views.ListingsEndPoint)



urlpatterns = [
    path("", include(router.urls))
]