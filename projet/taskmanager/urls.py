from django.urls import path
from . import views

urlpatterns = [
    path('connexion/', views.connexion, name="connexion"),
    path('deconnexion/', views.deconnexion, name="deconnexion"),
    path('projects/', views.projects_view, name="projects"),
    path('projects/newproject', views.newproject_view, name="new_project"),
    path('projects/delete/<int:id>', views.delete_project_view, name="delete_project"),
    path('projects/edit/<int:project_id>', views.edit_project_view, name="edit_project"),
    path('project/<int:project_id>', views.project_view, name="project"),
    path('task/<int:task_id>', views.task_view, name="task"),
    path('newtask/<project_id>', views.newtask_view, name="newtask"),
    path('edittask/<task_id>', views.edittask_view, name="edittask"),
]