from django.conf.urls.defaults import *
from django.contrib import admin

admin.autodiscover()

urlpatterns = patterns('',
	(r'^activate/(?P<email>[^/]+)/(?P<key>.{8})$', 'qa.main.views.activate'),
    (r'^admin/', include(admin.site.urls)),
    (r'^answer/(?P<answer_id>\d+)/edit$', 'qa.main.views.answerEdit'),
    (r'^ask$', 'qa.main.views.ask'),
    (r'^faq$', 'qa.main.views.faq'),
	(r'^login$', 'qa.main.views.loginView'),
	(r'^logout$', 'qa.main.views.logoutView'),
	(r'^profile$', 'qa.main.views.profile'),
    (r'^question/(?P<question_id>\d+)$', 'qa.main.views.question'),
    (r'^question/(?P<question_id>\d+)/edit$', 'qa.main.views.questionEdit'),
    (r'^thanks/(?P<question_id>\d+)$', 'qa.main.views.thanks'),
    (r'^tos$', 'qa.main.views.tos'),
    (r'^', 'qa.main.views.questions'),
)
