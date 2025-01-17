from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage

from taskApp.models import SuperAdmin, Statistics , UserProfile
def contextOfDashBoard(request):
    admin = SuperAdmin.objects.get(id=request.user.id)
    statics = Statistics.objects.first()
    users = UserProfile.objects.all()
    for user in users:
        user.totalTasks = user.task_set.all().count()
        user.grade = user.grade.lower()
    paginator = Paginator(list(users), 5)
    page_number = request.GET.get('page', 1)
    usersEmail = []
    for userEmail in users:
        if userEmail.email != '':
            usersEmail.append(userEmail.email)
    try:
        users = paginator.page(page_number)
    except PageNotAnInteger:
        users = paginator.page(1)
    except EmptyPage:
        users = paginator.page(paginator.num_pages)
    if statics:
        admin.first_name = admin.first_name[:7] + "..."
        context = {
            'admin': admin,
            'totalStudents': statics.totalStudents,
            'totalAdmins': statics.totalAdmins,
            'totalTasks': statics.totalTasks,
            'totalAmbassadors': statics.totalAmbassadors,
            'totalStudySupports': statics.totalStudySupports,
            'totalProfessionalSupports': statics.totalProfessionalSupports,
            'totalIntermediaries': statics.totalIntermediaries,
            'totalStudySupportsTasks': statics.totalStudySupportsTasks,
            'totalIntermediariesTasks': statics.totalIntermediariesTasks,
            'totalAmbassadorsTasks': statics.totalAmbassadorsTasks,
            'totalProfessionalSupportsTasks': statics.totalProfessionalSupportsTasks,
            'totalGuests': statics.totalGuests,
            'users': users,
            'usersEmail': usersEmail,
        }
        return context
    else:
        return  None