import sys
sys.path.append('/Library/Python/2.6/site-packages')
sys.path.append('/home/blake8086/webapps/c4c_development/qa')
sys.path.append('/home/blake8086/webapps/c4c_staging/qa')
sys.path.append('/home/blake8086/webapps/c4c_production/qa')
from qa.boto.fps.connection import FPSConnection
from django import forms
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.core.mail import EmailMultiAlternatives, send_mail
from django.db.models import Count, Sum
from django.http import HttpResponse, HttpResponseRedirect, HttpResponseForbidden
from django.shortcuts import render_to_response
from django.template import Context, RequestContext
from django.template.loader import get_template
from django.views.decorators.csrf import csrf_protect
from qa.main.models import Answer, Question, UserProfile
from qa.main.models import LogCallerToken, LogPaymentResponse, LogPipelineResponse, LogRecipientToken
from settings import *
from urllib import urlencode
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
					key = hashlib.sha256(user.password).hexdigest()[:8]
					activateUrl = 'http://' + SITE_DOMAIN + '/activate/' + email + '/' + key
					
					context = Context({
						'activateUrl': activateUrl,
						'password': password,
					})
					sendTemplateEmail('Welcome to code4cheap.com', email, 'questionerSignup', context)
				else:
					email = questionForm.cleaned_data['email']
					user = User.objects.filter(email = email)[0]
					user = authenticate(username = user.username, password = questionForm.cleaned_data['password'])
			q = Question.objects.create(
				text = questionForm.cleaned_data['text'],
				price = questionForm.cleaned_data['bounty'],
				user = user,
			)
			#redirect to amazon pipeline
			connection = FPSConnection(
				aws_access_key_id = AWS_KEY_ID,
				aws_secret_access_key = AWS_SECRET_KEY,
				is_secure = True,
				host = AMAZON_DOMAIN,
				path = '/',
			)
			url = connection.make_url(
				cobrandingUrl = AMAZON_COBRAND,
				returnURL = 'http://' + SITE_DOMAIN + '/thanks/' + str(q.id),
				paymentReason = 'Question on code4cheap',
				pipelineName = 'SingleUse',
				transactionAmount = str(q.price),
			)
			return HttpResponseRedirect(url)
	else:
		questionForm = QuestionForm(user, initial = {'bounty': u'10', 'newUser': 'True'})
	return render_to_response('ask.html', {
		'questionForm': questionForm
	}, context_instance = RequestContext(request))

def faq(request):
	return render_to_response('faq.html', {
	}, context_instance = RequestContext(request))

def home(request):
	if request.user.is_authenticated():
		questions = Question.objects.filter(published = True).annotate(public_answers = Sum('answer__published')).order_by('created').reverse()
		return render_to_response('questions.html', {
			'questions': questions
		}, context_instance = RequestContext(request))
	else:
		return render_to_response('splash.html', {}, context_instance = RequestContext(request))

def loginView(request):
	if request.method == 'POST':
		user = None
		if User.objects.filter(email = request.POST['email']).exists():
			user = User.objects.get(email = request.POST['email'])
		elif User.objects.filter(username = request.POST['email']).exists():
			user = User.objects.get(username = request.POST['email'])
		if user is not None:
			user = authenticate(username = user.username, password = request.POST['password'])
			if user is not None:
				if not user.is_active:
					user.is_active = True
					user.save()
					Answer.objects.filter(user = user).update(published = True)
					messages.success(request, 'Your account has been activated!')
				login(request, user)
				messages.success(request, 'Logged in as ' + user.username)
				return HttpResponseRedirect('/')
		messages.error(request, 'Wrong email/password')
	#if possible, change to redirect to referring page
	return HttpResponseRedirect('/')

def logoutView(request):
	logout(request)
	return HttpResponseRedirect('/')

def profile(request):
	user = request.user
	if not user.is_authenticated():
		return HttpResponseRedirect('/')

	profile = user.get_profile()
	#if they posted the form
	if request.method == 'POST':
		profileForm = ProfileForm(request.POST)
		if profileForm.is_valid():
			cleanData = profileForm.cleaned_data
			
			profile.enableEmails = cleanData['enableEmails']
			if cleanData['enableEmails']:
				profile.enableAnswerNotifications = cleanData['enableAnswerNotifications']
				profile.enablePickedNotifications = cleanData['enablePickedNotifications']
			else:
				profile.enableAnswerNotifications = False
				profile.enablePickedNotifications = False				
			profile.emailAlias = cleanData['emailAlias']
			if cleanData['emailAlias'] == 'False' and '@' not in cleanData['username']:
				user.username = cleanData['username']
				user.save()
			else:
				user.username = user.email
				user.save()
			profile.save()
			messages.success(request, 'Settings saved')
	else:
		emailAlias = False
		if '@' in user.username:
			emailAlias = True
		profileForm = ProfileForm(initial = {
			'enableEmails': profile.enableEmails,
			'enableAnswerNotifications': profile.enableAnswerNotifications,
			'enablePickedNotifications': profile.enablePickedNotifications,
			'emailAlias': emailAlias,
			'username': user.username,
		})
	
	answerCount = Answer.objects.filter(user = user).count()
	questionCount = Question.objects.filter(user = user).count()
	return render_to_response('profile.html', {
		'answerCount': answerCount,
		'profileForm': profileForm,
		'questionCount': questionCount,
		'user': user,
	}, context_instance = RequestContext(request))

@csrf_protect
def question(request, question_id):
	showForm = (request.method == 'POST')
	user = request.user
	answerForm = AnswerForm(user, initial = {'newUser': 'True'})
	question = Question.objects.get(pk = question_id)
	if question.published == False and user != question.user:
		return HttpResponseForbidden()
	question.views += 1
	question.save()
	is_q = user.is_authenticated() and user == question.user
	if request.method == 'POST':
		if is_q and not question.is_answered:
			answer = Answer.objects.get(pk = request.POST['answer'])
			answer.is_winner = True
			question.is_answered = True
			answer.save()
			question.save()

			context = Context({
				'answerer': answer.user,
				'questioner': question.user,
				'url': 'http://' + SITE_DOMAIN + '/question/' + str(question.id)
			})
			sendTemplateEmail('Your answer was selected!', answer.user.email, 'answererAccepted', context)
		else:
			answerForm = AnswerForm(user, request.POST)
			if answerForm.is_valid():
				message = 'Answer submitted!'
				if not user.is_authenticated():
					if answerForm.cleaned_data['newUser'] == u'True':
						email = answerForm.cleaned_data['email']
						user, password = createUserFromEmail(email, request)
						key = hashlib.sha256(user.password).hexdigest()[:8]
						activateUrl = 'http://' + SITE_DOMAIN + '/activate/' + email + '/' + key
						
						context = Context({
							'activateUrl': activateUrl,
							'email': email,
							'password': password,
						})
						sendTemplateEmail('Welcome to code4cheap.com', email, 'answererSignup', context)
						message = 'Answer saved! You will need to activate your account before your answer becomes public.'
					else:
						email = answerForm.cleaned_data['email']
						user = User.objects.filter(email = email)[0]
						user = authenticate(username = user.username, password = answerForm.cleaned_data['password'])
						login(request, user)
				published = user.is_active
				Answer.objects.create(
					published = published,
					question = question,
					text = answerForm.cleaned_data['text'],
					user = user,
				)
				showForm = False
				messages.success(request, message)
				context = Context({
					'url': 'http://' + SITE_DOMAIN + '/question/' + str(question.id),
				})
				sendTemplateEmail('Your question received an answer!', question.user.email, 'questionerAnswer', context)
				#clear answer form
				answerForm = AnswerForm(user, initial = {'newUser': 'True'})
					
	answers = Answer.objects.filter(question = question).order_by('created').reverse()
	
	return render_to_response('question.html', {
		'answers': answers,
		'answerForm': answerForm,
		'showForm': showForm,
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
		return render_to_response('question.html', {
			'answers': answers,
			'edit': True,
			'is_q': is_q,
			'question': question,
		}, context_instance = RequestContext(request))

def questions(request):
	questions = Question.objects.filter(published = True).annotate(public_answers = Sum('answer__published')).order_by('created').reverse()
	return render_to_response('questions.html', {
		'questions': questions
	}, context_instance = RequestContext(request))

def testEmail(request):
	if request.user.is_superuser:
		return render_to_response('testEmail.html', {}, context_instance = RequestContext(request))

def thanks(request, question_id):
	question = Question.objects.get(pk = question_id)
	
	connection = FPSConnection(
		aws_access_key_id = AWS_KEY_ID,
		aws_secret_access_key = AWS_SECRET_KEY,
		is_secure = True,
		host = AMAZON_DOMAIN,
		path = '/',
	)
	
	#verify signature
	returnUrl = 'http://' + SITE_DOMAIN + '/thanks/' + str(question_id)
	httpParameters = {}
	for k, v in dict(request.GET).items():
		httpParameters[k] = v[0]
	LogPipelineResponse.objects.create(question = question, response = str(httpParameters))
	httpParameters = urlencode(httpParameters)
	verifyResponse = connection.verify_signature(returnUrl, httpParameters).__dict__
	
	#check for errors
	if 'errorMessage' in request.GET:
		messages.error(request, request.GET['errorMessage'])
	#check if they're authorized
	if verifyResponse['Status'] == 'Success':
		#charge payment
		callerTokenId = connection.install_caller_instruction()
		LogCallerToken.objects.create(question = question, token = str(callerTokenId))
		recipientTokenId = connection.install_recipient_instruction()
		LogRecipientToken.objects.create(question = question, token = str(recipientTokenId))
		result = connection.pay(
			callerReference = request.GET['callerReference'],
			callerTokenId = callerTokenId,
			recipientTokenId = recipientTokenId,
			senderTokenId = request.GET['tokenID'],
			transactionAmount = str(question.price),
		)
	
		payResponse = result.__dict__
		LogPaymentResponse.objects.create(question = question, response = str(payResponse))
	
		#check for errors
		if 'Status' in payResponse and payResponse['Status']:
			question.published = True
			question.save()
			messages.success(request, 'Your question has been published!')
			
			context = Context({
				'questioner': question.user,
				'url': 'http://' + SITE_DOMAIN + '/question/' + str(question.id),
			})
			sendTemplateEmail('Question posted successfully!', question.user.email, 'questionerThanks', context)
			
			return HttpResponseRedirect('/question/' + str(question.id))
	messages.error(request, 'A problem occurred when processing your payment, please try again.')
	return HttpResponseRedirect('/question/' + str(question.id))
	
def tos(request):
	return render_to_response('tos.html', {}, context_instance = RequestContext(request))

###############################################################################
def createUserFromEmail(email, request):
	if User.objects.filter(email = email).count() > 0:
		raise Exception('Email is already in use (%s)' % email)
	username = email
	password = User.objects.make_random_password(8)
	user = User.objects.create_user(username, email, password)
	user.is_active = False
	user.save()
	profile = UserProfile.objects.create(user = user)
	profile.save()
	user = authenticate(username = username, password = password)
	login(request, user)
	return (user, password)

def sendTemplateEmail(subject, toEmail, templateName, context):
	plaintext = get_template('email/' + templateName + '.txt')
	htmly = get_template('email/' + templateName + '.html')

	text_content = plaintext.render(context)
	html_content = htmly.render(context)
	msg = EmailMultiAlternatives(subject, text_content, 'code4cheap@gmail.com', [toEmail])
	msg.attach_alternative(html_content, "text/html")
	msg.send()

class LoginForm(forms.Form):
	def __init__(self, user, *args, **kwargs):
		super(LoginForm, self).__init__(*args, **kwargs)
		if not user.is_authenticated():
			self.fields['email'] = forms.EmailField(label = 'Email:')
			self.fields['newUser'] = forms.ChoiceField(
				choices = (
					('False', 'yes'),
					('True', 'no'),
				),
				label = 'Do you have a code4cheap account?',
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
	text = forms.CharField(label = 'Your Answer:', widget = forms.Textarea)

class QuestionForm(LoginForm):
	text = forms.CharField(label = 'Your Question:', widget = forms.Textarea)
	bounty = forms.CharField(label = 'Bounty for a correct answer:', widget = forms.Select(choices = (
		('1', '$1.00'), ('2', '$2.00'), ('3', '$3.00'), ('5', '$5.00'),
		('10', '$10.00'), ('15', '$15.00'), ('20', '$20.00'), ('25', '$25.00'),
		('30', '$30.00'), ('40', '$40.00'), ('50', '$50.00'), ('100', '$100.00'),
	)))

class ProfileForm(forms.Form):
	enableEmails = forms.BooleanField(label = 'Allow code4cheap to send me emails', required = False)
	enableAnswerNotifications = forms.BooleanField(label = 'Send me emails when my question is answered', required = False)
	enablePickedNotifications = forms.BooleanField(label = 'Send me emails when my answer is picked', required = False)
	
	emailAlias = forms.ChoiceField(
		choices = (
			('True', 'email'),
			('False', 'username'),
		),
		label = 'Display my name as:',
		widget = forms.RadioSelect,
	)
	username = forms.CharField(required = False)
	def clean_username(self):
		username = self.cleaned_data.get('username')
		if self.cleaned_data.get('emailAlias') == 'False':
			if username == '':
				raise forms.ValidationError('Username cannot be blank.')
			if User.objects.filter(username = username):
				raise forms.ValidationError('This username is already taken.')
		return username
