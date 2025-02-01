from PIL import Image
from io import BytesIO
from django.core.files.uploadedfile import InMemoryUploadedFile
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.db.models import Q

from taskApp.models import UserProfile
def returnUsers(request):
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
            users = UserProfile.objects.filter(title__icontains=search)
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
def compressImage(inputImage):
    img = Image.open(inputImage)
    img = img.convert("RGB")
    img.thumbnail((300, 300))
    img_io = BytesIO()
    img.save(img_io, format='JPEG', quality=70)
    compressed_image = InMemoryUploadedFile(
        img_io, None, inputImage.name, 'image/jpeg', img_io.tell(), None
    )
    return compressed_image