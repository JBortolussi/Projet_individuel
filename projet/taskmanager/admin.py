from django.contrib import admin
from django.core.exceptions import ValidationError
from django.utils.text import Truncator

# models
from .models import Status, Task, Projet, Journal


class ProjetAdmin(admin.ModelAdmin):
    # configuration vue projet dans Admin
    list_display = ('name',)
    list_filter = ('members',)
    ordering = ('name',)
    search_fields = ('name',)

    # Ensure that the project has at least one member
    def clean(self):
        if not self.members:
            raise ValidationError("Un projet doit avoir au moins un membre")


class JournalAdmin(admin.ModelAdmin):
    list_display = ('author', 'date', 'apercu_entry', 'task', 'get_project')
    list_filter = ('author', 'date',)
    date_hierarchy = 'date'
    ordering = ('date',)

    def apercu_entry(self, journal):
        """
        Retourne les 40 premiers caractères du contenu du Journal,
        """
        return Truncator(journal.entry).chars(40, truncate='...')

    # pour permettre d'afficher le project auquel la tache du journal appartient
    def get_project(self, journal):
        return journal.task.projet

    get_project.short_description = "projet"
    apercu_entry.short_description = "entry"


class JournalInline(admin.TabularInline):
    '''
    Pour ajouter des journals directement de la page de la task
    '''
    model = Journal


class TaskAdmin(admin.ModelAdmin):
    list_display = ('name', 'projet', 'apercu_description', 'assignee', 'start_date', 'due_date', 'priority', 'status',)
    list_filter = ('projet', 'assignee', 'priority', 'status',)
    date_hierarchy = 'start_date'
    ordering = ('start_date',)
    search_fields = ('name', 'description',)

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

    # Configuration du formulaire d'édition
    fieldsets = (
        ('General', {
            'fields': ['name', 'projet', 'assignee'],
        }),
        ('Details', {
            'fields': ['start_date', 'due_date', 'status', 'priority', 'completion_percentage'],
        }),
        ('Optional', {
            'classes': ['collapse', ],
            'fields': ['description']
        }),
    )

    inlines = [JournalInline]  # pour inclure les journal dans la page de la tache


admin.site.register(Status)
admin.site.register(Task, TaskAdmin)
admin.site.register(Projet, ProjetAdmin)
admin.site.register(Journal, JournalAdmin)
