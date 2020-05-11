from django.contrib import admin
from django.core.exceptions import ValidationError

from .models import Status, Task, Projet, Journal


# Register your models here.

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

admin.site.register(Status)
admin.site.register(Task, TaskAdmin)
admin.site.register(Projet, ProjetAdmin)
admin.site.register(Journal, JournalAdmin)
