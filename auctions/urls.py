from django.urls import path
from auctions import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("create", views.create, name="create"),
    path("<int:product_id>", views.listing_profile, name="listing_profile"),
    path("place_bid/<int:product_id>", views.place_bid, name="place_bid"),
    path("close", views.close, name="close"),
]