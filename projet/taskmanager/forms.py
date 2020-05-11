from datetime import datetime

from django import forms
from django.core.exceptions import ValidationError
from django.forms import DateInput

from .models import Projet, Journal, Task, Status



class ConnexionForm(forms.Form):
    """Form for the connection page

    Set up the style properties
    """

    def __init__(self, *args, **kwargs):
        super(ConnexionForm, self).__init__(*args, **kwargs)

        # Set up the style properties
        self.fields['username'].label = "Nom d'utilisateur"
        self.fields['username'].widget.attrs.update({'class': 'form-control', 'placeholder': "Nom du d'utilisateur"})
        self.fields['password'].label = "Mot de passe"
        self.fields['password'].widget.attrs.update({'class': 'form-control', 'placeholder': "Mot de passe"})

    username = forms.CharField(label="Nom d'utilisateur", max_length=30)
    password = forms.CharField(label="Mot de passe", widget=forms.PasswordInput)


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


class ExportDataForm(forms.Form):
    user = forms.BooleanField(required=False)
    projects = forms.BooleanField(required=False)
    tasks = forms.BooleanField(required=False)
    journals = forms.BooleanField(required=False)
    status = forms.BooleanField(required=False)

    FORMAT_FIELD_CHOICES = [
        ('CSV', 'csv'),
        ('JSON', 'json'),
        ('XML', 'xml'),
        ('XLS', 'xls (MS Excel)'),
    ]
    file_format = forms.ChoiceField(choices=FORMAT_FIELD_CHOICES)