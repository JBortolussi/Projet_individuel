import datetime

from django.contrib import messages
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.db.models import Q
from django.shortcuts import render, redirect, get_object_or_404
from .forms import ProjectForm, JournalForm, TaskForm
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from .models import Projet, Task, Journal, Status


@login_required()
def redir():
    return redirect('projects')


@login_required()
def projects_view(request):
    """The for the project list display page"""

    # The projects to be displayed. Only ones in witch the logged in user is involved
    projects = request.user.projets.all()
    return render(request, 'projects.html', locals())


@login_required()
def newproject_view(request):
    """View for the newProject page

    This view handel the treatment of the newproject form
    Creat a new project based on the form's data. The logged in user will always be part of the project

    :param request: The request data. An user need to be logged in order to creat a project
    :return: The HttpResponse for the new project templates or redirect to the project list page if a project have been
    created
    """

    # Use to tell to the template that the user want to creat a new project
    is_new = True

    # Get all the user. Everyone may be member of the project
    users = User.objects.all()

    # If the view received data, try to creat a project
    if request.method == "POST":
        form = ProjectForm(request.user, request.POST)
        if form.is_valid():
            # Save the new project in the database
            form.save(commit=True)

            # redirect to the project list display page
            return redirect("projects")
    else:
        # creat an empty form for the template
        form = ProjectForm(request.user)

    return render(request, 'newProject.html', locals())


@login_required()
def delete_project_view(request, id):
    """The project deletion view

    This view handle the deletion of a project. Check if the logged in user is allowed to delete the project

    :param request:
    :param id: The id of the project to be deleted
    :return: Allays redirect to the project list display page
    """

    # retrieve the project to be deleted through his id. Raise an error if the project does not exist
    project = get_object_or_404(Projet, id=id)

    # Check if the logged in user is allowed to delete this project
    if request.user.has_perm('taskmanager.{}_project_permission'.format(project.id)):

        # Eventually delete the project
        project.delete()

    return redirect("projects")


@login_required()
def edit_project_view(request, project_id):
    """The project creation view

    This view handel the project edition form. Check if the logged in user is allowed to edit this project

    :param request:
    :param project_id: The id of the project to edited
    :return: Either HttpResponse for the edition template (same as creation) or redirect to project list display page if
     the project has been successfully edited
    """

    # Use to tell to the template that the user want to edit a project
    is_new = False

    # Retrieve the project to be edited or raise an error if this project does not exist
    project = get_object_or_404(Projet, id=project_id)

    # Check if the logged in user is allowed to edit this project
    if request.user.has_perm('taskmanager.{}_project_permission'.format(project.id)):

        # Check if the view receive data from the form
        if request.method == "POST":
            form = ProjectForm(request.user, request.POST)
            if form.is_valid():
                # Manually update the field using the data from form
                project.name = form.cleaned_data["name"]
                project.members.set(form.cleaned_data["members"])
                # Save the project. Does not creat a new project as long as the project's id is not modified
                project.save()
                return redirect("projects")
        else:
            form = ProjectForm(user=request.user, instance=project)
        return render(request, 'newProject.html', locals())
    else:
        return redirect("projects")

    return redirect("projects")


@login_required()
def project_view(request, project_id):
    """The project display view

    This view handel the template witch display the projects details.

    :param request:
    :param project_id: The id of the project to be displayed
    :return: Either a HttpResponse for the project template or redirect to the project list page if the user is not
    allowed to see this project
    """



    # Retrieve the project to to be displayed. Raise an error if this project does not exist
    project = get_object_or_404(Projet, id=project_id)

    if request.method == 'GET':
        print(request.GET)

        filters = Q()

        for key in request.GET:
            entry = request.GET.getlist(key)

            method = entry[0]
            value = entry[1]
            link = entry[2]

            if method == 'assign':
                if link == "and":
                    filters &= Q(assignee__id=value)
                else:
                    filters |= Q(assignee__id=value)
            elif method == 'not_assign':
                if link == "and":
                    filters &= ~Q(assignee__id=value)
                else:
                    filters |= ~Q(assignee__id=value)

        tasks = project.task_set.filter(filters).order_by('-priority')
    else:
        # Retrieve all the task of the project and order them
        tasks = project.task_set.all().order_by('-priority')


    # Check if the logged in user is allowed to see this project
    if request.user.has_perm('taskmanager.{}_project_permission'.format(project.id)):
        users = project.members.all()
        return render(request, 'project.html', locals())
    else:
        return redirect("projects")


@login_required()
def task_view(request, task_id):
    """The task page view

    This page display task's details such as his name and his status.
    It also display all the journal entries linked with this project
    and handel the Journal Form. So that can user can add a new entry to the project's journal

    :param request:
    :param task_id: The id of the task to be displayed
    :return: Always render the task page, except when the user logged in is not allowed to see this task
    """

    # retrieve the task, raise an error if the task does not exist
    task = get_object_or_404(Task, id=task_id)
    project = task.projet
    # Check if the logged in user is allowed to see this task
    if request.user.has_perm('taskmanager.{}_project_permission'.format(project.id)):
        # Check if a form has been submitted
        if request.method == "POST":

            # Build the form and verify it
            form = JournalForm(request.POST)
            if form.is_valid():

                # Save the Journal and set the project and author fields
                journal = form.save(commit=False)  # Does not save the Journal in the database
                journal.task = task
                journal.author = request.user
                journal.save()

                task.last_modification = datetime.datetime.now()
                task.save()
        else:
            # initialize a new form
            form = JournalForm()
        # Get the Journal entries linked with the task
        entries = Journal.objects.filter(task__id=task_id)
        return render(request, "task.html", locals())
    else:
        # redirect to the linked project to the project list page if the user is not allowed to see the task
        return redirect("projects")


@login_required()
def newtask_view(request, project_id):
    """The new task page view

    This view handel the task creation template and form.
    Check if the logged in user is allowed to add a task to the project

    :param request:
    :param project_id: The project to which the task will be linked
    :return: Either task page if a task have been created or the creation task page if not
    """
    # Use to tell to the template that user want to creat a new task
    is_new = True

    # Retrieve the task, raise an error if the task does not exist
    project = get_object_or_404(Projet, id=project_id)

    # Check if the user is allowed to add a task to this project
    if request.user.has_perm('taskmanager.{}_project_permission'.format(project.id)):

        # Check if a form has been submitted
        if request.method == "POST":
            # Pass project to the form. Set the task's project fields with this project (initialize and never modify)
            form = TaskForm(project, request.POST)
            if form.is_valid():
                task = form.save(commit=True)
                task.last_modification = datetime.datetime.now()
                task.save()
                return redirect("task", task_id=task.id)
        else:
            # Pass project to the form. Set the task's project fields with this project (initialize and never modify)
            form = TaskForm(project)
    else:
        return redirect("projects")
    return render(request, "newtask.html", locals())


@login_required()
def edittask_view(request, task_id):
    """The edit task page view

    Handel the edit task page and form. Check if the logged in user is allowed to modify this task.

    :param request:
    :param task_id: The task to be modified
    :return:
    """

    # Use to tell to the template tha the user want to edit an already existing task
    is_new = False

    # Retrieve the task, raise an error if the task does not exist
    task = get_object_or_404(Task, id=task_id)
    project = task.projet
    # Check if logged in user is allowed to modify the task
    if request.user.has_perm('taskmanager.{}_project_permission'.format(project.id)):
        # Check if the form has been submitted
        if request.method == "POST":
            form = TaskForm(project, request.POST)
            if form.is_valid():
                task = form.save(commit=False)
                # Manually set the project id. Otherwise a new task would be created
                task.id = task_id
                task.last_modification = datetime.datetime.now()
                task.save()
                return redirect("task", task_id=task.id)
        else:
            # Initialize the form with the task
            form = TaskForm(project, instance=task)
    else:
        return redirect("projects")
    return render(request, "newtask.html", locals())


@login_required()
def my_profile(request):

    projects = request.user.projets.all()

    return render(request, "myprofile.html", locals())


@login_required()
def taches_assignees(request):

    tasks = Task.objects.filter(assignee=request.user).exclude(status__name__contains="Finished")

    return render(request, "tachesassignees.html", locals())


@login_required()
def taches_terminees(request):

    tasks = Task.objects.filter(assignee=request.user, status__name__contains="Finished")

    return render(request, "tachesterminees.html", locals())


@login_required()
def taches_projets(request):

    projects = request.user.projets.all()

    return render(request, "tachesprojets.html", locals())

@login_required()
def taches_recents_home(request):

    projects = request.user.projets.all()

    return render(request, "tachesrecentshome.html", locals())


@login_required()
def taches_recents(request, project_id):

    project = get_object_or_404(Projet, id=project_id)
    tasks = project.task_set.all()

    return render(request, "tachesrecents.html", locals())


# Sign up page is the only view which doesn't require a log in for obvious reasons
def signup(request):
    if request.method == 'POST':

        # Form is a existing template imported from the library django.contrib.auth.forms
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            raw_password = form.cleaned_data.get('password1')
            user = authenticate(username=username, password=raw_password)

            # Automatically log in the user once they have signed up and redirect them to the home screen
            login(request, user)
            messages.success(request, 'You have successfully registered and logged in.')
            return redirect('projects')
    else:
        form = UserCreationForm()
    return render(request, 'registration/signup.html', locals())
