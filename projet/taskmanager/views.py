from django.contrib.auth.models import User
from django.shortcuts import render, HttpResponseRedirect, redirect, get_object_or_404
from .forms import ConnexionForm, ProjectForm, JournalForm, TaskForm
from django.contrib.auth import authenticate, login, logout
from django.urls import reverse
from django.contrib.auth.decorators import login_required

# Create your views here.
from .models import Projet, Task, Journal, Status


def connexion(request):
    """View for the connexion page

    This view handel the treatment the the connexion form.
    If the log in process is successful, redirect the user to the project list page

    :param request: the request data, include the form data if an user tried to logged in
    :return: Either the connexion HttpResponse or the redirection to the project list page if the user logged in
    """

    # If true an error will be displayed
    error = False

    # No need to use connexion method if already logged in
    if request.user.is_authenticated:
        return redirect("project")

    # Someone try to connected and had sent a form
    if request.method == "POST":
        # retrieve the user's data
        form = ConnexionForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data["username"]
            password = form.cleaned_data["password"]
            # Test if the user can be log in
            user = authenticate(username=username, password=password)
            # Success
            if user:
                # Actually log the user in
                login(request, user)
                return redirect("projects")
            # Failure
            else:
                error = True
    # A new user open the connexion view
    else:
        form = ConnexionForm()

    return render(request, 'connexion.html', locals())


def deconnexion(request):
    """Handel the log out process

    :param request: the request data, shall include the logged user's data (no error if not)
    :return: Redirect to the connexion page
    """
    logout(request)
    return HttpResponseRedirect(reverse(connexion))


@login_required()
def projects_view(request):
    """The for the display project list page"""

    # The projects to be displayed. Only ones in witch the logged in user is involved
    projects = request.user.projets.all()
    return render(request, 'projects.html', locals())


@login_required()
def newproject_view(request):
    """View for the newProject page

    This view handel the treatment of the newproject form
    

    :param request:
    :return:
    """

    is_new = True
    users = User.objects.all()
    if request.method == "POST":
        form = ProjectForm(request.user, request.POST)
        if form.is_valid():
            form.save(commit=True)
            return redirect("projects")
    else:
        form = ProjectForm(request.user)

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


@login_required()
def project_view(request, id):
    project = get_object_or_404(Projet, id=id)
    if request.user.has_perm('taskmanager.{}_project_permission'.format(project.id)):
        tasks = Task.objects.filter(projet__id__exact=project.id).order_by('-priority')
        return render(request, 'project.html', locals())
    else:
        return redirect("projects")


@login_required()
def task_view(request, task_id):
    task = get_object_or_404(Task, id=task_id)
    project = task.projet
    if request.user.has_perm('taskmanager.{}_project_permission'.format(project.id)):
        entries = Journal.objects.filter(task__id=task_id)
        if (request.method == "POST"):
            form = JournalForm(request.POST)
            if (form.is_valid()):
                journal = form.save(commit=False)
                journal.task = task
                journal.author = request.user
                journal.save()
        else:

            form = JournalForm()
        return render(request, "task.html", locals())
    else:
        return redirect("project", id=project.id)


@login_required()
def newtask_view(request, project_id):
    is_new = True
    project = get_object_or_404(Projet, id=project_id)
    members = project.members.all()
    status = Status.objects.all()
    if request.user.has_perm('taskmanager.{}_project_permission'.format(project.id)):
        if request.method == "POST":
            form = TaskForm(project, request.POST)
            print(request.POST['start_date'])
            if form.is_valid():
                task = form.save(commit=True)
                return redirect("task", task_id=task.id)
        else:
            form = TaskForm(project)
    return render(request, "newtask.html", locals())


@login_required()
def edittask_view(request, task_id):
    is_new = False
    task = get_object_or_404(Task, id=task_id)
    project = task.projet
    if request.user.has_perm('taskmanager.{}_project_permission'.format(project.id)):
        if request.method == "POST":
            form = TaskForm(project, request.POST)
            print(request.POST['start_date'])
            if form.is_valid():
                task = form.save(commit=False)
                task.id = task_id
                task.save()
                return redirect("task", task_id=task.id)
        else:
            form = TaskForm(project, instance=task)
    return render(request, "newtask.html", locals())
