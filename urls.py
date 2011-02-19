from django.conf.urls.defaults import *
from django.contrib import admin

admin.autodiscover()

urlpatterns = patterns('',
    (r'^admin/', include(admin.site.urls)),
    (r'^answer/(?P<answer_id>\d+)/edit$', 'main.views.answerEdit'),
    (r'^ask$', 'main.views.ask'),
	(r'^login$', 'main.views.loginView'),
	(r'^logout$', 'main.views.logoutView'),
    (r'^question/(?P<question_id>\d+)$', 'main.views.question'),
    (r'^question/(?P<question_id>\d+)/edit$', 'main.views.questionEdit'),
    (r'^questions$', 'main.views.questions'),
    (r'^tos$', 'main.views.tos'),
    (r'^', 'main.views.index'),
)
