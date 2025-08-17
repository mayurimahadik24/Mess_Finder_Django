

from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from .models import OwnerProfile
from django.contrib.auth.decorators import login_required
from .models import Mess, MenuItem, OwnerProfile
from .forms import MessForm, MenuItemForm
from django.shortcuts import render, redirect, get_object_or_404


def home(request):
    return render(request, 'home.html')


# def register_owner_view(request):
#     if request.method == 'POST':
#         username = request.POST.get('username')
#         email = request.POST.get('email')
#         mess_name = request.POST.get('mess_name')
#         location = request.POST.get('location')
#         password1 = request.POST.get('password1')
#         password2 = request.POST.get('password2')

#         # Debugging - see incoming data
#         print("Form received:", request.POST)

#         # Password match check
#         if password1 != password2:
#             messages.error(request, 'Passwords do not match.')
#             return redirect('register_owner')

#         # Username already exists
#         if User.objects.filter(username=username).exists():
#             messages.error(request, 'Owner name already taken.')
#             return redirect('register_owner')

#         # Email already exists
#         if User.objects.filter(email=email).exists():
#             messages.error(request, 'Email already in use.')
#             return redirect('register_owner')

#         # Create User
#         user = User.objects.create_user(username=username, password=password1, email=email)
#         print("User created:", user)

#         # Create Owner Profile
#         owner = OwnerProfile.objects.create(user=user, mess_name=mess_name, mess_location=location)
#         print("OwnerProfile created:", owner)

#         # Auto login the owner
#         login(request, user)

#         messages.success(request, 'Owner account created successfully! Please login.')
#         return redirect('login')  # change this if your login URL has a different name

#     return render(request, 'register_owner.html')



# @login_required
# def owner_dashboard_view(request):
#     try:
#         owner_profile = OwnerProfile.objects.get(user=request.user)
#     except ObjectDoesNotExist:
#         messages.error(request, "You are not authorized to access the owner dashboard.")
#         return redirect('home')  # or some error page

#     return render(request, 'owner/dashboard.html', {'owner': owner_profile})



# ---------------- Logout ----------------


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
                return redirect('home')
        else:
            messages.error(request, "Invalid username or password")

    return render(request, 'registration/login.html')

    
def logout_view(request):
    logout(request)
    messages.success(request, 'Logged out successfully.')
    return redirect('user_login')

# @login_required
# def owner_dashboard_view(request):
#     try:
#         owner_profile = OwnerProfile.objects.get(user=request.user)
#     except OwnerProfile.DoesNotExist:
#         messages.error(request, "You are not authorized to access the owner dashboard.")
#         return redirect("home")
#     return render(request, "owner/dashboard.html", {"owner": owner_profile})


# @login_required
# def owner_dashboard_view(request):
#     user = request.user  # logged-in user (owner)

#     # Get all messes belonging to this owner
#     messes = Mess.objects.filter(owner=user)

#     mess_form = MessForm()
#     menu_form = MenuItemForm()

#     # ✅ Handle POST actions
#     if request.method == "POST":
#         # ---------------------- Add Mess ----------------------
#         if "add_mess" in request.POST:
#             mess_form = MessForm(request.POST, request.FILES)
#             if mess_form.is_valid():
#                 mess = mess_form.save(commit=False)
#                 mess.owner = user
#                 mess.save()
#                 messages.success(request, "Mess added successfully!")
#                 return redirect("owner_dashboard")

#         # ---------------------- Edit Mess ----------------------
#         elif "edit_mess" in request.POST:
#             mess_id = request.POST.get("mess_id")
#             mess = get_object_or_404(Mess, id=mess_id, owner=user)
#             mess_form = MessForm(request.POST, request.FILES, instance=mess)
#             if mess_form.is_valid():
#                 mess_form.save()
#                 messages.success(request, "Mess updated successfully!")
#                 return redirect("owner_dashboard")

#         # ---------------------- Delete Mess ----------------------
#         elif "delete_mess" in request.POST:
#             mess_id = request.POST.get("mess_id")
#             mess = get_object_or_404(Mess, id=mess_id, owner=user)
#             mess.delete()
#             messages.success(request, "Mess deleted successfully!")
#             return redirect("owner_dashboard")

#         # ---------------------- Add Menu Item ----------------------
#         elif "add_menu" in request.POST:
#             mess_id = request.POST.get("mess_id")
#             mess = get_object_or_404(Mess, id=mess_id, owner=user)
#             menu_form = MenuItemForm(request.POST, request.FILES)
#             if menu_form.is_valid():
#                 item = menu_form.save(commit=False)
#                 item.mess = mess
#                 item.save()
#                 messages.success(request, "Menu item added successfully!")
#                 return redirect("owner_dashboard")

#         # ---------------------- Edit Menu Item ----------------------
#         elif "edit_menu" in request.POST:
#             item_id = request.POST.get("item_id")
#             item = get_object_or_404(MenuItem, id=item_id, mess__owner=user)
#             menu_form = MenuItemForm(request.POST, request.FILES, instance=item)
#             if menu_form.is_valid():
#                 menu_form.save()
#                 messages.success(request, "Menu item updated successfully!")
#                 return redirect("owner_dashboard")

#         # ---------------------- Delete Menu Item ----------------------
#         elif "delete_menu" in request.POST:
#             item_id = request.POST.get("item_id")
#             item = get_object_or_404(MenuItem, id=item_id, mess__owner=user)
#             item.delete()
#             messages.success(request, "Menu item deleted successfully!")
#             return redirect("owner_dashboard")

#     context = {
#         "messes": messes,
#         "mess_form": mess_form,
#         "menu_form": menu_form,
#     }
#     return render(request, "owner/dashboard.html", context)


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
