from django.urls import path

from .views import CompareView, HealthView, WebCheckView

urlpatterns = [
    path('health/', HealthView.as_view()),
    path('compare/', CompareView.as_view()),
    path('check-web/', WebCheckView.as_view()),
]
