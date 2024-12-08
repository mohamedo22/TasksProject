from django.contrib.auth.decorators import login_required
from django.shortcuts import render , redirect
from .models import *
from datetime import *
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth import login as auth_login
# Create your views here.
def redirect_user_based_on_role(user):
    if user.is_superuser:
        return redirect(adminHome)
    else:
        return redirect(studentHome)
def login(request):
    if request.user.is_authenticated:
        return redirect_user_based_on_role(request.user)
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
                return redirect(studentHome)
        except UserProfile.DoesNotExist:
            try:
                superAdmin = SuperAdmin.objects.get(email=email,password=password)
                if superAdmin:
                    auth_login(request, superAdmin)
                    send_mail("login Successfully", "There is a new login to your account in 'Sewedy PHP Tasks app'",
                              settings.EMAIL_HOST_USER, [email], fail_silently=False)
                    return redirect(adminHome)
            except SuperAdmin.DoesNotExist:
                return render(request, 'LoginPage.html', {'check': check})
    return render(request, 'LoginPage.html')
@login_required
def studentHome(request):
    return  render(request,'Student_HomePage.html')
@login_required
def adminHome(request):
    if request.user.is_superuser:
        return render(request,'Admin_HomePage.html')
    else:
        return redirect(studentHome)