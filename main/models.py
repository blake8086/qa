from django.db import models
from django.contrib.auth.models import User

#patch from http://kfalck.net/2010/12/30/longer-usernames-for-django
#to give much longer usernames
from django.contrib.auth.admin import UserAdmin
User._meta.get_field('username').max_length = 75
User._meta.get_field('username').validators[0].limit_value = 75
UserAdmin.form.base_fields['username'].max_length = 75
UserAdmin.form.base_fields['username'].validators[0].limit_value = 75

class Answer(models.Model):
	created = models.DateTimeField(auto_now_add = True)
	deleted = models.BooleanField(default = False)
	is_winner = models.BooleanField(default = False)
	modified = models.DateTimeField(auto_now = True)
	published = models.BooleanField(default = False)
	question = models.ForeignKey('Question')
	text = models.TextField()
	user = models.ForeignKey(User)
	
	def __unicode__(self):
		check = ''
		if self.is_winner:
			check = 'X'
		else:
			check = '_'
		return u'%d %s %s' % (self.id, check, self.text[:100])

class LogCallerToken(models.Model):
	created = models.DateTimeField(auto_now_add = True)
	modified = models.DateTimeField(auto_now = True)
	question = models.ForeignKey('Question')
	token = models.TextField()

class LogPaymentResponse(models.Model):
	created = models.DateTimeField(auto_now_add = True)
	modified = models.DateTimeField(auto_now = True)
	question = models.ForeignKey('Question')
	response = models.TextField()

class LogPipelineResponse(models.Model):
	created = models.DateTimeField(auto_now_add = True)
	modified = models.DateTimeField(auto_now = True)
	question = models.ForeignKey('Question')
	response = models.TextField()

class LogRecipientToken(models.Model):
	created = models.DateTimeField(auto_now_add = True)
	modified = models.DateTimeField(auto_now = True)
	question = models.ForeignKey('Question')
	token = models.TextField()

class Question(models.Model):
	created = models.DateTimeField(auto_now_add = True)
	deleted = models.BooleanField(default = False)
	is_answered = models.BooleanField(default = False)
	modified = models.DateTimeField(auto_now = True)
	published = models.BooleanField(default = False)
	price = models.DecimalField(max_digits = 6, decimal_places = 2)
	text = models.TextField()
	user = models.ForeignKey(User)
	views = models.IntegerField(default = 0)

	def __unicode__(self):
		check = ''
		if self.is_answered:
			check = 'X'
		else:
			check = '_'
		return u'%d %s $%d.00 %s' % (self.id, check, self.price, self.text[:100])
