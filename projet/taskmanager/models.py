from django.db import models
from django import forms
from django.contrib import admin
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError

# Create your models here.

class ProjetAdmin(admin.ModelAdmin):
    #configuration vue projet dans Admin
    list_display = ('name', )
    list_filter = ('name',)
    ordering = ('name',)
    search_fields = ('name', )

class Projet(models.Model):
    name = models.CharField(max_length=100)
    members = models.ManyToManyField(User, related_name='projets', blank=True)

    def __str__(self):
        return self.name

class Status(models.Model):
    name=models.CharField(max_length=100)

    class Meta:
        verbose_name = "Status"
        verbose_name_plural = "Status"

    def __str__(self):
        return self.name


class TaskAdmin(admin.ModelAdmin):
    list_display = ('name', 'projet', 'apercu_description', 'assignee', 'start_date', 'due_date', 'priority', 'status',)
    list_filter = ('projet', 'name', 'start_date', 'due_date', 'priority', 'status',)
    date_hierarchy = 'start_date'
    ordering = ('start_date',)
    search_fields = ('name', 'status',)

    def apercu_description(self, task):
        """
        Retourne les 40 premiers caractères de la description. S'il
        y a plus de 40 caractères, il faut rajouter des points de suspension.
        """
        text = task.description[0:40]
        if len(task.description) > 40:
            return '%s…' % text
        else:
            return text

class Task(models.Model):
    name = models.CharField(max_length=100)
    projet = models.ForeignKey("Projet", on_delete=models.CASCADE)
    description = models.TextField(default="Pas de description")
    assignee = models.ForeignKey(User, null=True, on_delete=models.SET_NULL)
    start_date = models.DateField()
    due_date = models.DateField()
    priority = models.IntegerField()
    status = models.ForeignKey('status', on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return self.name

    def clean(self):
        if self.assignee not in self.projet.members.all():
            raise ValidationError("Il faut que la perssonne à qui on assigne la tâche soit membre du projet")