from boto.fps.connection import FPSConnection
from django import forms
from django.contrib import messages
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.db.models import Count
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.views.decorators.csrf import csrf_protect
from main.models import Answer, Question
from settings import *
import hashlib

def getOrCreateUserFromEmail(email):
	#is this a recognized user
	userQuery = User.objects.filter(email = email)
	if len(userQuery) > 0:
		user = userQuery[0]
	else:
		user = User.objects.create_user(
			username = hashlib.sha256(email).hexdigest()[:30],
			email = email,
			password = User.objects.make_random_password(8)
		)

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
	if request.method == 'POST':
		form = QuestionForm(request.POST)
		if form.is_valid():
			email = form.cleaned_data['email']
			user = getOrCreateUserFromEmail(email)
			#add question but mark as not paid
			q = Question.objects.create(
				text = form.cleaned_data['text'],
				price = form.cleaned_data['bounty'],
				user = user,
			)
			#get a question slug
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
		form = QuestionForm(initial = {'bounty': u'10'})
	return render_to_response('ask.html', {
		'form': form
	}, context_instance = RequestContext(request))

def index(request):
	return render_to_response('index.html', {}, context_instance = RequestContext(request))

@csrf_protect
def question(request, question_id):
	answerForm = AnswerForm()
	user = request.user
	question = Question.objects.get(pk = question_id)
	is_q = user.is_authenticated() and user == question.user
	if request.method == 'POST':
		if is_q:
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
			answerForm = AnswerForm(request.POST)
			if answerForm.is_valid():
				if user.is_authenticated() == False:
					email = answerForm.cleaned_data['email']
					getOrCreateUserFromEmail(email)
				Answer.objects.create(
					question = question,
					text = answerForm.cleaned_data['text'],
					user = user,
				)
				messages.success(request, 'Answer posted!')
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

def checkEmailConfirm(form):
	cleaned_data = form.cleaned_data
	email = cleaned_data.get('email')
	email2 = cleaned_data.get('email2')
	if email and email2:
		if email != email2:
			raise forms.ValidationError("Email addresses must match.")
	return cleaned_data
	
class AnswerForm(forms.Form):
	text = forms.CharField(label = 'My Answer:', widget = forms.Textarea)
	email = forms.EmailField(label = 'If my answer is selected, notify me by email at:')
	email2 = forms.EmailField(label = 'Confirm email:')

	def clean(self):
		return checkEmailConfirm(self)

class QuestionForm(forms.Form):
	text = forms.CharField(label = 'My Question:', widget = forms.Textarea)
	email = forms.EmailField(label = 'When my question is answered, notify me by email at:')
	email2 = forms.EmailField(label = 'Confirm email:')
	bounty = forms.CharField(label = 'Bounty for a correct answer:', widget = forms.Select(choices = (
		('1', '$1.00'), ('2', '$2.00'), ('3', '$3.00'), ('5', '$5.00'),
		('10', '$10.00'), ('15', '$15.00'), ('20', '$20.00'), ('25', '$25.00'),
		('30', '$30.00'), ('40', '$40.00'), ('50', '$50.00'), ('100', '$100.00'),
	)))
	
	def clean(self):
		return checkEmailConfirm(self)
