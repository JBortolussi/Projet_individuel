# python modules
from datetime import datetime

# django modules
from django import forms
from django.core.exceptions import ValidationError
from django.forms import DateInput

# models
from .models import Projet, Journal, Task, Status


# REPLACED BY GENERIC VIEWS
# class ConnexionForm(forms.Form):
#     """Form for the connection page
#
#     Set up the style properties
#     """
#
#     def __init__(self, *args, **kwargs):
#         super(ConnexionForm, self).__init__(*args, **kwargs)
#
#         # Set up the style properties
#         self.fields['username'].label = "Nom d'utilisateur"
#         self.fields['username'].widget.attrs.update({'class': 'form-control', 'placeholder': "Nom du d'utilisateur"})
#         self.fields['password'].label = "Mot de passe"
#         self.fields['password'].widget.attrs.update({'class': 'form-control', 'placeholder': "Mot de passe"})
#
#     username = forms.CharField(label="Nom d'utilisateur", max_length=30)
#     password = forms.CharField(label="Mot de passe", widget=forms.PasswordInput)


class ProjectForm(forms.ModelForm):
    """Form for Projet Model

    Set up the style properties. By default the form propose the current user as the only member.

    This form ensure that the project has at least one member
    """

    def __init__(self, user, *args, **kwargs):
        """

        :param user: the initial value of the member field
        :param args:
        :param kwargs:
        """
        super(ProjectForm, self).__init__(*args, **kwargs)

        # Set the style properties
        self.fields['name'].label = "Nom du projet"
        self.fields['name'].widget.attrs.update({'class': 'form-control', 'placeholder': "Nom du projet"})
        self.fields['members'].label = "Membres du projet"
        self.fields['members'].widget.attrs.update({'class': 'form-control'})
        self.fields['members'].initial = user

    class Meta:
        model = Projet
        fields = "__all__"

    def clean(self):
        """Ensure the the project ha at least one member"""
        if not self.cleaned_data['members']:
            raise ValidationError("Un projet doit avoir au moins un membre")


class JournalForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super(JournalForm, self).__init__(*args, **kwargs)

        # Set the style properties
        self.fields['entry'].widget.attrs.update({'class': 'form-control'})

    class Meta:
        model = Journal

        # Exclude all the fields except the entry. They will be set up using the local value in the corresponding view
        exclude = ('task', 'date', 'author')
        widgets = {'entry': forms.TextInput(attrs={'cols': 10, 'placeholder': "Write here..."})
                   }


class TaskForm(forms.ModelForm):
    def __init__(self, project, *args, **kwargs):
        # Use to limit the possible choice for the assignee field to members of the project
        assignee_choices = [(member.id, member.username) for member in project.members.all()]
        super(TaskForm, self).__init__(*args, **kwargs)

        # Set the style properties
        self.fields['assignee'].label = "Assignée à :"
        self.fields['assignee'].widget.attrs.update({'class': 'form-control'})
        # Actually limit the choices for the assignee field
        self.fields['assignee'].choices = assignee_choices
        self.fields['name'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Nom de la tâche'})
        self.fields['description'].widget.attrs.update(
            {'class': 'form-control', 'placeholder': 'Description de la tache', 'rows': 4})
        self.fields['start_date'].widget.attrs.update({'class': 'form-control', })
        # Initialize the start_date field with the current date
        self.fields['start_date'].initial = datetime.now().strftime("%Y-%m-%d")
        self.fields['due_date'].widget.attrs.update({'class': 'form-control'})
        self.fields['status'].widget.attrs.update({'class': 'form-control'})
        self.fields['priority'].widget.attrs.update({'class': 'form-control'})
        self.fields['priority'].initial = 1
        self.fields['completion_percentage'].widget.attrs.update({'class': 'form-control'})
        self.fields['completion_percentage'].initial = 1
        # This field is only used in order to set up the project field with the project.
        # Shall not be modified by the user
        self.fields['projet'].widget.attrs.update({'style': 'display: none'})
        self.fields['projet'].initial = project
        # If a "new" status has be defined then initialize the status field with it
        if Status.objects.filter(name="Nouvelle"):
            self.fields['status'].initial = Status.objects.filter(name="Nouvelle")[0]

    class Meta:
        model = Task
        exclude = ('',)
        widgets = {
            'start_date': DateInput(format=('%Y-%m-%d'), attrs={'type': 'date'}),
            'due_date': DateInput(format=('%Y-%m-%d'), attrs={'type': 'date'})
        }

    # pour s'assurer que la priorité de la tache soit comprise entre 1 et 10
    def clean_priority(self):
        priority = self.cleaned_data['priority']
        if priority < 1 or priority > 10:
            raise ValidationError('Ensure this value is in the range.')

        return priority  # Ne pas oublier de renvoyer le contenu du champ traité

    # pour s'assurer que la due_date soit successive à la start_date
    def clean_due_date(self):
        start_date = self.cleaned_data['start_date']
        due_date = self.cleaned_data['due_date']
        if due_date < start_date:
            raise ValidationError('The due date must be posterior to the start date.')

        return due_date

        # pour s'assurer que la priorité de la tache soit comprise entre 1 et 10
    def clean_completion_percentage(self):
        completion_percentage = self.cleaned_data['completion_percentage']
        if completion_percentage < 0 or completion_percentage > 100:
            raise ValidationError('Ensure this value is between 0 % and 100 %')

        return completion_percentage


# form used to select what models to export
class ExportDataForm(forms.Form):
    # 5 boolean fields to select the models
    projects = forms.BooleanField(required=False)
    projects_members = forms.BooleanField(required=False)
    tasks = forms.BooleanField(required=False)
    journals = forms.BooleanField(required=False)
    status = forms.BooleanField(required=False)

    FORMAT_FIELD_CHOICES = [
        ('csv', 'csv'),
        ('json', 'json'),
        ('xml', 'xml'),
        ('xls', 'xls (MS Excel)'),
    ]
    # select field to select among the 4 file formats above
    file_format = forms.ChoiceField(choices=FORMAT_FIELD_CHOICES)

    # check if at least one tick has been put
    def clean(self):
        if self.cleaned_data['projects'] or self.cleaned_data['projects_members'] or self.cleaned_data['tasks'] or \
                self.cleaned_data['journals'] or self.cleaned_data['status']:
            raise ValidationError("Tick at least one")
