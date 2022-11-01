from django.test import TestCase, Client
from main.models import user,projects,tasks,issues

# Create your tests here.

class non_gui(TestCase):
	def setUp(self):
		uo = user.objects.create_user(email="owner@overwatcher.org",password="password",username="owner",first_name="nik",last_name="hil",is_superuser=True,is_staff=True,is_active=True,is_validated=True,is_admin=True)
		ue1 = user.objects.create_user(email="executive1@overwatcher.org",password="password",username="executive1",first_name="ex",last_name="1",is_superuser=False,is_staff=True,is_active=True,is_validated=True,is_admin=True)
		uh1 = user.objects.create_user(email="head1@overwatcher.org",password="password",username="head1",first_name="head",last_name="1",is_superuser=False,is_staff=True,is_active=True,is_validated=True,is_admin=False)
		uh2 = user.objects.create_user(email="head2@overwatcher.org",password="password",username="head2",first_name="head",last_name="2",is_superuser=False,is_staff=True,is_active=True,is_validated=True,is_admin=False)
		un1 = user.objects.create_user(email="normal1@overwatcher.org",password="password",username="normal1",first_name="normal",last_name="1",is_superuser=False,is_staff=False,is_active=True,is_validated=True,is_admin=False)
		un2 = user.objects.create_user(email="normal2@overwatcher.org",password="password",username="normal2",first_name="normal",last_name="2",is_superuser=False,is_staff=False,is_active=True,is_validated=True,is_admin=False)
		un3 = user.objects.create_user(email="normal3@overwatcher.org",password="password",username="normal3",first_name="normal",last_name="3",is_superuser=False,is_staff=False,is_active=True,is_validated=True,is_admin=False)
		p1 = projects.objects.create(title="project1",description="Test project 1",head=uh1)
		p1.assigned_to.add(uh1)
		p1.assigned_to.add(un1)
		p1.assigned_to.add(un2)
		p1.assigned_to.add(un3)
		p2 = projects.objects.create(title="project2",description="Test project 2",head=uh2)
		p1.assigned_to.add(uh2)
		t1 = tasks.objects.create(pid=p1,content="Test Task 1 project1",assigned_by=uh1,assigned_to=un1,progress="Yet to start")
		t2 = tasks.objects.create(pid=p1,content="Test Task 2 project1",assigned_by=uh1,assigned_to=un2,progress="Yet to start")
		t3 = tasks.objects.create(pid=p1,content="Test Task 3 project1",assigned_by=uh1,assigned_to=un3,progress="Yet to start")
		t4 = tasks.objects.create(pid=p1,content="Test Task 4 project1",assigned_by=uh1,assigned_to=un1,progress="Yet to start")
		t5 = tasks.objects.create(pid=p1,content="Test Task 5 project1",assigned_by=uh1,assigned_to=un2,progress="Yet to start")
		i1 = issues.objects.create(content="Issue 1 Task 1",tid = t1,assigned_to= t1.assigned_to,assigned_by=un2,t_content=t1.content)
		i2 = issues.objects.create(content="Issue 2 Task 3",tid = t3,assigned_to= t3.assigned_to,assigned_by=uh1,t_content=t3.content)
		i3 = issues.objects.create(content="Issue 3 Task 3",tid = t3,assigned_to= t3.assigned_to,assigned_by=uh1,t_content=t3.content)
		
	def test_login(self):
		c = Client()
		resp = c.post('/login',{"email":"owner@overwatcher.org","password":"password"})
		self.assertFalse("Invalid credentials" in resp.content.decode())
		resp = c.post('/login',{"email":"executive1@overwatcher.org","password":"password"})
		self.assertFalse("Invalid credentials" in resp.content.decode())
		resp = c.post('/login',{"email":"head1@overwatcher.org","password":"password"})
		self.assertFalse("Invalid credentials" in resp.content.decode())
		resp = c.post('/login',{"email":"head2@overwatcher.org","password":"password"})
		self.assertFalse("Invalid credentials" in resp.content.decode())
		resp = c.post('/login',{"email":"normal1@overwatcher.org","password":"password"})
		self.assertFalse("Invalid credentials" in resp.content.decode())
		resp = c.post('/login',{"email":"normal2@overwatcher.org","password":"password"})
		self.assertFalse("Invalid credentials" in resp.content.decode())
		resp = c.post('/login',{"email":"normal3@overwatcher.org","password":"password"})
		self.assertFalse("Invalid credentials" in resp.content.decode())
		resp = c.post('/login',{"email":"owner@overwatcher.org","password":"passworasfddsd"})
		self.assertTrue("Invalid credentials" in resp.content.decode())

	def test_register(self):
		c = Client()
		c.post('/register',{"email":"testuser@overwatcher.org","password":"password","confirm":"password","first_name":"test","last_name":"user"})
		resp = c.post('/login',{"email":"testuser@overwatcher.org","password":"password"})
		self.assertFalse("Invalid credentials" in resp.content.decode())

	def test_add_project(self):
		c = Client()
		uh2 = user.objects.get(email="head2@overwatcher.org")
		c.post('/login',{"email":"executive1@overwatcher.org","password":"password"})
		c.post('/add/project',{"title":"project2","description":"Test project 2","head":uh2.id})
		self.assertEqual(len(projects.objects.all()),3)

	def test_add_task(self):
		c = Client()
		c.login(username="head1",password="password")
		resp = c.post('/add/task',{"project":"1","user":"7","content":"Task 6 project 1"})
		c.logout()
		self.assertEqual(len(tasks.objects.all()),6)

	def test_update_task_and_issue_add(self):
		c = Client()
		c.login(username="normal1",password="password")
		x=c.post('/update/task/1',{"progress":"Testing","progress_log":"Testing"})
		self.assertEqual(tasks.objects.get(tid=1).progress,"Testing")
		c.post('/update/task/4',{"progress":"Testing","progress_log":"Testing"})
		self.assertEqual(tasks.objects.get(tid=4).progress,"Testing")
		c.logout()
		c.login(username="normal2",password="password")
		c.post('/update/task/2',{"progress":"Testing","progress_log":"Testing"})
		self.assertEqual(tasks.objects.get(tid=2).progress,"Testing")
		c.post('/update/task/5',{"progress":"Testing","progress_log":"Testing"})
		self.assertEqual(tasks.objects.get(tid=5).progress,"Testing")
		c.logout()
		c.login(username="normal3",password="password")
		c.post('/update/task/3',{"progress":"In Progress","progress_log":"Testing"})
		self.assertEqual(tasks.objects.get(tid=3).progress,"In Progress")
		self.assertEqual(projects.objects.get(pid=1).progress,"In Progress")
		c.logout()
		c.login(username="head1",password="password")
		c.post('/update/task/3',{"progress":"Completed","progress_log":"Testing"})
		self.assertEqual(projects.objects.get(pid=1).progress,"Testing")
		c.post('/update/task/1',{"progress":"Completed","progress_log":"Testing"})
		c.post('/update/task/2',{"progress":"Completed","progress_log":"Testing"})
		c.post('/update/task/3',{"progress":"Completed","progress_log":"Testing"})
		c.post('/update/task/4',{"progress":"Completed","progress_log":"Testing"})
		c.post('/update/task/5',{"progress":"Completed","progress_log":"Testing"})
		self.assertEqual(projects.objects.get(pid=1).progress,"Completed")
		c.logout()
		c.login(username="normal3",password="password")
		c.post('/add/issue',{"tid":"1","content":"new issue created"})
		self.assertEqual(projects.objects.get(pid=1).progress,"Fixing bugs")
		self.assertEqual(len(issues.objects.all()),4)
		
	def test_user_validation(self):
		c = Client()
		c.post('/register',{"email":"testuser2@overwatcher.org","password":"password","confirm":"password","first_name":"test","last_name":"user"})
		c.post('/register',{"email":"testuser3@overwatcher.org","password":"password","confirm":"password","first_name":"test","last_name":"user"})
		c.logout()
		c.login(username="executive1",password="password")
		c.post('/add/user',{"action":"reject","uid":"9"})
		self.assertEqual(len(user.objects.all()),8)
		c.post('/add/user',{"action":"reject","uid":"8","position":"head"})
		




