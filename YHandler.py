import requests
#import rauth
from rauth import OAuth1Service
#from serializer import deserialize_session, serialize_session
#from oauth_hook import OAuthHook
from requests import request
from urlparse import parse_qs
#from xml.dom import minidom
import webbrowser
import csv

GET_TOKEN_URL = 'https://api.login.yahoo.com/oauth/v2/get_token'
AUTHORIZATION_URL = 'https://api.login.yahoo.com/oauth/v2/request_auth'
REQUEST_TOKEN_URL = 'https://api.login.yahoo.com/oauth/v2/get_request_token'
CALLBACK_URL = 'oob'

#request_token_url = "https://api.login.yahoo.com/oauth/v2/get_request_token"
#authorize_url = 'https://api.login.yahoo.com/oauth/v2/request_auth'
#access_token_url = 'https://api.login.yahoo.com/oauth/v2/get_token'

class YHandler(object):

	def __init__(self, authf):
		self.authf = authf
		self.authd = self.get_authvals_csv(self.authf)
		self.session = None

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

	def reg_user(self):
		
		init_oauth_hook = OAuth1Service( consumer_key=self.authd['consumer_key'], consumer_secret=self.authd['consumer_secret'], name='yahoo', access_token_url=GET_TOKEN_URL, authorize_url=AUTHORIZATION_URL, request_token_url=REQUEST_TOKEN_URL, base_url='https://api.login.yahoo.com/oauth/v2/')
		request_token, request_token_secret = init_oauth_hook.get_request_token(data = { 'oauth_callback': CALLBACK_URL })
		#print "Request Token:"
		#print " - oauth_token = %s" % request_token
		#print " - oauth_token_secret = %s" % request_token_secret
		#print
		auth_url = init_oauth_hook.get_authorize_url(request_token)
		print 'Visit this URL in your browser: ' + auth_url
		pin = raw_input('Enter PIN from browser: ')
		self.session = init_oauth_hook.get_auth_session(request_token, request_token_secret, method='POST', data={'oauth_verifier': pin})
		#self.get_login_token()
		return self.session

	def get_login_token(self):
		oauth_hook = OAuthHook(self.authd['oauth_token'], self.authd['oauth_token_secret'], self.authd['consumer_key'], self.authd['consumer_secret'])
		response = requests.post(GET_TOKEN_URL, {'oauth_verifier': self.authd['oauth_verifier']}, hooks={'pre_request': oauth_hook})
		qs = parse_qs(response.content)
		self.authd.update(map(lambda d: (d[0], (d[1][0])), qs.items()))
		self.write_authvals_csv(self.authd, self.authf)
		return response

	def refresh_token(self):
                oauth_hook = OAuth1Service( consumer_key=self.authd['consumer_key'], consumer_secret=self.authd['consumer_secret'], name='yahoo', access_token_url=GET_TOKEN_URL, authorize_url=AUTHORIZATION_URL, request_token_url=REQUEST_TOKEN_URL, base_url='https://api.login.yahoo.com/oauth/v2/')
                request_token, request_token_secret = init_oauth_hook.get_request_token(data = { 'oauth_callback': CALLBACK_URL })
                #print "Request Token:"
                #print " - oauth_token = %s" % request_token
                #print " - oauth_token_secret = %s" % request_token_secret
                #print
                auth_url = init_oauth_hook.get_authorize_url(request_token)
                print 'Visit this URL in your browser: ' + auth_url
                pin = raw_input('Enter PIN from browser: ')
                self.session = init_oauth_hook.get_auth_session(request_token, request_token_secret, method='POST', data={'oauth_verifier': pin})
########


		oauth_hook = OAuthHook(access_token=self.authd['oauth_token'], access_token_secret=self.authd['oauth_token_secret'], consumer_key=self.authd['consumer_key'], consumer_secret=self.authd['consumer_secret'])
		response = requests.post(GET_TOKEN_URL, {'oauth_session_handle': self.authd['oauth_session_handle']}, hooks={'pre_request': oauth_hook})
		qs = parse_qs(response.content)
		self.authd.update(map(lambda d: (d[0], (d[1][0])), qs.items()))
		self.write_authvals_csv(self.authd, self.authf)


	def call_api(self, url, req_meth='GET', data=None, headers=None):
		req_oauth_hook = OAuthHook(self.authd['oauth_token'], self.authd['oauth_token_secret'], self.authd['consumer_key'], self.authd['consumer_secret'], header_auth=True)
		client = requests.session(hooks={'pre_request':req_oauth_hook})
		return client.request(method=req_meth, url=url, data=data, headers=headers)

	def getText(self, nodelist):
		rc = []
		for node in nodelist:
			if node.nodeType == node.TEXT_NODE:
				rc.append(node.data)
		return ''.join(rc)

	def api_req(self, querystring, req_meth='GET', data=None, headers=None):
		#print "In api_req..."
		base_url = 'http://fantasysports.yahooapis.com/fantasy/v2/'
		url = base_url + querystring
		#if ('oauth_token' not in self.authd) or ('oauth_token_secret' not in self.authd) or (not (self.authd['oauth_token'] and self.authd['oauth_token_secret'])):
		if (self.session is None):
			self.reg_user()
		#query = self.call_api(url, req_meth, data=data, headers=headers)
#		r=self.session.get('http://fantasysports.yahooapis.com/fantasy/v2/users;use_login=1/games;game_keys=314/leagues');
#		print r.text
		print "calling url: ", url
		r=self.session.get(url)
#		if query.status_code != 200: #We have both authtokens but are being rejected. Assume token expired. This could be a LOT more robust
#			self.refresh_token()
#			query = self.call_api(url, req_meth, data=data, headers=headers)
#		xmldoc = minidom.parseString(r.text)
#		for matchup in xmldoc.getElementsByTagName('matchup'):  # visit every node <matchup />
#			teamName1 = self.getText(matchup.getElementsByTagName("name")[0].childNodes)
#			teamName2 = self.getText(matchup.getElementsByTagName("name")[1].childNodes)
#			score1 = self.getText(matchup.getElementsByTagName("team_points"[0]).getElementsByTagName("total"[0]).childNodes)
#			score2 = self.getText(matchup.getElementsByTagName("team_points"[1]).getElementsByTagName("total"[0]).childNodes)
#			print teamName1, " => ", score1, " vs. ", teamName2, " => ", score2
	
		return r

	
