from qa.boto.fps.connection import FPSConnection
from django import forms
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.db.models import Count
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.views.decorators.csrf import csrf_protect
from qa.main.models import Answer, Question
from settings import *
import hashlib

def activate(request, email, key):
	user = None
	userQuery = User.objects.filter(email = email)
	if userQuery:
		user = userQuery[0]
	userKey = hashlib.sha256(user.password).hexdigest()[:8]
	if key == userKey:
		user.is_active = True
		user.save()
		Answer.objects.filter(user = user).update(published = True)
		messages.success(request, 'Account activated! All your answers are now publicly visible.')
	return HttpResponseRedirect('/')

@csrf_protect
def answerEdit(request, answer_id):
	user = request.user
	answer = Answer.objects.get(pk = answer_id)
	question = answer.question
	is_a = user.is_authenticated() and user == answer.user
	if request.method == 'POST':
		if is_a:
			answer.text = request.POST['text']
			answer.save()
			messages.success(request, 'Your changes have been saved!')
		return HttpResponseRedirect('/question/' + str(question.id))
	else:
		answers = Answer.objects.filter(question = question)
		return render_to_response('answerEdit.html', {
			'answer': answer,
			'question': question,
		}, context_instance = RequestContext(request))

@csrf_protect
def ask(request):
	user = request.user
	q = None
	if request.method == 'POST':
		questionForm = QuestionForm(user, request.POST)
		if questionForm.is_valid():
			if not user.is_authenticated():
				if questionForm.cleaned_data['newUser'] == u'True':
					email = questionForm.cleaned_data['email']
					user, password = createUserFromEmail(email, request)
					#todo: "you will either need to login or click this link to activate"
					send_mail(
						'Account created',
						'Thanks for signing up with qa site!  Your password is %s' % password,
						'blake8086@gmail.com',
						[email],
						fail_silently = False
					)
				else:
					email = questionForm.cleaned_data['email']
					user = User.objects.filter(email = email)[0]
					#todo: throw error if not found
					user = authenticate(username = user.username, password = questionForm.cleaned_data['password'])
			q = Question.objects.create(
				text = questionForm.cleaned_data['text'],
				price = questionForm.cleaned_data['bounty'],
				user = user,
			)
			#todo: get a question slug
			#redirect to amazon pipeline
			connection = FPSConnection(
				aws_access_key_id = AWS_KEY_ID,
				aws_secret_access_key = AWS_SECRET_KEY,
				is_secure = True,
				host = AMAZON_DOMAIN,
				path = '/',
			)
			url = connection.make_url(
				returnURL = 'http://www.google.com/',
				paymentReason = 'Question on [qa site]',
				pipelineName = 'SingleUse',
				transactionAmount = str(q.price) + '.00',
			)
			return HttpResponse(url)#HttpResponseRedirect(url)
	else:
		questionForm = QuestionForm(user, initial = {'bounty': u'10'})
	return render_to_response('ask.html', {
		'questionForm': questionForm
	}, context_instance = RequestContext(request))

def index(request):
	return render_to_response('index.html', {}, context_instance = RequestContext(request))
	
def loginView(request):
	if request.method == 'POST':
		user = User.objects.get(email = request.POST['email'])
		user = authenticate(username = user.username, password = request.POST['password'])
		if user is not None:
			if not user.is_active:
				user.is_active = True
				user.save()
				Answer.objects.filter(user = user).update(published = True)
				messages.success(request, 'Your account has been activated!')
			login(request, user)
			messages.success(request, 'Logged in as ' + user.email)
			return HttpResponseRedirect('/')
		else:
			messages.error(request, 'Wrong email/password')
	#if possible, change to redirect to referring page
	return HttpResponseRedirect('/')

def logoutView(request):
	logout(request)
	return HttpResponseRedirect('/')

@csrf_protect
def question(request, question_id):
	user = request.user
	answerForm = AnswerForm(user)
	question = Question.objects.get(pk = question_id)
	is_q = user.is_authenticated() and user == question.user
	if request.method == 'POST':
		if is_q and not question.is_answered:
			answer = Answer.objects.get(pk = request.POST['answer'])
			answer.is_winner = True
			question.is_answered = True
			answer.save()
			question.save()
			#send email notifications
			send_mail(
				'congrats',
				'your answer was accepted. get money. get paid.',
				'blake8086@gmail.com',
				[answer.user.email],
				fail_silently = False
			)
			send_mail(
				'notification',
				'you accepted some dude\'s answer',
				'blake8086@gmail.com',
				[question.user.email],
				fail_silently = False
			)
		else:
			answerForm = AnswerForm(user, request.POST)
			if answerForm.is_valid():
				message = 'Answer posted!'
				if not user.is_authenticated():
					if answerForm.cleaned_data['newUser'] == u'True':
						email = answerForm.cleaned_data['email']
						user, password = createUserFromEmail(email, request)
						#todo: convert to a template
						key = hashlib.sha256(user.password).hexdigest()[:8]
						activateUrl = 'http://localhost:8000/activate/' + email + '/' + key
						activateLink = '<a href="%s">Activate your account</a> %s' % (activateUrl, activateUrl)
						mailBody = """Thanks for signing up with qa site!  Your password is %s
You will need to activate your account before your answer becomes public.  %s""" % (password, activateLink)
						send_mail(
							'Account created',
							mailBody,
							'blake8086@gmail.com',
							[email],
							fail_silently = False
						)
						#todo: this answer is unpublished initially
						message = 'Answer saved! You will need to activate your account before your answer becomes public.'
					else:
						email = answerForm.cleaned_data['email']
						user = User.objects.filter(email = email)[0]
						#todo: throw error if not found
						user = authenticate(username = user.username, password = answerForm.cleaned_data['password'])
						login(request, user)
				published = user.is_active
				Answer.objects.create(
					published = published,
					question = question,
					text = answerForm.cleaned_data['text'],
					user = user,
				)
				messages.success(request, message)
					
	answers = Answer.objects.filter(question = question)
	
	return render_to_response('question.html', {
		'answers': answers,
		'answerForm': answerForm,
		'is_q': is_q,
		'question': question,
	}, context_instance = RequestContext(request))

@csrf_protect
def questionEdit(request, question_id):
	user = request.user
	question = Question.objects.get(pk = question_id)
	is_q = user.is_authenticated() and user == question.user
	if request.method == 'POST':
		if is_q:
			question.text = request.POST['text']
			question.save()
			messages.success(request, 'Your changes have been saved!')
		return HttpResponseRedirect('/question/' + str(question.id))
	else:
		answers = Answer.objects.filter(question = question)
		return render_to_response('questionEdit.html', {
			'answers': answers,
			'question': question,
		}, context_instance = RequestContext(request))

def questions(request):
	questions = Question.objects.annotate(Count('answer'))
	return render_to_response('questions.html', {
		'questions': questions
	}, context_instance = RequestContext(request))
	
def tos(request):
	return render_to_response('tos.html', {}, context_instance = RequestContext(request))

###############################################################################
def createUserFromEmail(email, request):
	username = hashlib.sha256(email).hexdigest()[:30]
	password = User.objects.make_random_password(8)
	user = User.objects.create_user(username, email, password)
	user.is_active = False
	user.save()
	user = authenticate(username = username, password = password)
	login(request, user)
	return (user, password)

class LoginForm(forms.Form):
	def __init__(self, user, *args, **kwargs):
		super(LoginForm, self).__init__(*args, **kwargs)
		if not user.is_authenticated():
			self.fields['email'] = forms.EmailField(label = 'Email:')
			self.fields['newUser'] = forms.ChoiceField(
				choices = (
					('True', 'No, I am a new customer'),
					('False', 'Yes, I have a password:'),
				),
				label = 'Do you have a [qa site] password?',
				widget = forms.RadioSelect,
			)
			self.fields['email2'] = forms.EmailField(label = 'Confirm email:', required = False)
			self.fields['password'] = forms.CharField(
				label = 'Password:',
				required = False,
				widget = forms.PasswordInput()
			)

	def clean_email2(self):
		email = self.cleaned_data.get('email')
		email2 = self.cleaned_data.get('email2')
		if self.cleaned_data.get('newUser') == 'True':
			if email != email2:
				raise forms.ValidationError("Email addresses must match.")
		return email2

	def clean_password(self):
		password = self.cleaned_data.get('password')
		if self.cleaned_data.get('newUser') == 'False':
			userQuery = User.objects.filter(email = self.cleaned_data.get('email'))
			if userQuery:
				user = userQuery[0]
				user = authenticate(username = user.username, password = password)
				if not user:
					raise forms.ValidationError("Wrong email/password combination.")
			else:
				raise forms.ValidationError("Wrong email/password combination.")
		return password

class AnswerForm(LoginForm):
	text = forms.CharField(label = 'My Answer:', widget = forms.Textarea)

class QuestionForm(LoginForm):
	text = forms.CharField(label = 'My Question:', widget = forms.Textarea)
	bounty = forms.CharField(label = 'Bounty for a correct answer:', widget = forms.Select(choices = (
		('1', '$1.00'), ('2', '$2.00'), ('3', '$3.00'), ('5', '$5.00'),
		('10', '$10.00'), ('15', '$15.00'), ('20', '$20.00'), ('25', '$25.00'),
		('30', '$30.00'), ('40', '$40.00'), ('50', '$50.00'), ('100', '$100.00'),
	)))
