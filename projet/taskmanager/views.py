# python modules
import csv
import datetime
import io
import xlwt
from zipfile import ZipFile

# django modules and functions
from django.contrib import messages
from django.core import serializers
from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required

# models
from django.contrib.auth.models import User
from django.db.models import Q
from .models import Projet, Task, Journal, Status

# forms
from django.contrib.auth.forms import UserCreationForm
from .forms import ProjectForm, JournalForm, TaskForm, ExportDataForm


# redirect to the projects list page if the url requested is just http://localhost:8000/
@login_required()
def redir(request):
    return redirect('projects')


@login_required()
def projects_view(request):
    """The view for the project list display page"""

    # The projects to be displayed. Only the ones in which the logged in user is involved
    projects = request.user.projets.all().order_by('name')
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

                # update the last modification DateTime of the Task instance
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
                task.last_modification = datetime.datetime.now() # it's probably not necessary
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
    tasks = project.task_set.order_by('-last_modification')

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


@login_required()
def data_selection(request):
    """
    This view contains a form that allows the user to select the data to export. After that the form has caught the
    user choices, it calls the function (or view) 'download_data' defined below
    """

    # get because I do not want to upload data into the database
    if request.method == 'GET':
        form = ExportDataForm(request.GET)
        if form.is_valid():
            # parameteres passed to 'download_data'
            file_format = form.cleaned_data['file_format']
            exp_m = form.cleaned_data['projects_members']
            exp_p = form.cleaned_data['projects']
            exp_t = form.cleaned_data['tasks']
            exp_j = form.cleaned_data['journals']
            exp_s = form.cleaned_data['status']

            return download_data(request, file_format, exp_p, exp_m, exp_t, exp_j, exp_s)
    else:
        form = ExportDataForm()
    return render(request, 'data_selection.html', locals())


@login_required()
def download_data(request, file_format, exp_p=False, exp_m=False, exp_t=False, exp_j=False, exp_s=False,
                  querysets=None):
    """ This view generates a zip file containing all the data required by the user.
    I tried to write a function as general as possible: it can either export all the data or some of the data
    that the AUTHENTICATED USER has access to, or export a general QUERYSET made by instances of the model of this app

    :param request:
    :param file_format: among .csv, .json, .xml, .xls (MS-Excel)
    :param exp_t, exp_m, exp_t, exp_j, exp_s: booleans, allows to select wheter to export projects, projects members,
                                                projects tasks, tasks journals or status models
                                                (a particular USER can export ONLY the data of the projects of which he/
                                                she is a member)

    :param querysets: a list of queryset (can be passed from whatever view to export the data)

    : return: the zip file containing the data
    """

    # set the response so that the browser will understand that the user is receiving a zip file to download
    response = HttpResponse(content_type='application/zip')
    response['Content-Disposition'] = 'attachment; filename="data.zip"'

    # create the zip archive by using the python library ZipFile
    data_zip = ZipFile(response, 'w')

    file_format = file_format.lower()  # it may be helpful

    """ ONLY the data that refers to the projects of which the AUTHENTICATED USER is MEMBER will be exported"""
    user = request.user
    # models queryset to be used to generate to export the database
    projects_queryset = user.projets.all()  # only projects that the user has access to
    projects_members_queryset = User.objects.filter(
        projets__in=projects_queryset).distinct()  # infos about project members
    tasks_queryset = Task.objects.filter(projet__in=projects_queryset)  # all the tasks in these projects
    journals_queryset = Journal.objects.filter(task__in=tasks_queryset)  # all the journals in these tasks
    status_queryset = Status.objects.all()

    def dump_to_file_format(queryset, file_format, data_zip):
        """ Subfunction used not to repeat the same code for the export process

        :param queryset: a generic queryset of a model
        :param file_format:
        :param data_zip: a zip archive

        """
        # create a temporary  output stream (temp file)
        if file_format == 'xls':
            # it seems that an excel file needs to be written on a BytesIo even if on the xlwt they write exactly
            # the opposite (I was about to become fool)
            output = io.BytesIO()
        else:
            output = io.StringIO()
        # get queryset model
        model = queryset.model
        # the export code depends on the file format
        if file_format == 'csv':
            # create an instance of csv writer that writes on the stream 'output' opened above
            csv_writer = csv.writer(output, dialect='excel', delimiter=';')

            # there are some things that may be different from a model to another

            # for example, I also want to write in the project csv the username of the members
            if model == Projet:
                csv_writer.writerow(['ID', 'NAME', 'MEMBERS'])
                for project in queryset:
                    # build a comma separated list with all the users and the tasks that are in the project
                    members = ', '.join([member.username for member in project.members.all()])
                    csv_writer.writerow([project.id, project.name, members])
            # if the model is User, only export non confidential fields
            if model == User:
                csv_writer.writerow(['USERNAME', 'NAME', 'SURNAME', 'E-MAIL'])
                for user in queryset:
                    csv_writer.writerow([user.username, user.first_name, user.last_name, user.email])
            # for the other models that's what is going to happen
            else:
                # get all the field names and write them as headers
                field_names = [field.name for field in model._meta.fields]
                csv_writer.writerow(field.upper() for field in field_names)
                # for each instance in the queryset
                for obj in queryset:
                    # """general backup code"""
                    # csv_writer.writerow([getattr(obj, field) for field in field_names])

                    row = []  # create an empty row list
                    # for each field of the model
                    for field in field_names:
                        # get the field value
                        field_value = getattr(obj, field)
                        # this is to control the format of the date that will be written in the csv
                        if isinstance(field_value, datetime.datetime):
                            field_value = field_value.strftime("%m/%d/%Y, %H:%M:%S")
                        row.append(field_value)  # append the field value to the end of the row list

                    csv_writer.writerow(row)

        # the .json and .xml formats are generated with the django serializers utilities
        elif file_format == 'json' or file_format == 'xml':
            # if the model is User, only export non confidential fields
            if model == User:
                json_xml = serializers.serialize(file_format, queryset, use_natural_foreign_keys=True,
                                                 fields=('username', 'first_name', 'last_name', 'email'))
            else:
                # use_natural_foreign_keys=True means that the foreign keys won't be written as just numbers
                json_xml = serializers.serialize(file_format, queryset, use_natural_foreign_keys=True)

            output.write(json_xml)

        elif file_format == 'xls':
            wb = xlwt.Workbook(encoding='utf-8')  # create excel workbook
            ws = wb.add_sheet(model._meta.model.__name__)  # create sheet

            # Sheet header, first row
            row_num = 0
            font_style = xlwt.XFStyle()
            font_style.font.bold = True

            '''This code is pretty similar to the code to export in .csv, but in excel each cell (row and column) 
            must written separately'''
            # get all the field names and write them as headers
            # if User only confidential data
            if model == User:
                field_names = ['username', 'first_name', 'last_name', 'email']
            else:
                field_names = [field.name for field in model._meta.fields]
            for col_num in range(len(field_names)):
                ws.write(row_num, col_num, field_names[col_num].upper(), font_style)

            # add a column for the members of the project
            if model == Projet:
                ws.write(row_num, col_num + 1, 'MEMBERS', font_style)

            # Sheet body, remaining rows
            font_style = xlwt.XFStyle()

            # for each instance in the queryset
            for obj in queryset:
                row_num += 1
                # for each field of the model
                for col_num in range(len(field_names)):
                    # get the field value
                    field_value = getattr(obj, field_names[col_num])
                    # this is to control the format of the date that will be written in the csv
                    if isinstance(field_value, datetime.datetime):
                        field_value = field_value.strftime("%m/%d/%Y, %H:%M:%S")
                    ws.write(row_num, col_num, field_value.__str__(), font_style)

                # add the column with the members of the project
                if model == Projet:
                    members = ', '.join([member.username for member in obj.members.all()])
                    ws.write(row_num, col_num + 1, members, font_style)

            # save the excel file on the output stream
            wb.save(output)

        # generates the name of the output file depending on the model and the file format
        file_name = model._meta.model.__name__.lower() + '_data.' + file_format
        # add the file to the zip archive and close the output stream
        data_zip.writestr(file_name, output.getvalue())
        output.close()

    '''
    uses the function defined above the export the data
    '''
    if exp_p:
        dump_to_file_format(projects_queryset, file_format, data_zip)
    if exp_m:
        dump_to_file_format(projects_members_queryset, file_format, data_zip)
    if exp_t:
        dump_to_file_format(tasks_queryset, file_format, data_zip)
    if exp_j:
        dump_to_file_format(journals_queryset, file_format, data_zip)
    if exp_s:
        dump_to_file_format(status_queryset, file_format, data_zip)

    # it is also possible to pass whatever list of querysets to this function
    if not querysets is None:
        for queryset in querysets:
            dump_to_file_format(queryset, file_format, data_zip)

    # closes the zip file
    data_zip.close()

    # finally send the zip file as a the HTTP response
    return response
