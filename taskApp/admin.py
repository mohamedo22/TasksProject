from django.contrib import admin
from  .models import *
# Register your models here.
admin.site.register(Task)
admin.site.register(TaskComments)
admin.site.register(TaskImages)
admin.site.register(Statistics)
admin.site.register(UserProfile)
admin.site.register(SuperAdmin)