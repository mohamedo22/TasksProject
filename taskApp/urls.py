from  django.urls import path
from .views import *

urlpatterns = [
    path('', login, name='index'),
    path('student_home/',studentHome,name='student_home'),
    path('admin_home/',adminHome,name='admin_home'),

]