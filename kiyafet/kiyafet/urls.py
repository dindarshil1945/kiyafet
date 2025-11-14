"""
URL configuration for kiyafet project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
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
from django.contrib import admin
from django.urls import path
from store_app import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('register', views.RegisterView.as_view(),name="register"),
    path('login', views.LoginView.as_view(),name="login"),
    path('staff/Dashboard', views.StaffHomeView.as_view(),name="staff_home"),
    path('staff/product/add', views.AddProductView.as_view(),name="add_product"),
    path('staff/product/manage', views.ManageProductView.as_view(),name="manage_products"),
    path('staff/product/delete/<int:id>', views.DeleteProductView.as_view(),name="delete_products"),
    path('staff/product/edit/<int:id>', views.ProductEditView.as_view(),name="edit_products"),
    path('staff/product/image/delete/<int:id>/', views.DeleteProductImageView.as_view(), name='delete_product_image'),
    path('', views.CustomerHomePage.as_view(), name='home'),
    path('product/view/<int:id>', views.ProductDetailView.as_view(), name='product_detail_view'),
    path('cart/add/<int:id>',views.AddToCartView.as_view(), name='add_to_cart'),
    path("cart/view", views.CartView.as_view(), name="cart_view"),
    path('cart/increase/<int:id>/', views.IncreaseCartItemView.as_view(), name='increase_cart_item'),
    path('cart/decrease/<int:id>/', views.DecreaseCartItemView.as_view(), name='decrease_cart_item'),
    path('cart/remove/<int:id>/', views.RemoveCartItemView.as_view(), name='remove_cart_item'),
    path("profile/", views.ProfileView.as_view(), name="profile"),
    path("profile/edit/", views.EditProfileView.as_view(), name="edit_profile"),
    path("address/add/", views.AddAddressView.as_view(), name="add_address"),
    path("address/edit/<int:id>/", views.EditAddressView.as_view(), name="edit_address"),
    path("address/delete/<int:id>/", views.DeleteAddressView.as_view(), name="delete_address"),
    path('logout', views.LogoutView.as_view(), name='logout'),
]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
