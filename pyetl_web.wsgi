"""version wsgi"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.realpath(__file__)))

def application(environ, start_response):
	for key in environ:
		if isinstance(environ[key], str):
			os.environ[key] = environ[key]
	from pyetl_webapp import app
	return app(environ, start_response)