from django.shortcuts import render, redirect,get_object_or_404
from django.views import View
from django.contrib.auth.models import User
from django.contrib import messages
from store_app.models import UserProfile,Product,ProductImage
from django.http import HttpResponse
from store_app.forms import ProductForm
from django.contrib.auth import authenticate,login,logout

class RegisterView(View):
    def get(self, request):
        return render(request, "register.html")
    
    def post(self, request):
        username = request.POST.get("username").strip()
        email = request.POST.get("email").strip()
        password = request.POST.get("password")
        confirm_password = request.POST.get("confirm_password")

        if password != confirm_password:
            messages.error(request, "Passwords do not match")
            return redirect("register")

        if User.objects.filter(email=email).exists():
            messages.error(request, "Email already registered")
            return redirect("register")

        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already taken")
            return redirect("register")

        # ✅ Create normal user
        user = User.objects.create_user(username=username, password=password, email=email)

        # ✅ Automatically create profile as CUSTOMER
        UserProfile.objects.create(user=user, user_type="customer")

        messages.success(request, "Account created successfully!")
        return redirect("register")

class LoginView(View):
    def get(self,request):
        return render(request,"login.html")
    def post(self,request):
        username=request.POST.get("username")
        password=request.POST.get("password")
        
        user=authenticate(request,username=username,password=password)
        
        if user is None:
            messages.error(request,"Invalid Username or Password")
            return redirect("login")
        
        login(request,user)
        
        profile=UserProfile.objects.get(user=user)
        
        if profile.user_type=='customer':
            return HttpResponse("customer_home")
        else:
            return redirect("staff_home")
        
class StaffHomeView(View):
    def get(self,request):
        # Check if user is logged in
        if not request.user.is_authenticated:
            return redirect('login')

        # Check if user has profile and is staff
        user_profile = getattr(request.user, 'userprofile', None)
        if not user_profile or user_profile.user_type != 'staff':
            messages.error(request, "You don't have permission to access this page.")
            return redirect('login')
        return render(request,"staff_home.html")

class AddProductView(View):
    def get(self, request):
        # Check if user is logged in
        if not request.user.is_authenticated:
            return redirect('login')

        # Check if user has profile and is staff
        user_profile = getattr(request.user, 'userprofile', None)
        if not user_profile or user_profile.user_type != 'staff':
            messages.error(request, "You don't have permission to access this page.")
            return redirect('login')

        # If allowed, render the add product page
        return render(request, 'add_product.html')
    
    def post(self,request):
        if not request.user.is_authenticated:
            return redirect('login')
        
        name = request.POST.get("name")
        category = request.POST.get("category")
        price = request.POST.get("price")
        description = request.POST.get("description")
        cover_image = request.FILES.get("cover_image")
        gallery_images = request.FILES.getlist("gallery_images")
        
        if not name or not category or not price or not cover_image:
            messages.error(request, "Please fill all required fields.")
            return redirect("add_product")
        
        product = Product.objects.create(
            name=name,
            category=category,
            price=price,
            description=description,
            cover_image=cover_image
        )
        
        for img in gallery_images:
            ProductImage.objects.create(product=product, image=img)
        
        messages.success(request, f"✅ Product '{name}' added successfully!")
        return redirect("add_product")

class ManageProductView(View):
    def get(self,request):
        # 1️⃣ Check if user is logged in
        if not request.user.is_authenticated:
            return redirect('login')

        # 2️⃣ Check if user is staff
        user_profile = getattr(request.user, 'userprofile', None)
        if not user_profile or user_profile.user_type != 'staff':
            messages.error(request, "You don't have permission to access this page.")
            return redirect('login')
        
        products=Product.objects.all().order_by("-created_at")
        return render(request,"manage_products.html",{'products': products})

class ProductEditView(View):
    def get(self, request, *args, **kwargs):
        product = get_object_or_404(Product, id=kwargs.get("id"))
        form = ProductForm(instance=product)
        images = ProductImage.objects.filter(product=product)
        return render(request, "edit_product.html", {"form": form, "product": product, "images": images})

    def post(self, request, *args, **kwargs):
        product = get_object_or_404(Product, id=kwargs.get("id"))
        form = ProductForm(request.POST, request.FILES, instance=product)

        if form.is_valid():
            form.save()

            # Handle gallery images
            gallery_images = request.FILES.getlist("gallery_images")
            for img in gallery_images:
                ProductImage.objects.create(product=product, image=img)

            messages.success(request, f"✅ Product '{product.name}' updated successfully!")
            return redirect("manage_products")

        # If invalid, re-render form with errors
        images = ProductImage.objects.filter(product=product)
        return render(request, "edit_product.html", {"form": form, "product": product, "images": images})

class DeleteProductImageView(View):
    def get(self, request, id):
        image = get_object_or_404(ProductImage, id=id)
        product_id = image.product.id
        image.delete()
        messages.success(request, "Image deleted successfully.")
        return redirect('edit_products', id=product_id)




class DeleteProductView(View):
    def get(self,request,*args, **kwargs):
        product=Product.objects.get(id=kwargs.get("id"))
        product.delete()
        messages.info(request,"Product Removed Successfully")
        return redirect("manage_products")
        