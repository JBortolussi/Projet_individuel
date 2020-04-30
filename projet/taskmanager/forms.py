from itertools import chain

from django import forms
from django.contrib.auth.models import User
from django.db.models import QuerySet

from .models import Projet, Journal, Task
from django.db.models import Q


class ConnexionForm(forms.Form):
    username = forms.CharField(label="Nom d'utilisateur", max_length=30)
    password = forms.CharField(label="Mot de passe", widget=forms.PasswordInput)


class ProjectForm(forms.ModelForm):
    def __init__(self, user, *args, **kwargs):
        self.user = user
        super().__init__(*args, **kwargs)

    class Meta:
        model = Projet
        exclude = ('',)

    def clean_members(self):
        members = self.cleaned_data['members']
        print(members)
        if (not self.user in members):
            members = User.objects.filter(Q(id__in=members) | Q(username__exact=self.user.username))
        print(members)
        return members

class JournalForm(forms.ModelForm):

    # def __init__(self, user, task, *args, **kwargs):
    #     super().__init__(*args, **kwargs)
    #     self.fields["author"] = user
    #     self.fields["task"] = task

    class Meta:
        model = Journal
        exclude = ('task', 'date', 'author')