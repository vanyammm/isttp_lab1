from django.contrib import admin
from .models import CustomUser, Category, Topic, Comment

# Register your models here.

admin.site.register(CustomUser)
admin.site.register(Category)
admin.site.register(Topic)
admin.site.register(Comment)

