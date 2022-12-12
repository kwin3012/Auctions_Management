from django.urls import path
from auctions import views

urlpatterns = [
    path('',views.index,name="auctions_index"),
]