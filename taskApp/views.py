import os
import random
import cloudinary.uploader
from cloudinary.uploader import upload
from django.contrib.sessions.models import Session
from django.db.models import Q
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import render , redirect
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.utils.timezone import now, is_naive, make_aware

from .Functions.AdminFunctions import contextOfDashBoard, sendEmailMessage, createInitialSuperAdmin
from .Functions.SharedFunctions import returnUsers, compressImage
from .models import *
from datetime import *
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth import login as auth_login, logout
from django.contrib.auth import authenticate as auth_authenticate
# Create your views here.
def createStatics():
    try:
        statics = Statistics.objects.first()  # Get the first record or None if not available
        if statics is None:
            newStatics = Statistics()
            newStatics.totalAdmins = SuperAdmin.objects.all().count()
            newStatics.totalTasks = Task.objects.all().count()
            newStatics.totalAmbassadorsTasks = Task.objects.filter(initiativeType='AM').count()
            newStatics.totalStudySupportsTasks = Task.objects.filter(initiativeType='SS').count()
            newStatics.totalProfessionalSupportsTasks = Task.objects.filter(initiativeType='PS').count()
            newStatics.totalIntermediariesTasks = Task.objects.filter(initiativeType='IN').count()
            newStatics.totalStudents = UserProfile.objects.filter(userPermission='student').count()
            newStatics.totalAdmins = UserProfile.objects.filter(userPermission='admin').count()
            query = Q()
            query = Q(firstStudentRule='SS') | Q(secondStudentRule='SS')
            newStatics.totalStudySupports = UserProfile.objects.filter(query).count()
            query = Q(firstStudentRule='AM') | Q(secondStudentRule='AM')
            newStatics.totalAmbassadors = UserProfile.objects.filter(query).count()
            query = Q(firstStudentRule='PS') | Q(secondStudentRule='PS')
            newStatics.totalProfessionalSupports = UserProfile.objects.filter(query).count()
            query = Q(firstStudentRule='IN') | Q(secondStudentRule='IN')
            newStatics.totalIntermediaries = UserProfile.objects.filter(query).count()
            newStatics.totalGuests = 0
            newStatics.save()

        else:
            statics.totalAdmins = SuperAdmin.objects.all().count()
            statics.totalTasks = Task.objects.all().count()
            statics.totalAmbassadorsTasks = Task.objects.filter(initiativeType='AM').count()
            statics.totalStudySupportsTasks = Task.objects.filter(initiativeType='SS').count()
            statics.totalProfessionalSupportsTasks = Task.objects.filter(initiativeType='PS').count()
            statics.totalIntermediariesTasks = Task.objects.filter(initiativeType='IN').count()
            statics.totalStudents = UserProfile.objects.filter(userPermission='student').count()
            statics.totalAdmins = UserProfile.objects.filter(userPermission='admin').count()
            query = Q()
            query = Q(firstStudentRule='SS') | Q(secondStudentRule='SS')
            statics.totalStudySupports = UserProfile.objects.filter(query).count()
            query = Q(firstStudentRule='AM') | Q(secondStudentRule='AM')
            statics.totalAmbassadors = UserProfile.objects.filter(query).count()
            query = Q(firstStudentRule='PS') | Q(secondStudentRule='PS')
            statics.totalProfessionalSupports = UserProfile.objects.filter(query).count()
            query = Q(firstStudentRule='IN') | Q(secondStudentRule='IN')
            statics.totalIntermediaries = UserProfile.objects.filter(query).count()
            statics.save()
    except Exception as e:
        print(f"Error creating statistics: {e}")

def send_login_email(email):
    """Sends an email notification for successful login."""
    send_mail(
        subject="Login Successfully",
        message="There is a new login to your account in 'Sewedy PHP Tasks app'.",
        html_message= "<h2>There is a new login to your account in  <span style='color:green'>Sewedy PHP Tasks app</span>.</h2>",
        from_email=settings.EMAIL_HOST_USER,
        recipient_list=[email],
        fail_silently=True
    )
def redirect_user_based_on_role(user):
    if user.is_superuser:
        return redirect(adminHome)
    else:
        return redirect(studentHome)
def login(request):
    createInitialSuperAdmin()
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
            if user and user.is_active:
                auth_login(request, user)
                if remember_me == 'on':
                    request.session.set_expiry(60 * 60 * 24 * 30)  # 30 days
                    print("Remember Me checked: Session expiry set to 30 days")
                else:
                    request.session.set_expiry(60*30)  # Expire when browser closes
                    print("Remember Me unchecked: Session expiry set to browser close")
                print(f"Remember Me: {remember_me}")
                print(f"Final session expiry: {request.session.get_expiry_age()} seconds")
                return redirect(studentHome)
        except UserProfile.DoesNotExist:
            try:
                superAdmin = SuperAdmin.objects.get(email=email,password=password)
                if superAdmin and superAdmin.is_active:
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
    createStatics()
    context = returnUsers(request)
    if request.user.is_superuser:
        return redirect(adminHome)
    if request.user.is_authenticated:
        userId = request.user.id
        user = UserProfile.objects.get(id=userId)
        user.name = user.name[:7] + "..."
        context['userProfile'] = user
        return  render(request,'Student_HomePage.html',context)
    else:
        if not request.session.get('gust'):
            request.session['gust'] = True
            statics = Statistics.objects.all()
            statics = statics[0]
            statics.totalGuests+=1
            statics.save()
        return render(request,'Student_HomePage.html',context)
@login_required
def changePassword(request):
    context={"wrongPassword":"","notMatch":""}
    if request.method == 'POST':
        userId = request.user.id
        print("user id: ",userId)
        oldPassword = request.POST.get('oldPassword',None)
        newPassword = request.POST.get('newPassword',None)
        confirmPassword = request.POST.get('confirmPassword',None)
        if oldPassword and newPassword and confirmPassword is not None:
            try:
                user = UserProfile.objects.get(id=userId)
                print("get user: ", user.name)
            except UserProfile.DoesNotExist:
                print("get admin")
                user = SuperAdmin.objects.get(id=userId)
            if not user.password == oldPassword:
                context["wrongPassword"]="True"
                return render(request, 'change_password.html', context)
            if newPassword != confirmPassword:
                context["notMatch"] = "True"
                return render(request, 'change_password.html', context)
            user.password = newPassword
            user.save()
            print("password changed successfully:  " , user.password)
            for session in Session.objects.all():
                data = session.get_decoded()
                if data.get('_auth_user_id') == str(userId):
                    session.delete()
            logout(request)
            return redirect(login)
    return render(request,'change_password.html',)
def forgetPassword(request):
    context = {
        "requested" : "False"
    }
    if request.method == 'POST':
        if 'email' in request.POST:
            email = request.POST.get('email')
            try:
                superAdmin = SuperAdmin.objects.get(email=email)
                OTP = str(random.randint(100000, 999999))
                OTP_CreatedTime = now() + timedelta(minutes=4)

                request.session['OTP'] = OTP
                request.session['userID'] = superAdmin.id
                request.session['OTP_CreatedTime'] = OTP_CreatedTime.isoformat()
                request.session['sent'] = True
                sendEmailMessage(f'<h1>Your OTP Code Is <span style="color:red;font-weight:bold;">{OTP}</span></h1>',
                                 "OTP Code", email)
                context['requested'] = "True"
                context['sent'] = "True"

            except SuperAdmin.DoesNotExist:
                context['requested'] = "True"
                context['sent'] = "True"
                request.session['sent'] = False
        elif 'sixthNumber' in request.POST:
            if request.session.get('sent',False):
                user_OTP = ''.join([
                    request.POST.get('firstNumber', ''),
                    request.POST.get('secondNumber', ''),
                    request.POST.get('thirdNumber', ''),
                    request.POST.get('forthNumber', ''),
                    request.POST.get('fifthNumber', ''),
                    request.POST.get('sixthNumber', '')
                ]).strip()
                stored_OTP = request.session.get('OTP')
                expiry_time_str = request.session.get('OTP_CreatedTime')
                if expiry_time_str:
                    expiry_time = datetime.fromisoformat(expiry_time_str)
                    if is_naive(expiry_time):
                        expiry_time = make_aware(expiry_time)
                    if now() < expiry_time:
                        if user_OTP == stored_OTP:
                            superAdmin = SuperAdmin.objects.get(id=request.session.get('userID'))
                            superAdmin.password = superAdmin.nationalId
                            superAdmin.save()
                            context['reset'] = "True"
                            del request.session['OTP']
                            del request.session['userID']
                        else:
                            del request.session['OTP']
                            del request.session['userID']
                            context['error'] = "Invalid OTP"
                    else:
                        del request.session['OTP']
                        del request.session['userID']
                        context['error'] = "OTP expired"
                else:
                    del request.session['OTP']
                    del request.session['userID']
                    context['error'] = "OTP session expired"
            else:
                context['error'] = "Invalid OTP"
    return render(request, 'forgetPassword.html', context)
@login_required
def adminHome(request):
    createStatics()
    if request.user.is_superuser:
        context = contextOfDashBoard(request)
        if context  is not None:
            return render(request, 'Admin_HomePage.html', context)
        else:
            return HttpResponse("Statistics not found")
    else:
        return redirect(studentHome)
@login_required
def ManageUsers(request,**kwargs):
    if request.user.is_superuser:
        allUsers = UserProfile.objects.all()
        if request.method == 'POST':
            search = request.POST.get('search')
            if search:
                allUsers = UserProfile.objects.filter(name__icontains=search)
        currentAdmin = SuperAdmin.objects.get(id=request.user.id)
        currentAdmin.first_name = currentAdmin.first_name[:8]+"..."
        page = request.GET.get('page',1)
        paginator = Paginator(allUsers,6)
        try:
            allUsers = paginator.page(page)
        except PageNotAnInteger:
            allUsers = paginator.page(1)
        except EmptyPage:
            allUsers = paginator.page(paginator.num_pages)
        context = {'users':allUsers,'admin':currentAdmin}
        update = kwargs.get('update', None)
        deleted = kwargs.get('deleted', None)
        if update is not None:
            context["updated"] = "True"
            update = None
        elif deleted is not None:
            context["deleted"] = "True"
            deleted = None
        return render(request , 'DashBoard_ManageUsers.html',context)
@login_required
def ManageSuperUsers(request,**kwargs):
    if request.user.is_superuser:
        allSuperUsers = SuperAdmin.objects.all()
        if request.method == 'POST':
            search = request.POST.get('search')
            if search:
                allUsers = SuperAdmin.objects.filter(first_name__icontains=search)
        currentAdmin = SuperAdmin.objects.get(id=request.user.id)
        currentAdmin.first_name = currentAdmin.first_name[:8]+"..."
        update = kwargs.get('update',None)
        deleted = kwargs.get('deleted',None)
        page = request.GET.get('page', 1)
        paginator = Paginator(allSuperUsers, 6)
        try:
            allSuperUsers = paginator.page(page)
        except PageNotAnInteger:
            allSuperUsers = paginator.page(1)
        except EmptyPage:
            allSuperUsers = paginator.page(paginator.num_pages)
        context = {'users':allSuperUsers,'admin':currentAdmin}
        if update is not None:
            context["updated"] = "True"
            update = None
        elif deleted is not None:
            context["deleted"] = "True"
            deleted = None
        return render(request , 'DashBoard_SuperUsers.html',context)
def sendEmailFromAdmin(request):
    if request.method == 'POST':
        userEmail = request.POST.get('userEmail')
        message = request.POST.get('emailmessage')
        title = request.POST.get('emailTitle')
        sendEmailMessage(message,title,userEmail)
        return redirect(adminHome)
@login_required
def editUserFromAdmin(request):
    if request.user.is_superuser:
        if request.method == 'POST':
            userId = request.POST.get('userId')
            userName = request.POST.get('name')
            email = request.POST.get('email')
            password = request.POST.get('password')
            phone = request.POST.get('phone')
            address = request.POST.get('address')
            nationalId = request.POST.get('nationalId')
            userPermission = request.POST.get('userPermission')
            grade = request.POST.get('grade')
            firstStudentRule = request.POST.get('firstStudentRule')
            secondStudentRule = request.POST.get('secondStudentRule')
            adminRule = request.POST.get('adminRule')
            isActive = request.POST.get('isActive','off')
            profileImage = request.FILES.get('profileImage')
            ###############
            user = UserProfile.objects.get(id=userId)
            if userName: user.name = userName
            if email: user.email = email
            if password: user.password = password
            if phone: user.phone = phone
            if address:user.address = address
            if nationalId:user.nationalId = nationalId
            if userPermission: user.userPermission = userPermission
            if grade:user.grade = grade
            if firstStudentRule:user.firstStudentRule = firstStudentRule
            if secondStudentRule: user.secondStudentRule = secondStudentRule
            if adminRule:user.adminRule = adminRule
            if profileImage:
                compressed_image = compressImage(profileImage)
                if compressed_image:
                    result = upload(
                        compressed_image,
                        public_id=f"user_profiles/{user.id}",
                        overwrite=True,
                        quality="auto:good"
                    )
                    user.profileImage = result['secure_url']
            if isActive == "on":
                user.is_active = True
            else:
                user.is_active = False
            user.save()
        return ManageUsers(request,update='True')
@login_required
def superAdminProfile(request):
    if request.user.is_superuser:
        currentAdmin = SuperAdmin.objects.get(id = request.user.id)
        currentAdmin.first_name = currentAdmin.first_name[:8]
        context={
            "admin":currentAdmin
        }
        if request.method == 'POST':
            userId = request.user.id
            firstName = request.POST.get('firstName')
            lastName = request.POST.get('lastName')
            email = request.POST.get('email')
            nationalId = request.POST.get('nationalId')
            profileImage = request.FILES.get('profileImage')
            ###############
            user = SuperAdmin.objects.get(id=userId)
            if firstName : user.first_name = firstName
            if lastName : user.last_name = lastName
            if email : user.email = email
            if nationalId : user.nationalId = nationalId
            if profileImage:
                compressed_image = compressImage(profileImage)
                if compressed_image:
                    result = upload(
                        compressed_image,
                        public_id=f"user_profiles/{user.id}",
                        overwrite=True,
                        quality="auto:good"
                    )
                    user.profileImage = result['secure_url']
            user.save()
            currentAdmin = SuperAdmin.objects.get(id=request.user.id)
            currentAdmin.first_name = currentAdmin.first_name[:8]
            context['admin']=currentAdmin
            context['updated']="True"
        return render(request,'SuperAdminProfile.html',context)
@login_required
def editSuperUserFromAdmin(request):
    if request.user.is_superuser:
        if request.method == 'POST':
            userId = request.POST.get('userId')
            name = request.POST.get('name')
            email = request.POST.get('email')
            isActive = request.POST.get('isActive','off')
            profileImage = request.FILES.get('profileImage')
            ###############
            user = SuperAdmin.objects.get(id=userId)
            user.first_name = name
            user.email = email
            if profileImage:
                compressed_image = compressImage(profileImage)
                if compressed_image:
                    result = upload(
                        compressed_image,
                        public_id=f"user_profiles/{user.id}",
                        overwrite=True,
                        quality="auto:good"
                    )
                    user.profileImage = result['secure_url']
            if isActive == "on":
                user.is_active = True
            else:
                user.is_active = False
            user.save()
        return ManageSuperUsers(request,update='True')
@login_required
def deleteUser(request):
    if request.method == 'POST':
        userId = request.POST.get('userId')
        user = UserProfile.objects.get(id=userId)
        if user:
            user.delete()
    return ManageUsers(request, deleted='True')
@login_required
def deleteSuperUser(request):
    if request.user.is_superuser:
        if request.method == 'POST':
            userId = request.POST.get('userId')
            user = SuperAdmin.objects.get(id=userId)
            if user:
                user.delete()
        return ManageSuperUsers(request,deleted='True')
@login_required
def dashBoardAddUser(request):
    if request.user.is_superuser:
        currentAdmin = SuperAdmin.objects.get(id=request.user.id)
        currentAdmin.first_name = currentAdmin.first_name[:8] + "..."
        context = {
            "admin": currentAdmin
        }
        if request.method == 'POST':
            name = request.POST.get('name')
            email = request.POST.get('email')
            phone = request.POST.get('phone')
            nationalId = request.POST.get('nationalId')
            userPermission = request.POST.get('userPermission')
            address = request.POST.get('address')
            adminRole = request.POST.get('adminRole')
            grade = request.POST.get('grade')
            firstStudentRole = request.POST.get('firstStudentRole')
            secondStudentRole = request.POST.get('secondStudentRole')
            newUser = UserProfile(
                name = name,
                username=name+nationalId,
                email=email,
                phone= phone,
                nationalId=nationalId,
                userPermission=userPermission,
                location=address,
                password=nationalId
            )
            lock = False
            if name and email and phone and nationalId and userPermission and address is not None:
                lock = True
            if userPermission =='admin':
                if adminRole:
                    newUser.adminRule = adminRole
                else:
                    lock = False
            else:
                if grade and firstStudentRole and secondStudentRole:
                    newUser.grade = grade
                    newUser.firstStudentRule = firstStudentRole
                    newUser.secondStudentRule = secondStudentRole
                else:
                    lock=False
            if lock:
                newUser.save()
                context["created"]="True"
            else:
                context["created"] = "False"
        return render(request,'DashBoard_AddUser.html',context)
@login_required
def dashBoardAddSuperUser(request):
    if request.user.is_superuser:
        currentAdmin = SuperAdmin.objects.get(id=request.user.id)
        currentAdmin.first_name = currentAdmin.first_name[:8] + "..."
        context = {
            "admin": currentAdmin
        }
        if request.method == 'POST':
            firstName = request.POST.get('firstName')
            lastName = request.POST.get('lastName')
            email = request.POST.get('email')
            nationalId = request.POST.get('nationalId')
            image = request.FILES.get('image')
            if firstName and lastName and email and nationalId and image is not None:
                newUser = SuperAdmin(
                    first_name = firstName,
                    last_name=lastName,
                    username=(firstName+nationalId).replace(" ",""),
                    email=email,
                    nationalId=nationalId,
                    password=nationalId,
                    is_superuser=True,
                    is_staff=True
                )
                newUser.save()
                if image:
                    compressed_image = compressImage(image)
                    if compressed_image:
                        result = upload(
                            compressed_image,
                            public_id=f"user_profiles/{newUser.id}",
                            overwrite=True,
                            quality="auto:good"
                        )
                        newUser.profileImage = result['secure_url']
                newUser.save()
                context["created"]="True"
            else:
                context["created"] = "False"
        return render(request,'DashBoard_AddSuperUser.html',context)
@login_required
def dashBoardTasks(request):
    if request.user.is_superuser:
        currentAdmin = SuperAdmin.objects.get(id=request.user.id)
        currentAdmin.first_name = currentAdmin.first_name[:8] + "..."
        context = returnUsers(request)
        context['admin'] = currentAdmin
        return  render(request,'DashBoard_Tasks.html',context)
@login_required
def dashBoardStudentTasks(request,Id):
    if request.user.is_superuser:
        currentAdmin = SuperAdmin.objects.get(id=request.user.id)
        currentAdmin.first_name = currentAdmin.first_name[:8] + "..."
        student = UserProfile.objects.get(id=Id)
        tasks = Task.objects.filter(user=student)
        if request.method == 'POST':
            search = request.POST.get('search')
            if search:
                tasks = Task.objects.filter(title__icontains=search)
        for task in tasks:
            if len(task.title) > 52:
                task.title = task.title[:52] + "..."
            if len(task.description) > 148:
                task.description = task.description[:148] + "..."
        page = request.GET.get('page', 1)
        paginator = Paginator(tasks, 6)
        try:
            tasks = paginator.page(page)
        except PageNotAnInteger:
            tasks = paginator.page(1)
        except EmptyPage:
            tasks = paginator.page(paginator.num_pages)
        context = {
            'student':student,
            'tasks': tasks,
            'admin':currentAdmin
        }
        return render(request, 'DashBoardSudentTasks.html', context)
@login_required
def dashBoardTaskDetiles(request,studenId,taskId):
    if request.user.is_superuser:
        task_sp = Task.objects.get(id=taskId)
        currentAdmin = SuperAdmin.objects.get(id=request.user.id)
        currentAdmin.first_name = currentAdmin.first_name[:8] + "..."
        task_sp.user.name = task_sp.user.name[:20] + "..."
        task_sp.studentsName = task_sp.studentsName.replace("\r", ", ")
        task_comments = task_sp.taskcomments_set.all()
        comments = []
        for comment in task_comments:
            # Calculate time difference
            time_diff = datetime.now(timezone.utc) - comment.publishedDate
            if time_diff.days > 0:
                time_ago = f"{time_diff.days} day{'s' if time_diff.days > 1 else ''} ago"
            elif time_diff.seconds >= 3600:
                hours = time_diff.seconds // 3600
                time_ago = f"{hours} hour{'s' if hours > 1 else ''} ago"
            elif time_diff.seconds >= 60:
                minutes = time_diff.seconds // 60
                time_ago = f"{minutes} minute{'s' if minutes > 1 else ''} ago"
            else:
                time_ago = "Just now"
            if comment.superAdmin:
                user = comment.superAdmin
                commenterName = comment.superAdmin.first_name
                isSuperAdmin = True
            else:
                user = comment.user
                commenterName = comment.user.name
                isSuperAdmin = False
            comments.append({
                "id": comment.id,
                "liked": request.session.get(f"{comment.id}"),
                "comment_text": comment.comment,
                "likes_count": comment.likesCount,
                "user": user,
                "commenterName":commenterName,
                "time_ago": time_ago,
                "isSuperAdmin":isSuperAdmin
            })
        page = request.GET.get('page', 1)
        paginator = Paginator(comments, 2)
        try:
            comments = paginator.page(page)
        except PageNotAnInteger:
            comments = paginator.page(1)
        except EmptyPage:
            comments = paginator.page(paginator.num_pages)
        context = {
            'admin':currentAdmin,
            'task': task_sp,
            'task_comments': comments,
            'student':UserProfile.objects.get(id=studenId)
        }
        return render(request, 'dashBoardTaskDetiles.html', context)

def studentTasks(request , id):

    student = UserProfile.objects.get(id=id)
    student.name = student.name[:14]+"..."
    tasks = Task.objects.filter(user=student)
    users = UserProfile.objects.filter(userPermission='student')
    if request.method == 'POST':
        filters = request.POST.getlist('filter')
        search = request.POST.get('search')
        if filters:
            query = Q()
            for filter in filters:
                query |= Q(initiativeType = filter)
            tasks = tasks.filter(query)
        if search:
            tasks = Task.objects.filter(title__icontains=search)
    for user in users:
        user.name = user.name[:7] + "..."
        for task in user.task_set.all():
            task.title = task.title[:14] + "..."
    student.name = student.name[:7]+"..."
    for task in tasks:
        if len(task.title) > 52:
            task.title = task.title[:52]+"..."
        if len(task.description) > 148:
            task.description = task.description[:148]+"..."
    page = request.GET.get('page',1)
    paginator = Paginator(tasks,9)
    try:
        tasks = paginator.page(page)
    except PageNotAnInteger:
        tasks = paginator.page(1)
    except EmptyPage:
        tasks = paginator.page(paginator.num_pages)
    context = {
        'student': student,
        'tasks': tasks,
        'usersData':users ,
    }
    if request.user.is_authenticated:
        current_user = UserProfile.objects.get(id=request.user.id)
        current_user.name = current_user.name[:7]+"..."
        context["current_user"] = current_user
    return render(request,'Student_Tasks.html',context)
@login_required
def addTask(request):
    if request.method == 'POST':
        user = UserProfile.objects.get(id=request.user.id)
        if user.userPermission == "student":
            title = request.POST.get('title')
            initiativePlace = request.POST.get('initiativePlace')
            description = request.POST.get('description')
            initiativeType = request.POST.get('initiativeType')
            dateOfTask = request.POST.get('dateOfTask')
            formatted_date = datetime.strptime(dateOfTask, '%m/%d/%Y').strftime('%Y-%m-%d')
            studentsName = request.POST.get('studentsName')
            initiativeImages = request.FILES.getlist('initiativeImages')
            task = Task(user=user,title=title, initiativePlace=initiativePlace , description=description, initiativeType=initiativeType, dateOfTask=formatted_date , studentsName=studentsName)
            task.save()
            for image in initiativeImages:
                    newImage = TaskImages(task=task)
                    if image:
                        compressed_image = compressImage(image)
                        if compressed_image:
                            result = upload(
                                compressed_image,
                                public_id=f"user_profiles/{task.id}",
                                overwrite=True,
                                quality="auto:good"
                            )
                            newImage.image = result['secure_url']
                    newImage.save()
            return render(request,'AddTask.html' , {'added':"True"})

    return  render(request , 'AddTask.html', {'added':''})
@login_required
def editTask(request,taskId):
    task = Task.objects.get(id=taskId)
    if not request.user.is_superuser:
        user = UserProfile.objects.get(id = request.user.id)
    else:
        user = None
    if request.method == 'POST':
        if task.user.id == request.user.id or request.user.is_superuser:
            title = request.POST.get('title')
            initiativePlace = request.POST.get('initiativePlace')
            description = request.POST.get('description')
            initiativeType = request.POST.get('initiativeType')
            dateOfTask = request.POST.get('dateOfTask')
            formatted_date = datetime.strptime(dateOfTask, '%m/%d/%Y').strftime('%Y-%m-%d')
            studentsName = request.POST.get('studentsName')
            ###########################
            task.title = title
            task.initiativePlace = initiativePlace
            task.description = description
            task.initiativeType = initiativeType
            task.dateOfTask = formatted_date
            task.studentsName = studentsName
            task.save()
            return render(request,'editTask.html' , {'updated':"True",'task':task})
        elif (user and user.userPermission == "admin"):
            title = request.POST.get('title')
            initiativePlace = request.POST.get('initiativePlace')
            description = request.POST.get('description')
            initiativeType = request.POST.get('initiativeType')
            dateOfTask = request.POST.get('dateOfTask')
            formatted_date = datetime.strptime(dateOfTask, '%m/%d/%Y').strftime('%Y-%m-%d')
            studentsName = request.POST.get('studentsName')
            ###########################
            task.title = title
            task.initiativePlace = initiativePlace
            task.description = description
            task.initiativeType = initiativeType
            task.dateOfTask = formatted_date
            task.studentsName = studentsName
            task.save()
            return render(request, 'editTask.html', {'updated': "True", 'task': task})
    return  render(request , 'editTask.html', {'updated':'','task':task})


@login_required
def deleteTask(request):
    if request.method == 'POST':
        if not request.user.is_superuser:
            user = UserProfile.objects.get(id=request.user.id)
        else:
            user = None
        taskId = request.POST.get('taskId')
        try:
            task = Task.objects.get(id=taskId)
        except Task.DoesNotExist:
            return redirect("some_error_page")
        if task.user.id == request.user.id or  request.user.is_superuser:
            task.delete()
            return redirect(login)
        elif (user and user.userPermission == "admin"):
            task.delete()
            return redirect(login)

    return redirect(login)
def taskDetails(request,studentId,id):
    task_sp = Task.objects.get(id=id)
    student = UserProfile.objects.get(id=studentId)
    student.name =  student.name[:14]+"..." if len(student.name) > 14  else student.name
    users = UserProfile.objects.filter(userPermission='student')
    for user in users:
        user.name = user.name[:7] + "..."
        for task in user.task_set.all():
            task.title = task.title[:14] + "..."
    task_sp.user.name = task_sp.user.name[:20] + "..."
    task_sp.studentsName = task_sp.studentsName.replace("\r",", ")
    student.name = student.name[:7] + "..."
    task_comments = task_sp.taskcomments_set.all()
    comments = []
    for comment in task_comments:
        # Calculate time difference
        time_diff = datetime.now(timezone.utc) - comment.publishedDate
        if time_diff.days > 0:
            time_ago = f"{time_diff.days} day{'s' if time_diff.days > 1 else ''} ago"
        elif time_diff.seconds >= 3600:
            hours = time_diff.seconds // 3600
            time_ago = f"{hours} hour{'s' if hours > 1 else ''} ago"
        elif time_diff.seconds >= 60:
            minutes = time_diff.seconds // 60
            time_ago = f"{minutes} minute{'s' if minutes > 1 else ''} ago"
        else:
            time_ago = "Just now"
        if comment.user:
            commenter = comment.user
            commenterName = comment.user.name[:10]+'...' if len(comment.user.name)>10 else comment.user.name
        else:
            commenter = comment.superAdmin
            commenterName = comment.superAdmin.first_name[:10]+'...' if len(comment.superAdmin.first_name)>10 else comment.superAdmin.first_name
        comments.append({
            "id":comment.id,
            "liked": request.session.get(f"{comment.id}"),
            "comment_text": comment.comment,
            "likes_count": comment.likesCount,
            "user": commenter,
            "commenterName":commenterName,
            "time_ago": time_ago,
        })
    page = request.GET.get('page', 1)
    paginator = Paginator(comments, 2)
    try:
        comments = paginator.page(page)
    except PageNotAnInteger:
        comments = paginator.page(1)
    except EmptyPage:
        comments = paginator.page(paginator.num_pages)
    context = {
        'student': student,
        'usersData': users,
        'task':task_sp,
        'task_comments':comments,
    }
    if request.user.is_authenticated:
        currentUser = UserProfile.objects.get(id=request.user.id)
        currentUser.name = currentUser.name[:7] + "..."
        context["currentUser"] = currentUser
    return render(request,'TaskDetails.html' , context)
def userProfile(request,id):
    user = UserProfile.objects.get(id=id)

    if request.method == 'POST':
        if user.id == request.user.id:
            email = request.POST.get('email')
            grade = request.POST.get('grade')
            phone = request.POST.get('phone')
            profileImage = request.FILES.get('profileImage')
            if email is not None:
                user.email = email
            if grade is not None:
                user.grade = grade
            if phone is not None:
                user.phone = phone
            if profileImage is not None:
                compressed_image = compressImage(profileImage)
                if compressed_image:
                    result = upload(
                        compressed_image,
                        public_id=f"user_profiles/{user.id}",
                        overwrite=True,
                        quality="auto:good"
                    )
                    user.profileImage = result['secure_url']
            user.save()
            return render(request,'UserProfile.html' , {'userData':user , "updated":"True"})
    return render(request,'UserProfile.html' , {'userData':user , "updated":""})
def addComment(request,studentId,taskId):
    if request.method == 'POST':
        task = Task.objects.get(id=taskId)
        comment = request.POST.get('comment')
        if request.user.is_superuser:
            commenter = SuperAdmin.objects.get(id=request.user.id)
            newComment = TaskComments(task=task, comment=comment, superAdmin=commenter)
            newComment.save()
        else:
            commenter = UserProfile.objects.get(id=request.user.id)
            newComment = TaskComments(task=task, comment=comment, user=commenter)
            newComment.save()
        if request.user.is_superuser:
            return redirect(dashBoardTaskDetiles,studentId,taskId)
        return redirect(taskDetails,studentId,taskId)
def addCommentLike(request,studentId,taskId,id):
    if request.method == 'POST':
        comment = TaskComments.objects.get(id=id)
        commentLiked = request.session.get(f'{comment.id}',False)
        if commentLiked:
            comment.likesCount-=1
            comment.save()
            request.session[f'{comment.id}'] = False
            if request.user.is_superuser:
                return redirect(dashBoardTaskDetiles, studentId,taskId)
            return redirect(taskDetails,studentId, taskId)
        else:
            request.session[f'{comment.id}'] = True
            comment.likesCount += 1
            comment.save()
            if request.user.is_superuser:
                return redirect(dashBoardTaskDetiles,studentId,taskId)
            return redirect(taskDetails, studentId,taskId)

