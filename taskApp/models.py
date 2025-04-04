from datetime import datetime

from cloudinary_storage.storage import MediaCloudinaryStorage
from django.db import models
from django.contrib.auth.models import User
from django.utils.text import slugify
# Create your models here.

###### Auth Tables ########
class UserProfile(User):
    name = models.CharField(max_length=100)
    phone = models.CharField(max_length=15)
    location = models.CharField(max_length=100)
    nationalId = models.CharField(max_length=20)
    userPermission = models.CharField(max_length=50)
    grade = models.CharField(max_length=50,null=True)
    firstStudentRule = models.CharField(max_length=50 , null=True)
    secondStudentRule = models.CharField(max_length=50 , null=True)
    adminRule = models.CharField(max_length=50 , null=True)
    profileImage = models.ImageField( default='https://res.cloudinary.com/dkcyr1ca9/image/upload/v1738752231/defaultUserProfile_bqkjax.png',null=True,storage=MediaCloudinaryStorage())
    totalTasks = models.IntegerField(default=0)
    def __str__(self):
        return self.name
class SuperAdmin(User):
    nationalId = models.CharField(max_length=20,default=0)
    profileImage = models.ImageField(default='https://res.cloudinary.com/dkcyr1ca9/image/upload/v1738752231/defaultUserProfile_bqkjax.png',storage=MediaCloudinaryStorage())
    pass
#### other Tables #######
class Task(models.Model):
    user = models.ForeignKey(UserProfile, on_delete=models.CASCADE)
    initiativeType = models.CharField(max_length=2)
    title = models.CharField(max_length=100)
    rate = models.CharField(default='0')
    description = models.TextField(max_length=2000)
    initiativePlace = models.CharField(max_length=50)
    dateOfTask = models.DateField(default=None)
    publishedDate = models.DateTimeField(auto_now_add=True)
    studentsName = models.TextField()
class TaskImages(models.Model):
    task = models.ForeignKey(Task, on_delete=models.CASCADE)
    image = models.ImageField(storage=MediaCloudinaryStorage())
class TaskComments(models.Model):
    task = models.ForeignKey(Task, on_delete=models.CASCADE)
    user = models.ForeignKey(UserProfile, on_delete=models.CASCADE,null=True)
    superAdmin = models.ForeignKey(SuperAdmin,on_delete=models.CASCADE,null=True)
    comment = models.TextField(max_length=2000)
    likesCount = models.IntegerField(default=0,null=True)
    publishedDate = models.DateTimeField(auto_now_add=True,null=True)
    def __str__(self):
        return self.comment
class Statistics(models.Model):
    totalTasks = models.IntegerField()
    totalAmbassadorsTasks = models.IntegerField()
    totalStudySupportsTasks = models.IntegerField()
    totalProfessionalSupportsTasks = models.IntegerField()
    totalIntermediariesTasks = models.IntegerField()
    totalStudents = models.IntegerField()
    totalAdmins = models.IntegerField()
    totalGuests = models.IntegerField()
    totalAmbassadors = models.IntegerField()
    totalStudySupports = models.IntegerField()
    totalProfessionalSupports = models.IntegerField()
    totalIntermediaries = models.IntegerField()