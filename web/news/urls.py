from django.urls import path
from .views import index

app_name = "reestr"

urlpatterns:list = [
    path('', index, name="index"),
]