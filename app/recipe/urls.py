"""
URL Mapping for Recipe APIs.
"""
from django.urls import path, include
from rest_framework import routers

from recipe import views

router = routers.DefaultRouter()
router.register(r'recipes', views.RecipeViewSet)

app_name = 'recipe'

urlpatterns = [
    path('', include(router.urls)),
]
