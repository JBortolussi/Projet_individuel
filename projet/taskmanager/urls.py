from django.urls import path
from . import views

urlpatterns = [
    path('', views.redir, name="redirect"),
    # path('connexion/', views.connexion, name="connexion"),    # generic views added
    # path('deconnexion/', views.deconnexion, name="deconnexion"),
    path('signup/', views.signup, name="signup"),
    path('projects/', views.projects_view, name="projects"),
    path('projects/newproject', views.newproject_view, name="new_project"),
    path('projects/delete/<int:id>', views.delete_project_view, name="delete_project"),
    path('projects/edit/<int:project_id>', views.edit_project_view, name="edit_project"),
    path('project/<int:project_id>', views.project_view, name="project"),
    path('task/<int:task_id>', views.task_view, name="task"),
    path('newtask/<project_id>', views.newtask_view, name="newtask"),
    path('edittask/<task_id>', views.edittask_view, name="edittask"),
    path('myprofile/1', views.my_profile, name="myprofile"),
    path('myprofile/2', views.taches_assignees, name="taches_assignees"),
]