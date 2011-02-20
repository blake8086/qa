from django.db import models
from django.contrib.auth.models import User

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
