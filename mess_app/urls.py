# from django.urls import path
# from . import views

# urlpatterns = [
#     path('', views.home, name='home'),
#     path('messes/', views.mess_list, name='mess_list'),
#     path('messes/<int:id>/', views.mess_detail, name='mess_detail'),
#     path('book/<int:mess_id>/', views.book_mess, name='book_mess'),
#     path('order/<int:mess_id>/', views.place_order, name='place_order'),
#     path('myorders/', views.user_orders, name='user_orders'),
#     path('owner/dashboard/', views.owner_dashboard, name='owner_dashboard'),
#     path('owner/bookings/', views.owner_bookings, name='owner_bookings'),
#     path('owner/orders/', views.owner_orders, name='owner_orders'),
# ]


# mess_app/urls.py
from django.urls import path
from . import views
from django.contrib.auth import views as auth_views


urlpatterns = [
    path('', views.home, name='home'),
    path('login/', views.user_login, name='user_login'),
    path('register/', views.register_user_view, name='register'),
    path('register-owner/', views.register_owner_view, name='register_owner'),
    path('dashboard/', views.owner_dashboard_view, name='owner_dashboard'), 
    path('messes/', views.mess_list_view, name='mess_list'),
    path("profile/", views.user_profile_view, name="user_profile"),
    path("order/<int:mess_id>/<int:item_id>/", views.place_order, name="place_order"),
    path("checkout/", views.checkout, name="checkout"),
    path('cart/', views.cart_view, name='cart'),
    path('add-to-cart/<int:item_id>/', views.add_to_cart, name='add_to_cart'),
    path("order-success/", views.order_success, name="order_success"),


    #  path('edit-mess/<int:mess_id>/', views.edit_mess, name='edit_mess'),
    # path('add-menu/<int:mess_id>/', views.add_menu_item, name='add_menu_item'),
    # path('edit-menu/<int:item_id>/', views.edit_menu_item, name='edit_menu_item'),

    # # ✅ New Delete URLs
    # path('delete-mess/<int:mess_id>/', views.delete_mess, name='delete_mess'),
    # path('delete-menu/<int:item_id>/', views.delete_menu_item, name='delete_menu'),
]
