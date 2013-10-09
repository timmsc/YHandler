import requests
from rauth import OAuth1Service
from requests import request
import webbrowser
import csv
import os.path

GET_TOKEN_URL = 'https://api.login.yahoo.com/oauth/v2/get_token'
AUTHORIZATION_URL = 'https://api.login.yahoo.com/oauth/v2/request_auth'
REQUEST_TOKEN_URL = 'https://api.login.yahoo.com/oauth/v2/get_request_token'
CALLBACK_URL = 'oob'

sessionf = 'yahoo_session.txt'

class YHandler(object):

	def __init__(self, authf):
		self.authf = authf
		self.authd = self.get_authvals_csv(self.authf)
		self.session = None
		# Get a real consumer key & secret
		self.yahoo = OAuth1Service(
			name='yahoo',
			consumer_key=self.authd['consumer_key'],
			consumer_secret=self.authd['consumer_secret'],
			request_token_url=REQUEST_TOKEN_URL,
			access_token_url=GET_TOKEN_URL,
			authorize_url=AUTHORIZATION_URL,
			base_url='https://api.login.yahoo.com/oauth/v2/')

	def get_authvals_csv(self, authf):
		vals = {}	#dict of vals to be returned
		with open(authf, 'rb') as f:
			f_iter = csv.DictReader(f)
			vals = f_iter.next()
		return vals
		

	def write_authvals_csv(self, authd, authf):
		f = open(authf, 'wb')
		fieldnames = tuple(authd.iterkeys())
		headers = dict((n,n) for n in fieldnames)
		f_iter = csv.DictWriter(f, fieldnames=fieldnames)
		f_iter.writerow(headers)
		f_iter.writerow(authd)
		f.close

	def new_session(self):
		request_token, request_token_secret = self.yahoo.get_request_token(data = { 'oauth_callback': CALLBACK_URL })
		auth_url = self.yahoo.get_authorize_url(request_token)
		print 'Visit this URL in your browser: ' + auth_url
		pin = raw_input('Enter PIN from browser: ')
		session = self.yahoo.get_auth_session(request_token, request_token_secret, method='POST', data={'oauth_verifier': pin})
		f = open(sessionf, 'wb')
		f.write(session.access_token + '\n')
		f.write(session.access_token_secret + '\n')
		return session

	def reuse_session(self):
		f = open(sessionf, 'rb')
                access_token = f.readline().rstrip('\n')
                access_token_secret = f.readline().rstrip('\n')
		print 'access_token: ' + access_token
		print 'access_token_secret: ' + access_token_secret
		session = self.yahoo.get_session((access_token, access_token_secret))
		return session

	def api_req(self, querystring, req_meth='GET', data=None, headers=None):
		base_url = 'http://fantasysports.yahooapis.com/fantasy/v2/'
		url = base_url + querystring
		if (self.session is None):
			if (os.path.exists(sessionf)):
				self.session = self.reuse_session()
			else:
				self.session = self.new_session()
		print "calling url: ", url
		r=self.session.get(url)
	
		return r

	
