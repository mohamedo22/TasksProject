from django.shortcuts import render , redirect
from .models import *
from datetime import *
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth import login as auth_login
# Create your views here.
def login(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        check = "false"
        try:
            user = UserProfile.objects.get(email=email, password=password)
            if user:
                auth_login(request, user)
                send_mail("login Successfully", "There is a new login to your account in 'Sewedy PHP Tasks app'",
                          settings.EMAIL_HOST_USER, [email], fail_silently=False)
                return
        except UserProfile.DoesNotExist:
            try:
                superAdmin = SuperAdmin.objects.get(email=email,password=password)
                if superAdmin:
                    auth_login(request, superAdmin)
                    send_mail("login Successfully", "There is a new login to your account in 'Sewedy PHP Tasks app'",
                              settings.EMAIL_HOST_USER, [email], fail_silently=False)
                    return
            except SuperAdmin.DoesNotExist:
                return render(request, 'LoginPage.html', {'check': check})
    return render(request, 'LoginPage.html')