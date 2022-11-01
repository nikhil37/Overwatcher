from django.urls import path, include
from main import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register_view, name="register"),
    path("verify", views.email_verification, name="email verification"),
    path("project/<int:pid>",views.project, name="project page"),
    path("add/task",views.add_task,name="Add a new task"),
    path("add/issue",views.add_issue,name="Add a new issue"),
    path("add/user",views.user_validation, name="Validate user by admin"),
    path("add/project",views.add_project,name="Start a new project"),
    path("update/task/<int:tid>",views.update_task,name="Update progress of a task"),

]
