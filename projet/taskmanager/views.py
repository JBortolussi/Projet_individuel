from django.contrib.auth.models import User
from django.shortcuts import render, HttpResponseRedirect, redirect, get_object_or_404
from .forms import ConnexionForm, ProjectForm
from django.contrib.auth import authenticate, login, logout
from django.urls import reverse
from django.contrib.auth.decorators import login_required

# Create your views here.
from .models import Projet


def connexion(request):
    error = False
    if (request.user.is_authenticated):
        return redirect("project")

    if request.method == "POST":
        form = ConnexionForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data["username"]
            password = form.cleaned_data["password"]
            user = authenticate(username=username, password=password)  # Nous vérifions si les données sont correctes
            if user:  # Si l'objet renvoyé n'est pas None
                login(request, user)  # nous connectons l'utilisateur
                return redirect("projects")
            else: # sinon une erreur sera affichée
                error = True
    else:
        form = ConnexionForm()
        form.fields["username"] = ""

    return render(request, 'connexion.html', locals())


def deconnexion(request):
    logout(request)
    return HttpResponseRedirect(reverse(connexion))

@login_required()
def project_view(request):
    projects = request.user.projets.all()
    return render(request, 'projects.html', locals())

@login_required()
def newproject_view(request):
    is_new = True
    users = User.objects.all()
    if request.method == "POST":
        form = ProjectForm(request.user, request.POST)
        if form.is_valid():
            form.save(commit=True)
            return redirect("projects")
    else:
        form = ProjectForm(request.user)
        form.fields["name"] = ""

    return render(request, 'newProject.html', locals())


@login_required()
def delete_project_view(request, id):
    project = get_object_or_404(Projet, id=id)
    if request.user.has_perm('taskmanager.{}_project_permission'.format(project.id)):
        project.delete()

    return redirect("projects")


@login_required()
def edit_project_view(request, id):
    is_new = False
    project = get_object_or_404(Projet, id=id)
    if request.user.has_perm('taskmanager.{}_project_permission'.format(project.id)):
        users = User.objects.all()
        if request.method == "POST":
            form = ProjectForm(request.user, request.POST)
            if form.is_valid():
                project.name = form.cleaned_data["name"]
                project.members.set(form.cleaned_data["members"])
                project.save()
                return redirect("projects")
        else:
            form = ProjectForm(user=request.user, instance=project)

        return render(request, 'newProject.html', locals())

    return redirect("projects")

