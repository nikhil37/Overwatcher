from django.core.management.base import BaseCommand, CommandError
from main.models import user,projects,tasks,issues


class Command(BaseCommand):
    help = "Populate the database"
    def handle(self, *args, **options):
        print("Creating users")
        uo = user.objects.create_user(email="owner@overwatcher.org",password="password",username="owner",first_name="nik",last_name="hil",is_superuser=True,is_staff=True,is_active=True,is_validated=True,is_admin=True)
        ue1 = user.objects.create_user(email="executive1@overwatcher.org",password="password",username="executive1",first_name="ex",last_name="1",is_superuser=False,is_staff=True,is_active=True,is_validated=True,is_admin=True)
        uh1 = user.objects.create_user(email="head1@overwatcher.org",password="password",username="head1",first_name="head",last_name="1",is_superuser=False,is_staff=True,is_active=True,is_validated=True,is_admin=False)
        uh2 = user.objects.create_user(email="head2@overwatcher.org",password="password",username="head2",first_name="head",last_name="2",is_superuser=False,is_staff=True,is_active=True,is_validated=True,is_admin=False)
        un1 = user.objects.create_user(email="normal1@overwatcher.org",password="password",username="normal1",first_name="normal",last_name="1",is_superuser=False,is_staff=False,is_active=True,is_validated=True,is_admin=False)
        un2 = user.objects.create_user(email="normal2@overwatcher.org",password="password",username="normal2",first_name="normal",last_name="2",is_superuser=False,is_staff=False,is_active=True,is_validated=True,is_admin=False)
        un3 = user.objects.create_user(email="normal3@overwatcher.org",password="password",username="normal3",first_name="normal",last_name="3",is_superuser=False,is_staff=False,is_active=True,is_validated=True,is_admin=False)
        uv1 = user.objects.create_user(email="unverified1@overwatcher.org",password="password",username="unverified1",first_name="unverified",last_name="1",is_superuser=False,is_staff=False,is_active=True,is_validated=False,is_admin=False)
        uv2 = user.objects.create_user(email="unverified2@overwatcher.org",password="password",username="unverified2",first_name="unverified",last_name="2",is_superuser=False,is_staff=False,is_active=True,is_validated=False,is_admin=False)
        print("Users created")
        print("Creating projects")
        p1 = projects.objects.create(title="project1",description="Test project 1",head=uh1,progress="Yet to start")
        p1.assigned_to.add(uh1)
        p1.assigned_to.add(un1)
        p1.assigned_to.add(un2)
        p1.assigned_to.add(un3)
        p2 = projects.objects.create(title="project2",description="Test project 2",head=uh2,progress="Yet to start")
        p1.assigned_to.add(uh2)
        print("Projects created")
        print("Creating tasks")
        t1 = tasks.objects.create(pid=p1,content="Test Task 1 project1",assigned_by=uh1,assigned_to=un1,progress="Yet to start")
        t2 = tasks.objects.create(pid=p1,content="Test Task 2 project1",assigned_by=uh1,assigned_to=un2,progress="Yet to start")
        t3 = tasks.objects.create(pid=p1,content="Test Task 3 project1",assigned_by=uh1,assigned_to=un3,progress="Yet to start")
        t4 = tasks.objects.create(pid=p1,content="Test Task 4 project1",assigned_by=uh1,assigned_to=un1,progress="Yet to start")
        t5 = tasks.objects.create(pid=p1,content="Test Task 5 project1",assigned_by=uh1,assigned_to=un2,progress="Yet to start")
        print("Tasks created")
        print("Creating issues")
        i1 = issues.objects.create(content="Issue 1 Task 1",tid = t1,assigned_to= t1.assigned_to,assigned_by=un2,t_content=t1.content)
        i2 = issues.objects.create(content="Issue 2 Task 3",tid = t3,assigned_to= t3.assigned_to,assigned_by=uh1,t_content=t3.content)
        i3 = issues.objects.create(content="Issue 3 Task 3",tid = t3,assigned_to= t3.assigned_to,assigned_by=uh1,t_content=t3.content)
        print("Issues created")
