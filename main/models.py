from django.db import models
from django.contrib.auth.models import AbstractUser

progress_choices = (
	('Yet to start','Yet to start'),
	('In Progress','In Progress'),
	('On-Hold','On-Hold'),
	('Testing','Testing'),
	('Under Review','Under Review'),
	('Completed','Completed'),
	('Fixing bugs','Fixing bugs'),
	('Released','Released'),
	)

class user(AbstractUser):
	is_validated = models.BooleanField(default = False)
	email_validated = models.BooleanField(default = False)
	verification_hash = models.CharField(max_length = 100,null = True)
	is_admin = models.BooleanField(default =False)



class projects(models.Model):
	pid = models.AutoField(primary_key = True)
	title = models.CharField(max_length = 300)
	description = models.CharField(max_length = 2000)
	head = models.ForeignKey(user,related_name='head',on_delete=models.CASCADE)
	assigned_to = models.ManyToManyField(user)
	code_link = models.CharField(max_length=300,null=True)
	progress = models.CharField(max_length = 200,choices =progress_choices, )


class tasks(models.Model):
	tid = models.AutoField(primary_key = True)
	pid = models.ForeignKey(projects,on_delete=models.CASCADE)
	content = models.CharField(max_length=2000)
	assigned_by = models.ForeignKey(user,related_name='tasks_assigned_by',on_delete = models.CASCADE)
	assigned_to = models.ForeignKey(user,related_name='tasks_assigned_to',on_delete = models.CASCADE)
	progress = models.CharField(max_length = 200,choices =progress_choices, )
	progress_log = models.JSONField(default = list)

class issues(models.Model):
	iid = models.AutoField(primary_key = True)
	content = models.CharField(max_length=200)
	t_content = models.CharField(max_length=200)
	progress = models.BooleanField(default=False)
	tid = models.ForeignKey(tasks, related_name="issues_tid", on_delete=models.CASCADE)
	assigned_to = models.ForeignKey(user,related_name='issues_assigned_to',on_delete = models.CASCADE)
	assigned_by = models.ForeignKey(user,related_name='issues_assigned_by',on_delete = models.CASCADE)
