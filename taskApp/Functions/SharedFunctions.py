from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage

from taskApp.models import UserProfile
def returnUsers(request):
    users = UserProfile.objects.filter(userPermission='student')
    if request.method == 'POST':
        search = request.POST.get('search')
        if search:
            users = UserProfile.objects.filter(name__icontains=search)
    for user in users:
        user.name = user.name[:7] + "..."
        for task in user.task_set.all():
            task.title = task.title[:14] + "..."
    page = request.GET.get('page', 1)
    if request.user.is_superuser:
        paginator = Paginator(users, 6)
    else:
        paginator = Paginator(users, 12)
    try:
        users = paginator.page(page)
    except PageNotAnInteger:
        users = paginator.page(1)
    except EmptyPage:
        users = paginator.page(paginator.num_pages)
    context = {
        'usersData': users,
    }
    return context