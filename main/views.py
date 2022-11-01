from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, authenticate, logout, get_user_model
from django.utils.datastructures import MultiValueDictKeyError
from django.core.mail import BadHeaderError, send_mail
from django.template.loader import render_to_string
from django.http import HttpResponse,Http404,JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from time import ctime
from hashlib import md5
from main.models import user,tasks,projects,issues


progress_choices = ["Yet to start","In Progress","On-Hold","Testing","Fixing bugs","Under Review","Completed","Released",]


def send_email(u, h, email, domain):
    print("sending now")
    to_email = email
    message = render_to_string("confirmation_email.html", {"link": f"http://{domain}/?e={u}&v={h}"})
    subject = "Confirm Email and Activate account"
    from_email = settings.EMAIL_HOST_USER
    send_mail(subject=subject,message=message,from_email=from_email,recipient_list=[to_email],fail_silently=False,)


@login_required
def index(request):
    if request.user.email_validated == False and settings.EMAIL_VERIFICATION:
        return render(request, "not_confirmed.html")
    if request.user.is_validated == False:
        return render(request, "not_validated.html")
    if request.user.is_staff == False: # normal user
        tasks_obj = tasks.objects.filter(assigned_to=request.user)
        projects_obj = projects.objects.filter(assigned_to__username=request.user.username)
        issues_obj = issues.objects.filter(assigned_to=request.user)
        users_obj = user.objects.filter(is_validated = True)
        if len(projects_obj) > 0:
            issuable_tasks_obj=tasks.objects.filter(pid=projects_obj[0])
            for i in range(1,len(projects_obj)):
                issuable_tasks_obj.union(tasks.objects.filter(pid=i))
        return render(request, "index.html",{"issues":issues_obj,"tasks":tasks_obj,"projects":projects_obj,"users":users_obj,'issuable_tasks':issuable_tasks_obj})
    if request.user.is_admin == False: # staff user
        projects_obj = projects.objects.all()
        tasks_obj = tasks.objects.filter(assigned_to=request.user)
        issues_obj = issues.objects.filter(assigned_to=request.user)
        staff_tasks_obj = tasks.objects.filter(assigned_by=request.user)
        staff_projects_obj = projects.objects.filter(head=request.user)
        staff_issues_obj = issues.objects.filter(tid__pid__head=request.user)
        users_obj = user.objects.filter(is_validated = True)
        prs = projects.objects.filter(assigned_to=request.user)
        if len(prs)> 0:
            issuable_tasks = tasks.objects.filter(pid=prs[0])
            for i in range(1,len(prs)):
                issuable_tasks.union(tasks.objects.filter(pid=prs[i]))
        else:
            issuable_tasks = None
        return render(request, "staff.html",{"issues":issues_obj,"tasks":tasks_obj,"projects":projects_obj,"staff_issues":staff_issues_obj,"staff_tasks":staff_tasks_obj,"staff_projects":staff_projects_obj,"users":users_obj,"issuable_tasks":issuable_tasks})        
    projects_obj = projects.objects.all()
    tasks_obj = tasks.objects.all()
    issues_obj = issues.objects.all()
    users_obj = user.objects.filter(is_validated = True)
    heads = user.objects.filter(is_staff=True)
    unverified_users_obj = user.objects.filter(is_validated = False)
    return render(request, "admin.html",{"issues":issues_obj,"tasks":tasks_obj,"projects":projects_obj,"issuable_tasks":tasks_obj,"users":users_obj,"heads":heads,"staff_tasks":tasks_obj,"staff_projects":projects_obj,"unverified_users":unverified_users_obj,'issuable_tasks':tasks_obj})


def login_view(request):
    if request.method == "POST":
        try:
            username = user.objects.filter(email=request.POST["email"])[0].username
        except IndexError:
            return render(request, "login.html", {"error": True, "message": "Invalid credentials"})
        password = request.POST["password"]
        u = authenticate(request, username=username, password=password)
        if u != None:
            login(request, u)
            return redirect("/")
        else:
            return render(request, "login.html", {"error": True, "message": "Invalid credentials"})
    return render(request, "login.html")

def logout_view(request):
    logout(request)
    return redirect('/')

def register_view(request):
    if request.method == "POST":
        email = request.POST["email"]
        password = request.POST["password"]
        confirm = request.POST["confirm"]
        first_name = request.POST["first_name"]
        last_name = request.POST["last_name"]
        if password != confirm:
            return render(request,"register.html",{"error": True, "message": "Passwords do not match"})
        if settings.EMAIL_VERIFICATION:
            v_hash = md5(ctime()).hexdigest()
            u = user.objects.create_user(email=email,password=password,first_name=first_name,last_name=last_name,username=email.split("@")[0],verification_hash=v_hash)
            u.save()
            send_email(md5(u.email).hexdigest(),v_hash,u.email,domain=request.META["HTTP_HOST"])
        else:
            u = user.objects.create_user(email=email,password=password,first_name=first_name,last_name=last_name,username=email.split("@")[0],email_validated=True,verification_hash=None)
            u.save()
        return redirect("/")

    return render(request, "register.html")


def email_verification(request):
    try:
        passed_hash = request.GET["v"]
        email_hash = request.GET["e"]
    except MultiValueDictKeyError:
        return HttpResponse("Bad request", status=400)
    u = user.objects.filter(verification_hash=passed_hash)
    if len(u) == 0:
        return HttpResponse("Bad request", status=400)
    u = u[0]
    if email_hash != md5(u.email).hexdigest():
        return HttpResponse("Bad request", status=400)
    u.verification_hash = None
    u.email_validated = True
    u.save()
    return redirect("/")


def project(request,pid):
    try:
        project_obj = projects.objects.get(pid=pid)
    except projects.DoesNotExist:
        return HttpResponse("<h1>Not Found</h1>",status=404)
    if (request.user in project_obj.assigned_to.all() and request.user.is_admin):
        return HttpResponse("<h1>FORBIDDEN</h1>")

    tasks_obj = tasks.objects.filter(pid=project_obj)
    issues_obj = issues.objects.filter(tid__pid=project_obj)
    staff_issues_obj = issues.objects.filter(tid__pid__head=request.user)
    return render(request, 'project.html',{"project":project_obj,"tasks":tasks_obj,"issues":issues_obj,"staff_tasks":tasks_obj})

def add_project(request):
    if request.user.is_admin == False:
        return HttpResponse('<h1>FORBIDDEN</h1>',status=403)
    if request.method=="POST":
        # Add project
        u = user.objects.get(id=request.POST['head'])
        p = projects.objects.create(title=request.POST['title'],description=request.POST['description'],head=u,progress=progress_choices[0])
        p.assigned_to.add(u)
        p.save()
        return redirect('/')
    return redirect('/')

def add_task(request): # AJAX
    if request.user.is_staff is not False and request.user.is_admin is not False:
        return HttpResponse('<h1>FORBIDDEN</h1>',status=403)
    if request.method == "POST":
        p = projects.objects.get(pid=request.POST['project'])
        p.progress = "Yet to start"
        p.save()
        u = user.objects.get(id=request.POST['user'])
        if request.user != p.head and request.user.is_admin == False:
            return JsonResponse({"success":False})
        t = tasks.objects.create(pid=p,content=request.POST['content'],assigned_by=request.user,assigned_to=u,progress=progress_choices[0])
        t.save()
        return JsonResponse({"success":True})
    return JsonResponse({"success":False})

@csrf_exempt
def update_task(request,tid): # AJAX
    if request.method == "POST":
        t = tasks.objects.get(tid=tid)
        if request.user == t.assigned_by or request.user.is_admin or t.assigned_to == request.user:
            if request.POST['progress'] == "Completed" and t.assigned_to == request.user:
                return JsonResponse({"success":False})
            if request.POST['progress'] in progress_choices[-3:]:
                is_s = issues.objects.filter(tid=t)
                for is_ in is_s:
                    is_.progress = True
                    is_.save()
            t.progress = request.POST['progress']
            t.progress_log.append(request.POST['progress_log'])
            t.save()
            p = t.pid
            ts = tasks.objects.filter(pid=t.pid)
            for i in range(len(progress_choices)):
                p.progress = progress_choices[i]
                if len(ts.filter(progress=progress_choices[i])) > 0:
                    break
            p.save()
            return JsonResponse({"success":True})
        return JsonResponse({"success":False})
    return JsonResponse({"success":False})

def add_issue(request): # AJAX
    if request.method == "POST":
        t = tasks.objects.get(tid=request.POST["tid"])
        i = issues.objects.create(content=request.POST["content"],tid=t,assigned_to=t.assigned_to,assigned_by=request.user,t_content=t.content)
        i.save()
        t.progress = "Fixing bugs"
        p = t.pid
        p.progress = "Fixing bugs"
        t.save()
        p.save()
        return JsonResponse({"success":True})
    return JsonResponse({"success":False})

def user_validation(request): # AJAX
    try:
        user_obj = user.objects.get(id=request.POST['uid'])
    except user.DoesNotExist:
        return HttpResponse("<h1>Not Found</h1>",status=404)
    if request.user.is_admin == False:
        return HttpResponse('<h1>FORBIDDEN</h1>',status=403)
    if request.method == "POST":
        ac = request.POST['action']
        if ac == "reject":
            user_obj.delete()
            return JsonResponse({"success":True})
        elif ac == "accept":
            pos = request.POST['position']
            if pos == "normal":
                user_obj.is_staff = False
                user_obj.is_admin = False
                user_obj.is_validated = True
                user_obj.verification_hash = None
            elif pos == "head":
                user_obj.is_staff = True
                user_obj.is_admin = False
                user_obj.is_validated = True
                user_obj.verification_hash = None
            elif pos == "executive":
                user_obj.is_staff = True
                user_obj.is_admin = True
                user_obj.is_validated = True
                user_obj.verification_hash = None
            user_obj.save()
            return JsonResponse({"success":True})
        else:
            return JsonResponse({"success":False})
    return JsonResponse({"success":False})


