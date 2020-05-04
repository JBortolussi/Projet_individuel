from datetime import datetime
from itertools import chain

from django import forms
from django.contrib.auth.models import User
from django.db.models import QuerySet
from django.forms import DateInput

from .models import Projet, Journal, Task, Status
from django.db.models import Q


class ConnexionForm(forms.Form):
    username = forms.CharField(label="Nom d'utilisateur", max_length=30)
    password = forms.CharField(label="Mot de passe", widget=forms.PasswordInput)


class ProjectForm(forms.ModelForm):
    def __init__(self, user, *args, **kwargs):
        self.user = user
        super().__init__(*args, **kwargs)
        self.fields['name'].label = "Nom du projet"
        self.fields['name'].widget.attrs.update({'class': 'form-control', 'placeholder': "Nom du projet"})
        self.fields['members'].label = "Membres du projet"
        self.fields['members'].widget.attrs.update({'class': 'form-control'})
        self.fields['members'].initial = user

    class Meta:
        model = Projet
        exclude = ('',)

    def clean_members(self):
        members = self.cleaned_data['members']
        if (not self.user in members):
            members = User.objects.filter(Q(id__in=members) | Q(username__exact=self.user.username))
        return members

class JournalForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super(JournalForm, self).__init__(*args, **kwargs)
        self.fields['entry'].widget.attrs.update({'class': 'form-control'})

    class Meta:
        model = Journal
        exclude = ('task', 'date', 'author')


class TaskForm(forms.ModelForm):
    def __init__(self,project, *args, **kwargs):
        assignee_choices = [(member.id, member.username) for member in project.members.all()]
        super(TaskForm, self).__init__(*args, **kwargs)
        self.fields['assignee'].label = "Assignée à :"
        self.fields['assignee'].widget.attrs.update({'class': 'form-control'})
        self.fields['assignee'].choices = assignee_choices
        self.fields['name'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Nom de la tâche'})
        self.fields['description'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Description de la tache', 'rows': 4})
        self.fields['start_date'].widget.attrs.update({'class': 'form-control',})
        self.fields['start_date'].initial = datetime.now().strftime("%Y-%m-%d")
        self.fields['due_date'].widget.attrs.update({'class': 'form-control'})
        self.fields['status'].widget.attrs.update({'class': 'form-control'})
        self.fields['priority'].widget.attrs.update({'class': 'form-control'})
        self.fields['priority'].initial = 1
        self.fields['projet'].widget.attrs.update({'style': 'display: none'})
        if Status.objects.filter(name="Nouvelle"):
            self.fields['status'].initial = Status.objects.filter(name="Nouvelle")[0]

    class Meta:
        model = Task
        exclude = ('',)
        widgets = {
            'start_date': DateInput(format=('%Y-%m-%d'), attrs={'type': 'date'}),
            'due_date': DateInput(format=('%Y-%m-%d'), attrs={'type': 'date'})
        }
