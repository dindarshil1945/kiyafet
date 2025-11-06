from django.shortcuts import render, redirect
from django.views import View
from django.contrib.auth.models import User
from django.contrib import messages
from store_app.models import UserProfile
from django.http import HttpResponse
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
            return redirect(login)
        
        login(request,user)
        
        profile=UserProfile.objects.get(user=user)
        
        if profile.user_type=='customer':
            return HttpResponse("customer_homr")