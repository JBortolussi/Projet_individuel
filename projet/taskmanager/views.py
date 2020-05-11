import csv
import datetime
import io

from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.core import serializers
from zipfile import ZipFile

from django.db.models import ManyToManyField
from django.http import HttpResponse
from django.shortcuts import render, HttpResponseRedirect, redirect, get_object_or_404
from .forms import ConnexionForm, ProjectForm, JournalForm, TaskForm, ExportDataForm
from django.contrib.auth import authenticate, login, logout
from django.urls import reverse
from django.contrib.auth.decorators import login_required
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
        return redirect("projects")

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
def redir(request):
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

    # Check if the logged in user is allowed to see this project
    if request.user.has_perm('taskmanager.{}_project_permission'.format(project.id)):

        # Retrieve all the task of the project and order them
        tasks = project.task_set.all().order_by('-priority')
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
                return redirect("task", task_id=task.id)
        else:
            # Pass project to the form. Set the task's project fields with this project (initialize and never modify)
            form = TaskForm(project)
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
                task.save()
                return redirect("task", task_id=task.id)
        else:
            # Initialize the form with the task
            form = TaskForm(project, instance=task)
    return render(request, "newtask.html", locals())


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
            return redirect('projects')
    else:
        form = UserCreationForm()
    return render(request, 'signup.html', locals())


@login_required()
def data_selection(request):
    if request.method == 'GET':
        form = ExportDataForm(request.GET)
        if form.is_valid():
            file_format = form.cleaned_data['file_format']
            exp_u = int(form.cleaned_data['user'])
            exp_p = int(form.cleaned_data['projects'])
            exp_t = int(form.cleaned_data['tasks'])
            exp_j = int(form.cleaned_data['journals'])
            exp_s = int(form.cleaned_data['status'])

            return redirect(download_data, file_format, exp_u, exp_p, exp_t, exp_j, exp_s)
    else:
        form = ExportDataForm()
    return render(request, 'data_selection.html', locals())


# this view return a zip file to download containing the models that corresponds to the arguments set to True
@login_required()
def download_data(request, file_format, exp_u=0, exp_p=0, exp_t=0, exp_j=0, exp_s=0):
    # set the response so that the browser will understand that the user is receiving a zip file to download
    response = HttpResponse(content_type='application/zip')
    response['Content-Disposition'] = 'attachment; filename="data.zip"'

    # create the zip file
    data_zip = ZipFile(response, 'w')

    file_format = file_format.lower()  # not to call this too many times after

    # models queryset to be used to generate to export the database
    user = request.user
    user_queryset = User.objects.filter(username=request.user.username)
    projects_queryset = user.projets.all()  # only projects that the user has access to
    tasks_queryset = Task.objects.filter(projet__in=projects_queryset)  # all the tasks in these projects
    journals_queryset = Journal.objects.filter(task__in=tasks_queryset)  # all the journals in these tasks
    status_queryset = Status.objects.all()

    if exp_u:
        dump_to_file_format(user_queryset, file_format, data_zip)
    if exp_p:
        dump_to_file_format(projects_queryset, file_format, data_zip)
    if exp_t:
        dump_to_file_format(tasks_queryset, file_format, data_zip)
    if exp_j:
        dump_to_file_format(journals_queryset, file_format, data_zip)
    if exp_s:
        dump_to_file_format(status_queryset, file_format, data_zip)

    # closes the zip file
    data_zip.close()

    # finally send the zip file as a the response HTTP
    return response

    # '''
    # I preferred not to write this lines as as function to use for each model queryset because each model has some
    # peculiarities and I want to personally handle the csv files formatting
    # '''
    # # if the user wants to export his personal data
    # # if exp_u:
    # #     # create a temporary stream output (temp file)
    # #     output = io.StringIO()  # temporary stream output
    # #     # the following depends on the file format chosen
    # #
    # #     if file_format == 'csv':
    # #         # create an instance of csv writer that writes on the stream 'output' opened above
    # #         csv_user = csv.writer(output, dialect='excel', delimiter=';')
    # #         csv_user.writerow(['USERNAME', 'NAME', 'SURNAME', 'E-MAIL'])
    # #         # write the informations on the csv
    # #         csv_user.writerow([user.username, user.first_name, user.last_name, user.email])
    # #     elif file_format == 'json' or file_format == 'xml':
    # #         # uses django serialization to serialize in 'json' or 'xml'
    # #         json_xml_user = serializers.serialize(file_format, [user],
    # #                                               fields=('username', 'first_name', 'last_name', 'email'),
    # #                                               use_natural_primary_keys=True)  # uses the username as primary key
    # #         # write on the output stream
    # #         output.write(json_xml_user)
    # #
    # #     # add the extension to the file name
    # #     file_name = 'user_data.' + file_format
    # #     # write the file generated from the output stream to the zip file generated in the beginning
    # #     data_zip.writestr(file_name, output.getvalue())
    # #     # in the end close the output stream
    # #     output.close()
    # #
    # # '''
    # # in the next lines, the steps to generate the files for the different models are always the same
    # # I didn't find a way to make it shorter because each models has its own particularities
    # # The things that are a bit different will be highlighted
    # # '''
    # # # if the user requires his projects
    # # if exp_p:
    # #     output = io.StringIO()
    # #     if file_format == 'csv':
    # #         csv_projects = csv.writer(output, dialect='excel', delimiter=';')
    # #         csv_projects.writerow(['NAME', 'MEMBERS', 'TASKS'])
    # #         for project in projects_queryset:
    # #             # build a comma separated list with all the users and the tasks that are in the project
    # #             members = ', '.join([member.username for member in project.members.all()])
    # #             # the tasks are included for the sake of completeness, even if it is not an attribute of the model
    # #             tasks = ', '.join([task.name for task in project.task_set.all()])
    # #             csv_projects.writerow([project.name, members, tasks])
    # #     elif file_format == 'json' or file_format == 'xml':
    # #         json_xml_projects = serializers.serialize(file_format, projects_queryset,
    # #                                                   use_natural_foreign_keys=True,  # foreign keys not as numbers
    # #                                                   use_natural_primary_keys=True)  # project name used as primary key
    # #         output.write(json_xml_projects)
    # #
    # #     file_name = 'projects_data.' + file_format
    # #     data_zip.writestr(file_name, output.getvalue())
    # #     output.close()
    # #
    # # # if the user requires all the tasks in his projects
    # # if exp_t:
    # #     output = io.StringIO()
    # #     if file_format == 'csv':
    # #         csv_tasks = csv.writer(output, dialect='excel', delimiter=';')
    # #         csv_tasks.writerow(
    # #             ['PROJECT', 'NAME', 'ASSIGNED TO', 'STATUS', 'PRIORITY', 'START DATE', 'DUE DATE', 'DESCRIPTION'])
    # #         for task in tasks_queryset:
    # #             # note that the date are converted into strings with strftime() (in an appropriate format)
    # #             task_data = [task.projet, task.name, task.assignee, task.status, task.priority,
    # #                          task.start_date.strftime("%m/%d/%Y"), task.due_date.strftime("%m/%d/%Y"), task.description]
    # #             csv_tasks.writerow(task_data)
    # #     elif file_format == 'json' or file_format == 'xml':
    # #         json_xml_tasks = serializers.serialize(file_format, tasks_queryset, use_natural_foreign_keys=True,
    # #                                                use_natural_primary_keys=True)
    # #         output.write(json_xml_tasks)
    # #
    # #     file_name = 'tasks_data.' + file_format
    # #     data_zip.writestr(file_name, output.getvalue())
    # #     output.close()
    # #
    # #     # if the user requires all the journals of the tasks in his projects
    # # if exp_j:
    # #     output = io.StringIO()
    # #     if file_format == 'csv':
    # #         csv_journals = csv.writer(output, dialect='excel', delimiter=';')
    # #         csv_journals.writerow(['PROJECT', 'TASK', 'DATE', 'AUTHOR', 'ENTRY'])
    # #         for journal in journals_queryset:
    # #             # note that:
    # #             # 1. the datetime is converted in a proper way into a string
    # #             # 2. also the information on the project is included
    # #             journal_data = [journal.task.projet, journal.task, journal.date.strftime("%m/%d/%Y, %H:%M:%S"),
    # #                             journal.author, journal.entry]
    # #             csv_journals.writerow(journal_data)
    # #     elif file_format == 'json' or file_format == 'xml':
    # #         json_xml_journals = serializers.serialize(file_format, journals_queryset, use_natural_foreign_keys=True,
    # #                                                   use_natural_primary_keys=True)
    # #         output.write(json_xml_journals)
    # #
    # #     file_name = 'journals_data.' + file_format
    # #     data_zip.writestr(file_name, output.getvalue())  # write csv file to zip
    # #     output.close()
    # #
    # # # if the user requires the status'
    # # if exp_s:
    # #     # this queryset does not depend on the others above
    # #     status_queryset = Status.objects.all()
    # #     output = io.StringIO()
    # #     if file_format == 'csv':
    # #         csv_status = csv.writer(output, dialect='excel', delimiter=';')
    # #         csv_status.writerow(['NAME'])
    # #         for status in status_queryset:
    # #             status_data = [status.name]
    # #             csv_status.writerow(status_data)
    # #     elif file_format == 'json' or file_format == 'xml':
    # #         json_xml_status = serializers.serialize(file_format, status_queryset, use_natural_primary_keys=True)
    # #         output.write(json_xml_status)
    # #
    # #     file_name = 'status_data.' + file_format
    # #     data_zip.writestr(file_name, output.getvalue())
    # #     output.close()
    # #



def dump_to_file_format(queryset, file_format, data_zip):
    output = io.StringIO()
    # get queryset model
    model = queryset.model
    if file_format == 'csv':
        csv_writer = csv.writer(output, dialect='excel', delimiter=';')
        if model == Projet:
            csv_writer.writerow(['ID', 'NAME', 'MEMBERS'])
            for project in queryset:
                # build a comma separated list with all the users and the tasks that are in the project
                members = ', '.join([member.username for member in project.members.all()])
                csv_writer.writerow([project.id, project.name, members])
        else:
            field_names = [field.name for field in model._meta.fields]
            csv_writer.writerow(field.upper() for field in field_names)
            for obj in queryset:
                csv_writer.writerow([getattr(obj, field) for field in field_names])
                # print([getattr(obj, field) for field in field_names])
                # row = []
                # for field in field_names:
                #     field_value = getattr(obj, field)
                #     # if isinstance(field_value, datetime):
                #     # #     field_value = field_value.strftime("%m/%d/%Y, %H:%M:%S")
                #     row.append(field_value)
                # csv_writer.writerow(row)
                # print(row)

    elif file_format == 'json' or file_format == 'xml':
        json_xml_projects = serializers.serialize(file_format, queryset, use_natural_foreign_keys=True,
                                                  use_natural_primary_keys=True)
        output.write(json_xml_projects)

    file_name = model._meta.model.__name__.lower() + '_data.' + file_format
    data_zip.writestr(file_name, output.getvalue())
    output.close()