"""foodyList URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.urls import path, include

#file imports
from . import views

urlpatterns = [
    path('registerUser/', views.registerUser, name="registerUser"),
    path('registerVendor/', views.registerVendor, name="registerVendor"),
    path('login/', views.login, name="login"),
    path('logout/', views.logout, name="logout"),
    path('myAccount/', views.myAccount, name="myAccount"),
    path('customerDashboard/', views.customerDashboard, name="customerDashboard"),
    path('VendorDashboard/', views.VendorDashboard, name="VendorDashboard"),
    path('activate/<uidb64>/<token>/', views.activate, name = 'activate'),
    path('forgot_password/', views.forgot_password, name = 'forgot_password'),
    path('reset_password_validate/<uidb64>/<token>/', views.reset_password_validate, name = 'reset_password_validate'),
    path('reset_password/', views.reset_password, name = 'reset_password'),
]
