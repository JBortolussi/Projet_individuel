from django.contrib.contenttypes.models import ContentType
from django.db import models
from django import forms
from django.contrib import admin
from django.contrib.auth.models import User, Group, Permission
from django.core.exceptions import ValidationError
from django.dispatch import receiver
from django.db.models.signals import pre_save, m2m_changed, pre_delete
from django.utils import timezone

# Create your models here.
from projet import settings


class ProjetAdmin(admin.ModelAdmin):
    # configuration vue projet dans Admin
    list_display = ('name',)
    list_filter = ('name',)
    ordering = ('name',)
    search_fields = ('name',)

    # Ensure that the prject has at least one member
    def clean(self):
        if not self.members:
            raise ValidationError("Un projet doit avoir au moins un membre")

class Projet(models.Model):
    name = models.CharField(max_length=100)
    members = models.ManyToManyField(User, related_name='projets')

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
    name = models.CharField(max_length=100, verbose_name="Nom")
    projet = models.ForeignKey("Projet", on_delete=models.CASCADE, null=True, blank=True)
    description = models.TextField()
    assignee = models.ForeignKey(User, null=True, on_delete=models.SET_NULL)
    start_date = models.DateField(verbose_name="Date de début")
    due_date = models.DateField(verbose_name="Date de fin")
    priority = models.IntegerField()
    status = models.ForeignKey('Status', on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return self.name

    def clean(self):
        if self.projet==None:
            return
        if self.assignee not in self.projet.members.all():
            raise ValidationError("Il faut que la perssonne à qui on assigne la tâche soit membre du projet")


class Journal(models.Model):
    date = models.DateTimeField(default=timezone.now, verbose_name="Date de parution", blank=True)
    entry = models.CharField(max_length=160)
    author = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    task = models.ForeignKey('Task', on_delete=models.CASCADE, null=True, blank=True)


class JournalAdmin(admin.ModelAdmin):
    list_display = ('author', 'date', 'apercu_entry', 'task',)
    list_filter = ('author', 'date',)
    date_hierarchy = 'date'
    ordering = ('date',)

    def apercu_entry(self, journal):
        """
        Retourne les 40 premiers caractères de la description. S'il
        y a plus de 40 caractères, il faut rajouter des points de suspension.
        """
        text = journal.entry[0:40]
        if len(journal.entry) > 40:
            return '%s…' % text
        else:
            return text


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
    project_id = kwargs['instance'].id
    if not Permission.objects.filter(codename='{}_project_permission'.format(project_id)):
        content_type = ContentType.objects.get_for_model(Projet)
        permission = Permission.objects.create(
            codename='{}_project_permission'.format(project_id),
            name='can see and contribute to the project {}({})"'.format(project_name, project_id),
            content_type=content_type,
        )
        permission.save()
        # TODO ajouter ici les autres permissions, trouver un moyen plus propre de le faire
        group = Group(name="{}_project_group".format(project_id))
        group.save()
        group.permissions.add(permission)
        for member in kwargs['instance'].members.all():
            member.groups.add(group)
            member.save()
    else:
        group = Group.objects.get(name="{}_project_group".format(project_id))
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
    project_id = kwargs['instance'].id
    group = Group.objects.get(name="{}_project_group".format(project_id))
    # TODO si il ya plusieur permission, mettre une boucle
    permission = group.permissions.get(codename='{}_project_permission'.format(project_id))

    for member in group.user_set.all():
        member.groups.remove(group)
        member.save()

    group.delete()
    permission.delete()
