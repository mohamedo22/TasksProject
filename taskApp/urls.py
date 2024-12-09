from  django.urls import path
from .views import *
from django.conf import settings
from django.conf.urls.static import static
urlpatterns = [
    path('', login, name='index'),
    path('student_home/',studentHome,name='student_home'),
    path('admin_home/',adminHome,name='admin_home'),

]
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)