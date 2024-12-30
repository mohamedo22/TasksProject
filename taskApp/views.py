from tkinter.font import names
from django.db.models import Q
from django.contrib.auth.decorators import login_required
from django.shortcuts import render , redirect
from django.template.defaultfilters import lower
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
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
                else:
                    request.session.set_expiry(60*30)  # Expire when browser closes
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
    users = UserProfile.objects.filter(userPermission='student')
    if request.method == 'POST':
            filters = request.POST.getlist('filter')
            search = request.POST.get('search')
            if filters:
                query = Q()
                for filter in filters:
                    query |= Q(firstStudentRule=filter) | Q(secondStudentRule=filter)
                users = users.filter(query)
            if search:
                users = UserProfile.objects.filter(name__icontains=search)
    for user in users:
        user.name = user.name[:7]+"..."
        for task in user.task_set.all():
            task.title = task.title[:14] + "..."

    context = {
        'usersData':users ,
    }
    if request.user.is_superuser:
        return redirect(adminHome)
    if request.user.is_authenticated:
        userId = request.user.id
        user = UserProfile.objects.get(id=userId)
        user.name = user.name[:7] + "..."
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
    context = {
        'student': student,
        'tasks': tasks,
        'usersData':users ,
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
        formatted_date = datetime.strptime(dateOfTask, '%m/%d/%Y').strftime('%Y-%m-%d')
        studentsName = request.POST.getlist('studentsName')
        initiativeImages = request.FILES.getlist('initiativeImages')
        task = Task(user=user,title=title, initiativePlace=initiativePlace , description=description, initiativeType=initiativeType, dateOfTask=formatted_date , studentsName=studentsName)
        task.save()
        for image in initiativeImages:
                newImage = TaskImages(task=task,image=image)
                newImage.save()
        return render(request,'AddTask.html' , {'added':"True"})

    return  render(request , 'AddTask.html', {'added':''})
def taskDetails(request,id):
    task_sp = Task.objects.get(id=id)
    student = UserProfile.objects.get(id=request.user.id)
    users = UserProfile.objects.filter(userPermission='student')
    for user in users:
        user.name = user.name[:7] + "..."
        for task in user.task_set.all():
            task.title = task.title[:14] + "..."
    task_sp.user.name = task_sp.user.name[:20] + "..."
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

        comments.append({
            "id":comment.id,
            "liked": request.session.get(f"{comment.id}"),
            "comment_text": comment.comment,
            "likes_count": comment.likesCount,
            "user": comment.user,
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
    return render(request,'TaskDetails.html' , context)
def userProfile(request,id):
    user = UserProfile.objects.get(id=id)
    return render(request,'UserProfile.html' , {'userData':user})
def deleteTask(request,id):
    task = Task.objects.get(id=id)
    task.delete()
    return redirect(studentTasks,request.user.id)
def addComment(request,id):
    if request.method == 'POST':
        task = Task.objects.get(id=id)
        comment = request.POST.get('comment')
        commenter = UserProfile.objects.get(id=request.user.id)
        newComment = TaskComments(task=task,comment=comment,user=commenter)
        newComment.save()
        return redirect(taskDetails,id)
def addCommentLike(request,taskId,id):
    if request.method == 'POST':
        comment = TaskComments.objects.get(id=id)
        commentLiked = request.session.get(f'{comment.id}',False)
        if commentLiked:
            comment.likesCount-=1
            comment.save()
            request.session[f'{comment.id}'] = False
            return redirect(taskDetails,taskId)
        else:
            request.session[f'{comment.id}'] = True
            comment.likesCount += 1
            comment.save()
            return redirect(taskDetails, taskId)
