from django.contrib import admin
from django.urls import path
from django.views.generic import TemplateView
from django.contrib.auth.views import LogoutView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', TemplateView.as_view(template_name='home.html'), name='home'),
    path('login/', TemplateView.as_view(template_name='accounts/login.html'), name='login'),
    path('register/', TemplateView.as_view(template_name='accounts/register.html'), name='register'),
    path('forgot-password/', TemplateView.as_view(template_name='accounts/forgot-password.html'), name='forgot_password'),
    path('about/', TemplateView.as_view(template_name='about.html'), name='about'),
    path('consultation/', TemplateView.as_view(template_name='consultation.html'), name='consultation'),
    path('shop/', TemplateView.as_view(template_name='shop.html'), name='shop'),
    path('contact/', TemplateView.as_view(template_name='contact.html'), name='contact'),
    path('logout/', LogoutView.as_view(), name='logout'),
]
