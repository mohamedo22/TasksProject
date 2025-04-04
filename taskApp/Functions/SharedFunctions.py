from PIL import Image, UnidentifiedImageError
from io import BytesIO
from django.core.files.uploadedfile import InMemoryUploadedFile
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.db.models import Q
from taskApp.models import UserProfile
import magic
def returnUsers(request):
    users = UserProfile.objects.filter(userPermission='student').order_by('id')
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
        user.name = user.name[:11] + "..."
        user.grade = user.grade.lower()
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


def compressImage(image):
    try:
        # Create in-memory file handler
        img_io = BytesIO()

        # Open and validate image using Pillow
        with Image.open(image) as img:
            # Convert to RGB if needed (strip alpha channel)
            if img.mode in ("RGBA", "P"):
                img = img.convert("RGB")

            # Preserve original format if JPEG/PNG, else convert to JPEG
            original_format = img.format
            if original_format not in ('JPEG', 'PNG'):
                original_format = 'JPEG'

            # Set quality parameters (85% for JPEG, optimize for PNG)
            save_kwargs = {
                'format': original_format,
                'quality': 85,
                'optimize': True
            }

            # Special handling for PNG to maintain transparency
            if original_format == 'PNG':
                img.save(img_io, **save_kwargs, compress_level=3)
            else:
                img.save(img_io, **save_kwargs)

            # Determine content type
            content_type = f'image/{original_format.lower()}'

            # Reset buffer position
            img_io.seek(0)

            # Create new InMemoryUploadedFile
            return InMemoryUploadedFile(
                file=img_io,
                field_name=None,
                name=image.name,
                content_type=content_type,
                size=img_io.getbuffer().nbytes,
                charset=None
            )

    except (UnidentifiedImageError, OSError, IOError):
        # Handle invalid/corrupt images
        return None
    except Exception as e:
        # Log unexpected errors for debugging
        print(f"Compression error: {str(e)}")
        return None