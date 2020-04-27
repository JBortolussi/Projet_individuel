from django.contrib import admin
from .models import Status, Task, Projet, TaskAdmin, ProjetAdmin

# Register your models here.
admin.site.register(Status)
admin.site.register(Task, TaskAdmin)
admin.site.register(Projet, ProjetAdmin)