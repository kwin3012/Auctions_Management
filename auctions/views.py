from django.shortcuts import render
from django.http import HttpResponse


def index(request):
    return HttpResponse("Ready to Start!")

# Create your views here.
