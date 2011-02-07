# Create your views here.
from django.shortcuts import render_to_response
from main.models import Answer, Question
from django.db.models import Count

def ask(request):
	return render_to_response('ask.html', {})

def index(request):
	return render_to_response('index.html', {})

def question(request, question_id):
	question = Question.objects.get(pk = question_id)
	answers = Answer.objects.filter(question = question)
	return render_to_response('question.html', {'question': question, 'answers': answers})

def questions(request):
	questions = Question.objects.annotate(Count('answer'))
	return render_to_response('questions.html', {'questions': questions})
	
#this is really just a placeholder from the mocks
def payment(request):
	return render_to_response('payment.html', {})

def tos(request):
	return render_to_response('tos.html', {})

