from django.contrib.contenttypes.models import ContentType
from django.db import models
from django import forms
from django.contrib import admin
from django.contrib.auth.models import User, Group, Permission
from django.core.exceptions import ValidationError
from django.dispatch import receiver
from django.db.models.signals import pre_save, m2m_changed, pre_delete


# Create your models here.

class ProjetAdmin(admin.ModelAdmin):
    # configuration vue projet dans Admin
    list_display = ('name',)
    list_filter = ('name',)
    ordering = ('name',)
    search_fields = ('name',)


class Projet(models.Model):
    name = models.CharField(max_length=100)
    members = models.ManyToManyField(User, related_name='projets', null=True)

    def __str__(self):
        return self.name


class Status(models.Model):
    name = models.CharField(max_length=100)

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


@receiver(m2m_changed, sender=Projet.members.through)
def update_tasks_assignment(sender, **kwargs):
    project_tasks = Task.objects.filter(projet=kwargs['instance'])
    project_members = kwargs['instance'].members.all()
    # on recupère la liste des gens qui n'on rien à faire là
    wrong_assignee_task = project_tasks.exclude(assignee__in=project_members)
    for task in wrong_assignee_task:
        task.assignee = None
        task.save()


@receiver(m2m_changed, sender=Projet.members.through)
def creat_project_group(sender, **kwargs):
    project_name = kwargs['instance'].name
    if not Permission.objects.filter(codename='{}_project_permission'.format(project_name)):
        content_type = ContentType.objects.get_for_model(Projet)
        permission = Permission.objects.create(
            codename='{}_project_permission'.format(project_name),
            name='can see and contribute to the project {}"'.format(project_name),
            content_type=content_type,
        )
        permission.save()

        group = Group(name="{}_project_group".format(project_name))
        group.save()
        group.permissions.add(permission)

        print("{} will be added in {}".format(kwargs['instance'].members.all(), project_name))
        for member in kwargs['instance'].members.all():
            member.groups.add(group)
            member.save()
    else:
        group = Group.objects.get(name="{}_project_group".format(project_name))
        old_member = group.user_set.all()
        curent_member = kwargs['instance'].members.all()
        new_member = curent_member.exclude(id__in=old_member)
        member_to_be_remove = old_member.exclude(id__in=curent_member)
        for member in new_member:
            member.groups.add(group)
            member.save()
        for member in member_to_be_remove:
            member.groups.remove(group)
            member.save()


@receiver(pre_delete, sender=Projet)
def delete_related_group_and_permissions(sender, **kwargs):
    project_name = kwargs['instance'].name
    group = Group.objects.get(name="{}_project_group".format(project_name))
    permission = group.permissions.get(codename='{}_project_permission'.format(project_name))

    for member in group.user_set.all():
        member.groups.remove(group)
        member.save()

    group.delete()
    permission.delete()
