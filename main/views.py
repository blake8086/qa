# Create your views here.
from django.shortcuts import render_to_response

def ask(request):
	return render_to_response('ask.html', {})

def index(request):
	return render_to_response('index.html', {})

def question(request):
	return render_to_response('question.html', {})

def questions(request):
	return render_to_response('answer.html', {})
	
#this is really just a placeholder from the mocks
def payment(request):
	return render_to_response('payment.html', {})

def tos(request):
	return render_to_response('tos.html', {})

