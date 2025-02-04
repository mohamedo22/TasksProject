from  django.urls import path
from .views import *
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth.views import LogoutView
from django.contrib.auth.views import PasswordChangeView, PasswordChangeDoneView
urlpatterns = [
    path('', login, name='index'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('setting/changePassword', changePassword , name='change_password'),
    path('ForgetPassword', forgetPassword , name='forgetPassword'),
    path('student_home/',studentHome,name='student_home'),
    path('admin_home/',adminHome,name='admin_home'),
    path('DashBoard/sendEmail',sendEmailFromAdmin , name='sendEmailFromAdmin'),
    path('DashBoard/ManageUsers',ManageUsers,name='ManageUsers'),
    path('DashBoard/SuperAdmins',ManageSuperUsers,name='ManageSuperAdmins'),
    path('DashBoard/TasksBoard',dashBoardTasks,name='tasksBoard'),
    path('DashBoard/TasksBoard/<int:Id>',dashBoardStudentTasks,name='dashBoardStudentTasks'),
    path('DashBoard/TasksBoard/<int:studenId>/Task/<int:taskId>',dashBoardTaskDetiles,name='dashBoardTaskDetails'),
    path('DashBoard/ManageUsers/editUser/',editUserFromAdmin,name='editUser'),
    path('DashBoard/ManageSuperUsers/editSuperUser/',editSuperUserFromAdmin,name='editSuperUser'),
    path('DashBoard/ManageUsers/deleteUser/',deleteUser,name='deleteUser'),
    path('DashBoard/ManageUsers/AddUser/',dashBoardAddUser,name='addUser'),
    path('DashBoard/ManageUsers/AddSuperUser/',dashBoardAddSuperUser,name='addSuperUser'),
    path('DashBoard/ManageSuperUsers/deleteUser/', deleteSuperUser, name='deleteSuperUser'),
    path('DashBoard/SuperAdminProfile', superAdminProfile, name='superAdminProfile'),
    path('student_home/tasks/<int:id>' , studentTasks , name='student_tasks'),
    path('add_task',addTask,name='addTask'),
    path('edit_task/<int:taskId>',editTask,name='editTask'),
    path('delete_task',deleteTask,name='deleteTask'),
    path('student_home/student/<int:studentId>/task/<int:id>',taskDetails, name='taskDetails'),
    path('student/<int:studentId>/task/<int:taskId>/addComment' , addComment , name='addComment'),
    path('student/<int:studentId>/task/<int:taskId>/addCommentLike/<int:id>',addCommentLike,name='addCommentLike'),
    path('setting/user_profile/<int:id>',userProfile,name='userProfile')


]
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)