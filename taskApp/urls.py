from  django.urls import path
from .views import *
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth.views import LogoutView
urlpatterns = [
    path('', login, name='index'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('student_home/',studentHome,name='student_home'),
    path('admin_home/',adminHome,name='admin_home'),
    path('student_home/tasks/<int:id>' , studentTasks , name='student_tasks'),
    path('add_task',addTask,name='addTask'),
    path('student_home/tasks/task/<int:id>',taskDetails, name='taskDetails'),
    path('task/<int:id>/comment' , addComment , name='addComment')


]
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)