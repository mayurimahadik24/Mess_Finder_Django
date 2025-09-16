

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
from django.views.generic import TemplateView

from django.core.mail import send_mail
from django.conf import settings


def home(request):
    return render(request, 'home.html')


class AboutView(TemplateView):
    template_name = "common/about_us.html"

    
class ContactView(TemplateView):
    template_name = "common/contact.html"

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




# def mess_list_view(request):
#     messes = Mess.objects.prefetch_related('menuitem_set').all()

#     location = request.GET.get('location')
#     pincode = request.GET.get('pincode')
#     food_type = request.GET.get('food_type')
#     price = request.GET.get('price')
#     menu_search = request.GET.get('menu')

#     if location:
#         messes = messes.filter(location__icontains=location)
#     if pincode:
#         messes = messes.filter(pincode__icontains=pincode)
#     if food_type:
#         messes = messes.filter(food_type__iexact=food_type)
#     if price:
#         messes = messes.filter(menuitem_set__price__lte=price)
#     if menu_search:
#         messes = messes.filter(menuitem_set__name__icontains=menu_search)

#     cart_items = Cart.objects.filter(user=request.user) if request.user.is_authenticated else []
#     cart_count = cart_items.count()
#     cart_total = sum(item.get_total_price() for item in cart_items)

#     return render(request, 'user/mess_list.html', {
#         'messes': messes.distinct(),
#         'cart_count': cart_count,
#         'cart_total': cart_total
#     })

def mess_list_view(request):
    # prefetch_related uses the default reverse name 'menuitem_set'
    messes = Mess.objects.prefetch_related('menuitem_set').all()

    location = request.GET.get('location')
    pincode = request.GET.get('pincode')
    food_type = request.GET.get('food_type')
    price = request.GET.get('price')
    menu_search = request.GET.get('menu')

    if location:
        messes = messes.filter(location__icontains=location)
    if pincode:
        messes = messes.filter(pincode__icontains=pincode)
    if food_type:
        messes = messes.filter(food_type__iexact=food_type)
    if price:
        messes = messes.filter(menuitem__price__lte=price)
    if menu_search:
        messes = messes.filter(menuitem__name__icontains=menu_search)

    cart_items = Cart.objects.filter(user=request.user) if request.user.is_authenticated else []
    cart_count = cart_items.count()
    cart_total = sum(item.get_total_price() for item in cart_items)

    return render(request, 'user/mess_list.html', {
        'messes': messes.distinct(),
        'cart_count': cart_count,
        'cart_total': cart_total
    })


# @login_required
# def user_profile_view(request):
#     # Fetch all orders for the logged-in user
#     orders = Order.objects.filter(user=request.user).order_by("-created_at")

#     # Separate current and past orders
#     current_orders = orders.exclude(status__in=["Delivered", "Rejected"])
#     order_history = orders.filter(status__in=["Delivered", "Rejected"])

#     return render(request, "user/profile.html", {
#         "user": request.user,
#         "current_orders": current_orders,
#         "order_history": order_history
#     })
@login_required
def user_profile_view(request):
    current_orders = Order.objects.filter(user=request.user).exclude(status="Delivered").order_by("-created_at")
    past_orders = Order.objects.filter(user=request.user, status="Delivered").order_by("-created_at")
    return render(request, "user/profile.html", {
        "user": request.user,
        "current_orders": current_orders,
        "past_orders": past_orders
    })


@login_required
def delete_order_history(request, order_id):
    """Delete an order from history (only if delivered or rejected)"""
    order = get_object_or_404(Order, id=order_id, user=request.user)

    if order.status in ["Delivered", "Rejected"]:
        order.delete()
        messages.success(request, "Order history deleted successfully.")
    else:
        messages.error(request, "You can only delete completed or rejected orders.")

    return redirect("user_profile")

# @login_required
# def place_order(request, mess_id, item_id):
#     mess = get_object_or_404(Mess, id=mess_id)
#     item = get_object_or_404(MenuItem, id=item_id)

#     # New order for single item (you can extend later for cart system)
#     order = Order.objects.create(
#         user=request.user,
#         mess=mess,
#         total_price=item.price
#     )
#     order.items.add(item)

#     messages.success(request, f"✅ Order placed for {item.name} from {mess.name}")
#     return redirect("mess_list")   # back to mess list

# @login_required
# def add_to_cart(request, item_id):
#     cart = request.session.get('cart', [])
#     if item_id not in cart:
#         cart.append(item_id)
#     request.session['cart'] = cart
#     request.session.modified = True
#     return JsonResponse({"message": "Item added", "cart": cart})

# @login_required
# def cart_view(request):
#     cart = request.session.get('cart', [])
#     items = MenuItem.objects.filter(id__in=cart)
#     total_price = sum([item.price for item in items])
#     return render(request, "user/cart.html", {"items": items, "total_price": total_price})

# def order_success(request):
#     return render(request, "user/order_success.html")

# def checkout(request):
#     cart_items = Cart.objects.filter(user=request.user)

#     if not cart_items.exists():
#         return redirect("cart")  # redirect to cart page instead of rendering cart.html

#     if request.method == "POST":
#         name = request.POST.get("name")
#         address = request.POST.get("address")
#         pincode = request.POST.get("pincode")
#         payment_method = request.POST.get("payment_method")

#         order = Order.objects.create(
#             user=request.user,
#             customer_name=name,
#             address=address,
#             pincode=pincode,
#             payment_method=payment_method,
#         )

#         for item in cart_items:
#             order.items.add(item.food_item)
#         cart_items.delete()

#         return redirect("order_success")  # ✅ go to success page

#     return render(request, "user/checkout.html", {"cart_items": cart_items})


@login_required
def place_order(request):
    cart = request.session.get('cart', {})
    
    if not cart:
        messages.error(request, "Your cart is empty.")
        return redirect('messes')

    # Create order in DB
    order = Order.objects.create(user=request.user, total_price=calculate_total(cart))
    for item_id, quantity in cart.items():
        menu_item = MenuItem.objects.get(id=item_id)
        OrderItem.objects.create(order=order, menu_item=menu_item, quantity=quantity)
    
    # ✅ Clear the cart
    request.session['cart'] = {}
    request.session.modified = True

    messages.success(request, "Your order has been placed successfully!")
    return redirect('order_confirmation')  # or wherever you want


@login_required
def add_to_cart(request, item_id):
    item = get_object_or_404(MenuItem, id=item_id)

    # Check if this item is already in the user's cart
    cart_item, created = Cart.objects.get_or_create(
        user=request.user,
        item=item
    )

    if not created:
        # If item already exists in cart, increase quantity
        cart_item.quantity += 1
        cart_item.save()

    return JsonResponse({
        "message": f"{item.name} added to cart",
        "quantity": cart_item.quantity
    })


@login_required
def cart_view(request):
    cart_items = Cart.objects.filter(user=request.user)
    total_price = sum(item.get_total_price() for item in cart_items)  # ✅ uses model method
    return render(request, "user/cart.html", {
        "cart_items": cart_items,
        "total_price": total_price
    })



@login_required
def delete_cart_item(request, item_id):
    cart_item = get_object_or_404(Cart, id=item_id, user=request.user)
    cart_item.delete()
    return redirect('cart')


def order_success(request):
    return render(request, "user/order_success.html")


# @login_required
# def checkout(request):
#     cart_items = Cart.objects.filter(user=request.user)

#     if not cart_items.exists():
#         messages.warning(request, "Your cart is empty.")
#         return redirect("cart")

#     total_price = sum(item.get_total_price() for item in cart_items)

#     if request.method == "POST":
#         name = request.POST.get("name")
#         address = request.POST.get("address")
#         pincode = request.POST.get("pincode")
#         payment_method = request.POST.get("payment_method")

#         order = Order.objects.create(
#             user=request.user,
#             customer_name=name,
#             address=address,
#             pincode=pincode,
#             payment_method=payment_method,
#             total_price=total_price
#         )

#         for cart_item in cart_items:
#             order.items.add(cart_item.item)

#         cart_items.delete()

#         return redirect("order_success")

#     return render(
#         request,
#         "user/checkout.html",
#         {
#             "cart_items": cart_items,
#             "total_price": total_price
#         }
#     )


@login_required
def checkout(request):
    cart_items = Cart.objects.filter(user=request.user)

    if not cart_items.exists():
        messages.warning(request, "Your cart is empty.")
        return redirect("cart")

    total_price = sum(item.get_total_price() for item in cart_items)

    if request.method == "POST":
        name = request.POST.get("name")
        phone = request.POST.get("phone")
        address = request.POST.get("address")
        pincode = request.POST.get("pincode")
        payment_method = request.POST.get("payment_method")

        mess = cart_items.first().item.mess  

        order = Order.objects.create(
            user=request.user,
            mess=mess,
            customer_name=name,
            phone=phone,
            address=address,
            pincode=pincode,
            total_price=total_price,
            payment_status="Pending",
            status="Pending"
        )

        for cart_item in cart_items:
            order.items.add(cart_item.item)

        cart_items.delete()

        # Send emails (optional)...

        messages.success(request, "Your order has been placed successfully!")
        return redirect("order_success", order_id=order.id)

    return render(request, "user/checkout.html", {
        "cart_items": cart_items,
        "total_price": total_price
    })


# @login_required
# def owner_orders(request):
#     owner_profile = OwnerProfile.objects.get(user=request.user)
#     mess = owner_profile.mess
#     orders = mess.orders.all().order_by("-created_at")  # ✅ all orders for this mess
#     return render(request, "owner/orders.html", {"orders": orders})


@login_required
def owner_orders_view(request):
    messes = Mess.objects.filter(owner=request.user)  # can be 1 or many
    orders = Order.objects.filter(mess__in=messes).order_by('-created_at')
    return render(request, 'owner/owner_orders.html', {'orders': orders})


def order_success(request, order_id):
    order = Order.objects.get(id=order_id)
    return render(request, "user/order.html", {"order": order})


def update_order_status(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    new_status = request.POST.get('status')
    if new_status:
        order.status = new_status
        order.save()
    return redirect('owner_orders') 



def delete_order(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    order.delete()
    messages.success(request, "Order deleted successfully.")
    return redirect('owner_orders')

