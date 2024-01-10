from django.urls import path, include
from rest_framework import routers

from . import views

app_name = 'study'

router = routers.DefaultRouter()
router.register('', views.StudyViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
