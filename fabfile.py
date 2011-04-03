from __future__ import with_statement
from fabric.api import abort, cd, env, local, run, settings
from fabric.contrib.console import confirm

env.hosts = ['blake8086@blake8086.webfactional.com']

def development():
	with cd('/home/blake8086/webapps/c4c_development/qa/'):
		run('git pull')
	run('/home/blake8086/webapps/c4c_development/apache2/bin/stop')
	#wait till it's down
	run('/home/blake8086/webapps/c4c_development/apache2/bin/start')
	#wait till it's up

def static():
	local('cp -r /Users/blake8086/Documents/qa/static/* /Library/WebServer/Documents/')
