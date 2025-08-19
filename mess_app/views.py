

from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from .models import OwnerProfile
from django.contrib.auth.decorators import login_required
from .models import Mess, MenuItem, OwnerProfile
from .forms import MessForm, MenuItemForm
from django.shortcuts import render, redirect, get_object_or_404
import json 
from .models import Order
from django.http import JsonResponse
from .models import Cart

def home(request):
    return render(request, 'home.html')



def register_user_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        email = request.POST['email']
        password1 = request.POST['password1']
        password2 = request.POST['password2']

        if password1 != password2:
            return render(request, 'register.html', {'error': 'Passwords do not match'})

        if User.objects.filter(username=username).exists():
            return render(request, 'register.html', {'error': 'Username already exists'})

        user = User.objects.create_user(username=username, email=email, password=password1)
        user.save()
        messages.success(request, 'Registration successful! Please login.')
        return redirect('login')

    return render(request, 'register.html')




def register_owner_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        mess_name = request.POST.get('mess_name')
        location = request.POST.get('location')
        password1 = request.POST.get('password1')
        password2 = request.POST.get('password2')

        if password1 != password2:
            messages.error(request, 'Passwords do not match.')
            return redirect('register_owner')

        if User.objects.filter(username=username).exists():
            messages.error(request, 'Owner name already taken.')
            return redirect('register_owner')

        if User.objects.filter(email=email).exists():
            messages.error(request, 'Email already in use.')
            return redirect('register_owner')

        user = User.objects.create_user(username=username, password=password1, email=email)

        # ✅ Create Owner Profile
        OwnerProfile.objects.create(user=user, mess_name=mess_name, mess_location=location)

        # ✅ Auto login and go to dashboard
        login(request, user)
        return redirect('owner_dashboard')   # 🚀 go directly to dashboard
    return render(request, 'register_owner.html')



def user_login(request):
    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '').strip()

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)

            # agar mess owner hai
            if OwnerProfile.objects.filter(user=user).exists():
                return redirect('owner_dashboard')
            else:
                return redirect('mess_list')
        else:
            messages.error(request, "Invalid username or password")

    return render(request, 'registration/login.html')

    
def logout_view(request):
    logout(request)
    messages.success(request, 'Logged out successfully.')
    return redirect('user_login')


@login_required
def owner_dashboard_view(request):
    user = request.user
    messes = Mess.objects.filter(owner=user)

    # Blank forms for adding
    mess_form = MessForm()
    menu_form = MenuItemForm()

    if request.method == "POST":
        if "add_mess" in request.POST:
            form = MessForm(request.POST, request.FILES)
            if form.is_valid():
                mess = form.save(commit=False)
                mess.owner = user
                mess.save()
                messages.success(request, "Mess added successfully!")
                return redirect("owner_dashboard")

        elif "edit_mess" in request.POST:
            mess_id = request.POST.get("mess_id")
            mess = get_object_or_404(Mess, id=mess_id, owner=user)
            form = MessForm(request.POST, request.FILES, instance=mess)
            if form.is_valid():
                form.save()
                messages.success(request, "Mess updated successfully!")
                return redirect("owner_dashboard")

        elif "delete_mess" in request.POST:
            mess_id = request.POST.get("mess_id")
            mess = get_object_or_404(Mess, id=mess_id, owner=user)
            mess.delete()
            messages.success(request, "Mess deleted successfully!")
            return redirect("owner_dashboard")

        elif "add_menu" in request.POST:
            mess_id = request.POST.get("mess_id")
            mess = get_object_or_404(Mess, id=mess_id, owner=user)
            form = MenuItemForm(request.POST, request.FILES)
            if form.is_valid():
                item = form.save(commit=False)
                item.mess = mess
                item.save()
                messages.success(request, "Menu item added successfully!")
                return redirect("owner_dashboard")

        elif "edit_menu" in request.POST:
            item_id = request.POST.get("item_id")
            item = get_object_or_404(MenuItem, id=item_id, mess__owner=user)
            form = MenuItemForm(request.POST, request.FILES, instance=item)
            if form.is_valid():
                form.save()
                messages.success(request, "Menu item updated successfully!")
                return redirect("owner_dashboard")

        elif "delete_menu" in request.POST:
            item_id = request.POST.get("item_id")
            item = get_object_or_404(MenuItem, id=item_id, mess__owner=user)
            item.delete()
            messages.success(request, "Menu item deleted successfully!")
            return redirect("owner_dashboard")

    context = {
        "messes": messes,
        "mess_form": mess_form,  # for Add new mess
        "menu_form": menu_form,  # for Add new menu
    }
    return render(request, "owner/dashboard.html", context)



def mess_list_view(request):
    # Fetch all messes and prefetch their menus to avoid extra queries
    messes = Mess.objects.prefetch_related('menuitem_set').all()
    return render(request, 'user/mess_list.html', {'messes': messes})




@login_required
def user_profile_view(request):
    return render(request, "user/profile.html", {"user": request.user})


@login_required
def place_order(request, mess_id, item_id):
    mess = get_object_or_404(Mess, id=mess_id)
    item = get_object_or_404(MenuItem, id=item_id)

    # New order for single item (you can extend later for cart system)
    order = Order.objects.create(
        user=request.user,
        mess=mess,
        total_price=item.price
    )
    order.items.add(item)

    messages.success(request, f"✅ Order placed for {item.name} from {mess.name}")
    return redirect("mess_list")   # back to mess list

@login_required
def add_to_cart(request, item_id):
    cart = request.session.get('cart', [])
    if item_id not in cart:
        cart.append(item_id)
    request.session['cart'] = cart
    request.session.modified = True
    return JsonResponse({"message": "Item added", "cart": cart})

@login_required
def cart_view(request):
    cart = request.session.get('cart', [])
    items = MenuItem.objects.filter(id__in=cart)
    total_price = sum([item.price for item in items])
    return render(request, "user/cart.html", {"items": items, "total_price": total_price})

def order_success(request):
    return render(request, "user/order_success.html")

def checkout(request):
    cart_items = Cart.objects.filter(user=request.user)

    if not cart_items.exists():
        return redirect("cart")  # redirect to cart page instead of rendering cart.html

    if request.method == "POST":
        name = request.POST.get("name")
        address = request.POST.get("address")
        pincode = request.POST.get("pincode")
        payment_method = request.POST.get("payment_method")

        order = Order.objects.create(
            user=request.user,
            customer_name=name,
            address=address,
            pincode=pincode,
            payment_method=payment_method,
        )

        for item in cart_items:
            order.items.add(item.food_item)
        cart_items.delete()

        return redirect("order_success")  # ✅ go to success page

    return render(request, "user/checkout.html", {"cart_items": cart_items})
