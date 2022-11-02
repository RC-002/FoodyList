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
from accounts import views as accountViews
#file imports
from . import views

urlpatterns = [
    path('',accountViews.VendorDashboard, name='vendor'),
    path('profile/', views.vProfile, name="vProfile"),
    path('menu-builder', views.menu_builder, name='menu_builder'),
    path('menu-builder/category/<int:pk>/', views.foodItems_by_category, name='foodItems_by_category'),

    #CRUD
    path('menu-builder/category/add/', views.add_category, name="add_category"),
    path('menu-builder/category/edit/<int:pk>/', views.edit_category, name="edit_category"),
    path('menu-builder/category/delete/<int:pk>/', views.delete_category, name="delete_category"),
]
