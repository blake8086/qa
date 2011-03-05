from qa.main.models import Answer, Question
from qa.main.models import LogCallerToken, LogPaymentResponse, LogPipelineResponse, LogRecipientToken
from django.contrib import admin

admin.site.register([Answer, LogCallerToken, LogPaymentResponse, LogPipelineResponse, LogRecipientToken, Question])
