from django.shortcuts import render, redirect,get_object_or_404
from django.views import View
from django.contrib.auth.models import User
from django.contrib import messages
from store_app.models import UserProfile,Product,ProductImage,CartItem,Address,Order,OrderItem
from django.http import HttpResponse,HttpResponseBadRequest
from store_app.forms import ProductForm
from django.contrib.auth import authenticate,login,logout
from django.core.mail import send_mail
from django.conf import settings
import razorpay
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt


#-----------------------------------------------------Register and login---------------------------------------------------------------

class RegisterView(View):
    def get(self, request):
        return render(request, "register.html")

    def post(self, request):
        username = request.POST.get("username", "").strip()
        email = request.POST.get("email", "").strip()
        password = request.POST.get("password")
        confirm_password = request.POST.get("confirm_password")

        #  Validation
        if password != confirm_password:
            messages.error(request, "⚠️ Passwords do not match.")
            return render(request, "register.html")

        if User.objects.filter(email=email).exists():
            messages.error(request, "⚠️ This email is already registered.")
            return render(request, "register.html")

        if User.objects.filter(username=username).exists():
            messages.error(request, "⚠️ This username is already taken.")
            return render(request, "register.html")

        try:
            #  Create user
            user = User.objects.create_user(username=username, password=password, email=email)
            UserProfile.objects.create(user=user, user_type="customer")

            #  Send Welcome Email
            subject = "Welcome to Kiyafet – Where Elegance Begins"
            message = (
                f"Hi {username},\n\n"
                "Thank you for joining Kiyafet — your destination for timeless elegance and handcrafted fashion.\n"
                "We're thrilled to have you as part of our growing family.\n\n"
                "Explore our latest collections and discover outfits designed to bring out your confidence and grace.\n\n"
                "With love,\n"
                "Team Kiyafet 🤍"
            )
            from_email = settings.EMAIL_HOST_USER
            recipient_list = [email]

            try:
                send_mail(subject, message, from_email, recipient_list)
                messages.success(request, "✅ Account created successfully!")
            except Exception:
                messages.warning(request, "✅ Account created, but the welcome email could not be sent.")

            return redirect("login")

        except Exception as e:
            messages.error(request, f"⚠️ Something went wrong during registration: {e}")
            return render(request, "register.html")


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
            messages.success(request,"Logged In Succesfully")
            return redirect("home")
        else:
            return redirect("staff_home")

#---------------------------------------------Staff Home and Dashboard----------------------------------------------------------------
        
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
    
class StaffOrderListView(View):
    def get(self, request):
        # Check login + staff
        if not request.user.is_authenticated:
            return redirect("login")

        user_profile = getattr(request.user, "userprofile", None)
        if not user_profile or user_profile.user_type != "staff":
            return redirect("login")

        orders = Order.objects.all().order_by("-created_at")

        return render(request, "staff_orders_list.html", {"orders": orders})

class StaffOrderDetailView(View):
    def get(self, request, order_id):
        if not request.user.is_authenticated:
            return redirect("login")

        user_profile = getattr(request.user, "userprofile", None)
        if not user_profile or user_profile.user_type != "staff":
            return redirect("login")

        order = get_object_or_404(Order, id=order_id)
        items = OrderItem.objects.filter(order=order)

        return render(request, "staff_order_detail.html", {
            "order": order,
            "items": items
        })

class UpdateOrderView(View):
    def post(self, request, order_id):

        order = get_object_or_404(Order, id=order_id)

        order.status = request.POST.get("status")
        order.tracking_id = request.POST.get("tracking_id")
        order.courier_name = request.POST.get("courier_name")

        order.save()
        messages.success(request, "Order updated successfully!")

        return redirect("staff_orders")
    
class DeleteOrderView(View):
    def post(self, request, id):

        # Only staff can delete
        user_profile = getattr(request.user, "userprofile", None)
        if not user_profile or user_profile.user_type != "staff":
            messages.error(request, "Permission denied.")
            return redirect("staff_home")

        order = get_object_or_404(Order, id=id)

        # Only allow delete if payment failed or pending
        if order.payment_status.lower() not in ["pending", "failed"]:
            messages.error(request, "You cannot delete a paid order!")
            return redirect("manage_orders")

        order.delete()
        messages.success(request, f"Order #{id} deleted successfully.")

        return redirect("staff_orders")

#--------------------------------------------------------------Customer Product and Home---------------------------------------------------------------------
        
class CustomerHomePage(View):
    def get(self,request):
        featured_products = Product.objects.all().order_by('-id')[:3]   # latest 3
        new_arrivals = Product.objects.all().order_by('-created_at')[:8]  # latest 4

        context = {
            'featured_products': featured_products,
            'new_arrivals': new_arrivals,
        }
        return render(request, 'customer_home.html', context)
    
class ProductDetailView(View):
    def get(self,request,*args, **kwargs):
        product=Product.objects.get(id=kwargs.get("id"))
        related_products = Product.objects.filter(category=product.category).exclude(id=product.id)[:4]
        return render(request,"product_detail.html",{"product":product,"related_products":related_products})

#----------------------------------------------------------Add To Cart------------------------------------------------------------------------------

class AddToCartView(View):
    def post(self, request, **kwargs):
        if not request.user.is_authenticated:
            messages.warning(request, "Please login to add products to your cart.")
            return redirect('login')

        product = Product.objects.get(id=kwargs.get("id"))
        size = request.POST.get("size", "M")  # default M if not selected

        cart_item, created = CartItem.objects.get_or_create(
            user=request.user,
            product=product,
            size=size  # Include size when checking for duplicates
        )

        if not created:
            cart_item.quantity += 1
            cart_item.save()
            messages.success(request, f"Updated quantity for {product.name} ({size}).")
        else:
            messages.success(request, f"Added {product.name} ({size}) to your cart.")

        return redirect("product_detail_view", id=product.id)


class CartView(View):
    def get(self, request, **kwargs):
        # If user is not logged in, show a message + login button
        if not request.user.is_authenticated:
            context = {"not_logged_in": True}
            return render(request, "cart.html", context)

        # Get all cart items for the logged-in user
        cart_items = CartItem.objects.filter(user=request.user)

        # Calculate total price
        total = sum(item.product.price * item.quantity for item in cart_items)

        context = {
            "cart_items": cart_items,
            "total": total,
            "not_logged_in": False,
        }
        return render(request, "cart.html", context)

class IncreaseCartItemView(View):
    def get(self, request, id):
        item = CartItem.objects.get(id=id, user=request.user)
        item.quantity += 1
        item.save()
        return redirect('cart_view')


class DecreaseCartItemView(View):
    def get(self, request, id):
        item = CartItem.objects.get(id=id, user=request.user)
        if item.quantity > 1:
            item.quantity -= 1
            item.save()
        else:
            item.delete()
        return redirect('cart_view')


class RemoveCartItemView(View):
    def get(self, request, id):
        item = CartItem.objects.get(id=id, user=request.user)
        item.delete()
        messages.success(request, "Item removed from your cart.")
        return redirect('cart_view')

#----------------------------------------------------User Profile and Address -----------------------------------------------------------------------------------------

class ProfileView(View):
    def get(self, request):
        
        if not request.user.is_authenticated:
            return render(request, "login_required.html")
        
        profile = UserProfile.objects.get(user=request.user)
        addresses = Address.objects.filter(user=request.user)

        return render(request, "profile.html", {"profile": profile,"addresses": addresses})


class EditProfileView(View):
    def get(self, request):
        profile = request.user.userprofile
        return render(request, "edit_profile.html", {
            "profile": profile,
            "user": request.user,
        })

    def post(self, request):
        user = request.user
        profile = user.userprofile

        # Update User model fields
        user.first_name = request.POST.get("first_name")
        user.last_name = request.POST.get("last_name")
        user.email = request.POST.get("email")
        user.save()

        # Update UserProfile model fields
        profile.phone = request.POST.get("phone")
        profile.address = request.POST.get("address")
        profile.save()

        return redirect("profile")




class AddAddressView(View):
    def get(self, request):
        if not request.user.is_authenticated:
            return redirect("login")
        return render(request, "add_address.html")

    def post(self, request):
        if not request.user.is_authenticated:
            return redirect("login")

        Address.objects.create(
            user=request.user,
            full_name=request.POST.get("full_name"),
            phone=request.POST.get("phone"),
            house=request.POST.get("house"),
            street=request.POST.get("street"),
            city=request.POST.get("city"),
            state=request.POST.get("state"),
            pincode=request.POST.get("pincode"),
            country=request.POST.get("country") or "India",
        )

        messages.success(request, "Address added successfully!")
        return redirect("profile")

class EditAddressView(View):
    def get(self, request, id):
        if not request.user.is_authenticated:
            return redirect("login")

        address = get_object_or_404(Address, id=id, user=request.user)
        return render(request, "edit_address.html", {"address": address})

    def post(self, request, id):
        if not request.user.is_authenticated:
            return redirect("login")

        address = get_object_or_404(Address, id=id, user=request.user)

        address.full_name = request.POST.get("full_name")
        address.phone = request.POST.get("phone")
        address.house = request.POST.get("house")
        address.street = request.POST.get("street")
        address.city = request.POST.get("city")
        address.state = request.POST.get("state")
        address.pincode = request.POST.get("pincode")
        address.country = request.POST.get("country") or "India"
        address.save()

        messages.success(request, "Address updated successfully!")
        return redirect("profile")

class DeleteAddressView(View):
    def get(self, request, id):
        address = get_object_or_404(Address, id=id, user=request.user)
        address.delete()
        messages.success(request, "Address deleted successfully!")
        return redirect("profile")


#-----------------------------------------------------------Check Out and Payment------------------------------------------------------------------------------------------

class CheckoutView(View):
    def get(self, request):
        if not request.user.is_authenticated:
            messages.warning(request, "Please login to continue checkout.")
            return redirect("login")

        cart_items = CartItem.objects.filter(user=request.user)

        if not cart_items.exists():
            messages.warning(request, "Your cart is empty.")
            return redirect("cart_view")

        addresses = Address.objects.filter(user=request.user)
        total = sum(item.product.price * item.quantity for item in cart_items)

        return render(request, "checkout.html", {
            "cart_items": cart_items,
            "addresses": addresses,
            "total": total
        })

class StartPaymentView(View):
    def post(self, request):
        address_id = request.POST.get("address")
        amount = float(request.POST.get("amount"))

        # Validate address belongs to user
        try:
            address = Address.objects.get(id=address_id, user=request.user)
        except Address.DoesNotExist:
            messages.error(request, "Address not found or not allowed.")
            return redirect("checkout_view")

        # Get the user's cart
        cart_items = CartItem.objects.filter(user=request.user)

        if not cart_items.exists():
            messages.error(request, "Your cart is empty.")
            return redirect("cart_view")

        total = sum(item.product.price * item.quantity for item in cart_items)

        # Create Order
        order = Order.objects.create(
            user=request.user,
            address=address,
            full_name=address.full_name,
            phone=address.phone,
            total_amount=total,
            payment_status="Pending",
        )

        # Create Order Items
        for item in cart_items:
            OrderItem.objects.create(
                order=order,
                product=item.product,
                size=item.size,
                quantity=item.quantity,
                price=item.product.price,
            )

        # redirect to razorpay:
        return redirect("razorpay_pay", order_id=order.id)

class RazorpayPayView(View):
    def get(self, request, order_id):
        order = Order.objects.get(id=order_id)

        # Razorpay client
        client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))

        payment = client.order.create({
            "amount": int(order.total_amount * 100),  # convert to paisa
            "currency": "INR",
            "payment_capture": 1
        })

        order.payment_id = payment["id"]
        order.save()

        return render(request, "razorpay_payment.html", {
            "order": order,
            "payment": payment,
            "razorpay_key": settings.RAZORPAY_KEY_ID,
        })

@method_decorator(csrf_exempt, name='dispatch')
class PaymentConfirmView(View):
    def post(self, request, *args, **kwargs):

        # Razorpay response fields
        razorpay_payment_id = request.POST.get('razorpay_payment_id')
        razorpay_order_id = request.POST.get('razorpay_order_id')
        razorpay_signature = request.POST.get('razorpay_signature')

        order_id = request.GET.get("order_id")

        if not (razorpay_payment_id and razorpay_order_id and razorpay_signature):
            return HttpResponseBadRequest("Payment verification failed.")

        # Find your order
        try:
            order = Order.objects.get(id=order_id, user=request.user)
        except Order.DoesNotExist:
            messages.error(request, "Order not found.")
            return redirect("cart_view")

        # Razorpay client for verification
        client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))

        # Verify payment signature
        try:
            client.utility.verify_payment_signature({
                'razorpay_order_id': razorpay_order_id,
                'razorpay_payment_id': razorpay_payment_id,
                'razorpay_signature': razorpay_signature
            })
        except:
            messages.error(request, "Payment verification failed.")
            return redirect("cart_view")

        # SUCCESS → Update order
        order.payment_status = "Paid"
        order.payment_id = razorpay_payment_id
        order.status = "confirmed"
        order.save()

        # Clear cart after payment
        CartItem.objects.filter(user=request.user).delete()

        return render(request, "payment_success.html", {"order": order})

    # Razorpay sometimes sends GET request — handle safely
    def get(self, request):
        return redirect("home")

#--------------------------------------------------User Order Page----------------------------------------------------------------------------------

class OrdersListView(View):
    def get(self, request):
        if not request.user.is_authenticated:
            return render(request,"login_required.html")
        
        orders = Order.objects.filter(user=request.user).order_by("-created_at")
        return render(request, "orders_list.html", {"orders": orders})

class OrderDetailView(View):
    def get(self, request, order_id):
        # Validate order belongs to the logged-in user
        order = get_object_or_404(Order, id=order_id, user=request.user)

        order_items = order.orderitem_set.all()

        return render(request, "order_detail.html", {
            "order": order,
            "items": order_items,
        })

class LogoutView(View):
    def get(self,request):
        logout(request)
        messages.success(request,"Logged Out Succesfully")
        return redirect("home")