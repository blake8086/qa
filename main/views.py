# Create your views here.
from django import forms
from django.contrib.auth.models import User
from django.db.models import Count
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.views.decorators.csrf import csrf_protect
from main.models import Answer, Question
import hashlib

@csrf_protect
def ask(request):
	if request.method == 'POST':
		form = QuestionForm(request.POST)
		if form.is_valid():
			email = form.cleaned_data['email']
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
			#add question but mark as not paid
			q = Question.objects.create(
				text = form.cleaned_data['text'],
				price = form.cleaned_data['bounty'],
				user = user,
			)
			#get a question slug
			#redirect to amazon pipeline
			url =  'https://authorize.payments-sandbox.amazon.com/cobranded-ui/actions/start'
			url += '?callerKey=AKIAJJSGY3AIETRPFIZA'
			url += '&callerReference=Question+Number' + str(q.id)
			url += '&paymentReason=Question+on+qa+site'
			url += '&pipelineName=SingleUse'
			url += '&returnURL=http://www.example.com/question/' + str(q.id)
			url += '&signature=[URL-encoded value you generate]'
			url += '&transactionAmount=' + str(q.price) + '.00'
			return HttpResponse(url) #HttpResponseRedirect(url)
	else:
		form = QuestionForm(initial = {'bounty': u'10'})
	return render_to_response('ask.html', {'form': form}, context_instance = RequestContext(request))

def index(request):
	return render_to_response('index.html', {})

def question(request, question_id):
	question = Question.objects.get(pk = question_id)
	answers = Answer.objects.filter(question = question)
	return render_to_response('question.html', {'question': question, 'answers': answers})

def questions(request):
	questions = Question.objects.annotate(Count('answer'))
	return render_to_response('questions.html', {'questions': questions})
	
def tos(request):
	return render_to_response('tos.html', {})

class QuestionForm(forms.Form):
	text = forms.CharField(label = 'My Question:', widget = forms.Textarea)
	email = forms.EmailField(label = 'When my question is answered, notify me by email at:')
	email2 = forms.EmailField(label = 'Confirm email:')
	bounty = forms.CharField(label = 'Bounty for a correct answer:', widget = forms.Select(choices = (
		('1', '$1.00'),
		('2', '$2.00'),
		('3', '$3.00'),
		('5', '$5.00'),
		('10', '$10.00'),
		('15', '$15.00'),
		('20', '$20.00'),
		('25', '$25.00'),
		('30', '$30.00'),
		('40', '$40.00'),
		('50', '$50.00'),
		('100', '$100.00'),
	)))
	