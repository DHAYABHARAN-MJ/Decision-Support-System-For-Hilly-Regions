from django.urls import path, include
from django.views.generic import TemplateView

urlpatterns = [
    path('', TemplateView.as_view(template_name='dss/dashboard.html'), name='dashboard'),
    path('assess/', TemplateView.as_view(template_name='dss/index.html'), name='assess'),
    path('api/dss/', include('dss.urls')),
]
