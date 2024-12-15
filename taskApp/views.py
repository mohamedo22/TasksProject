from tkinter.font import names
from django.db.models import Q
from django.contrib.auth.decorators import login_required
from django.shortcuts import render , redirect
from .models import *
from datetime import *
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth import login as auth_login
from django.contrib.auth import authenticate as auth_authenticate
# Create your views here.
def send_login_email(email):
    """Sends an email notification for successful login."""
    send_mail(
        subject="Login Successfully",
        message="There is a new login to your account in 'Sewedy PHP Tasks app'.",
        from_email=settings.EMAIL_HOST_USER,
        recipient_list=[email],
        fail_silently=False
    )
def redirect_user_based_on_role(user):
    if user.is_superuser:
        return redirect(adminHome)
    else:
        return redirect(studentHome)
def login(request):
    if request.user.is_authenticated:
        return redirect_user_based_on_role(request.user)
    if request.method == 'POST':
        print(request.POST)
        email = request.POST.get('email')
        password = request.POST.get('password')
        remember_me = request.POST.get('rememberMy', 'off')
        check = "false"
        try:
            user = UserProfile.objects.get(email=email, password=password)
            if user:
                auth_login(request, user)
                if remember_me == 'on':
                    request.session.set_expiry(60 * 60 * 24 * 30)  # 30 days
                    print("Remember Me checked: Session expiry set to 30 days")
                elif remember_me == 'off':
                    request.session.set_expiry(0)  # Expire when browser closes
                    print("Remember Me unchecked: Session expiry set to browser close")
                print(f"Remember Me: {remember_me}")
                print(f"Final session expiry: {request.session.get_expiry_age()} seconds")
                return redirect(studentHome)
        except UserProfile.DoesNotExist:
            try:
                superAdmin = SuperAdmin.objects.get(email=email,password=password)
                if superAdmin:
                    auth_login(request, superAdmin)
                    remember_me = request.POST.get('rememberMy', None)
                    if remember_me:
                        request.session.set_expiry(60 * 60 * 24 * 30)  # 30 days
                    else:
                        request.session.set_expiry(0)
                    send_login_email(email)
                    return redirect(adminHome)
            except SuperAdmin.DoesNotExist:
                return render(request, 'LoginPage.html', {'check': check})
    return render(request, 'LoginPage.html')
def studentHome(request):
    users = UserProfile.objects.all()
    if request.method == 'POST':
        filters = request.POST.getlist('filter')
        if request.method == 'POST':
            filters = request.POST.getlist('filter')
            if filters:
                query = Q()
                for filter in filters:
                    query |= Q(firstStudentRule=filter) | Q(secondStudentRule=filter)
                users = users.filter(query)
    users_data = []
    for user in users:
        users_data.append((user.id,user.name[:9]+"..." if len(user.name) > 9 else user.name ,user.firstStudentRule[:9]+"..." if len(user.firstStudentRule) >9 else user.firstStudentRule,user.secondStudentRule[:9]+"..."if len(user.secondStudentRule)>9 else user.secondStudentRule))
    context = {
        'usersData':users_data ,
    }
    if request.user.is_superuser:
        return redirect(adminHome)
    if request.user.is_authenticated:
        userId = request.user.id
        user = UserProfile.objects.get(id=userId)
        context['userProfile'] = user
        return  render(request,'Student_HomePage.html',context)
    else:
        return render(request,'Student_HomePage.html',context)
@login_required
def adminHome(request):
    if request.user.is_superuser:
        return render(request,'Admin_HomePage.html')
    else:
        return redirect(studentHome)
@login_required
def studentTasks(request , id):
    student = UserProfile.objects.get(id=id)
    tasks = Task.objects.filter(user=student)
    for task in tasks:
        if len(task.title) > 52:
            task.title = task.title[:52]+"..."
        if len(task.description) > 148:
            task.description = task.description[:148]+"..."
    context = {
        'student': student,
        'tasks': tasks,
    }
    return render(request,'Student_Tasks.html',context)
@login_required
def addTask(request):
    if request.method == 'POST':
        user = UserProfile.objects.get(id=request.user.id)
        title = request.POST.get('title')
        initiativePlace = request.POST.get('initiativePlace')
        description = request.POST.get('description')
        initiativeType = request.POST.get('initiativeType')
        dateOfTask = request.POST.get('dateOfTask')
        formatted_date = datetime.strptime(dateOfTask, '%d/%m/%Y').strftime('%Y-%m-%d')
        studentsName = request.POST.getlist('studentsName')
        initiativeImages = request.FILES.getlist('initiativeImages')
        task = Task(user=user,title=title, initiativePlace=initiativePlace , description=description, initiativeType=initiativeType, dateOfTask=formatted_date , studentsName=studentsName)
        task.save()
        for image in initiativeImages:
                newImage = TaskImages(task=task,image=image)
                newImage.save()
        return render(request,'AddTask.html' , {'added':"True"})

    return  render(request , 'AddTask.html', {'added':''})