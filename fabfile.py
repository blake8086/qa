from __future__ import with_statement
from fabric.api import abort, cd, env, local, run, settings
from fabric.contrib.console import confirm

env.hosts = ['blake8086@blake8086.webfactional.com']

def deploy(name):
	with cd('/home/blake8086/webapps/c4c_%s/qa/' % name):
		run('git pull')
	run('/home/blake8086/webapps/c4c_%s/apache2/bin/restart' % name)

def development():
	deploy('development')

def dev_log():
	run('tail -f /home/blake8086/logs/user/error_c4c_development.log')

def staging():
	deploy('staging')
	
def production():
	deploy('production')

def static():
	local('cp -r /Users/blake8086/Documents/qa/static/* /Library/WebServer/Documents/')
