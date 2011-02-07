from django.conf.urls.defaults import *
from django.contrib import admin

admin.autodiscover()

urlpatterns = patterns('',
    (r'^admin/', include(admin.site.urls)),
    (r'^ask$', 'main.views.ask'),
    (r'^question$', 'main.views.question'),
    (r'^questions$', 'main.views.questions'),
    (r'^payment$', 'main.views.payment'),
    (r'^tos$', 'main.views.tos'),
    (r'^', 'main.views.index'),
)
