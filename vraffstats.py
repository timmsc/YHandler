#!/usr/bin/python

import sys

from YHandler import *
#from xml.dom import minidom
try:
	import xml.etree.cElementTree as ET
except ImportError:
	import xml.etree.ElementTree as ET

week = sys.argv[1]

try:
	league = sys.argv[2]
except IndexError:
	league = '475902'
print 'Getting stats for league ' + league

def getText(nodelist):
	rc = []
	for node in nodelist:
		if node.nodeType == node.TEXT_NODE:
			rc.append(node.data)
	return ''.join(rc)

yhandler = YHandler('auth.csv')

usermap = {}	#dict of vals to be returned
with open('userteammap.csv', 'rt') as f:
	f_iter = csv.DictReader(f)
	for row in f_iter:
		usermap[row['team_key']] = row['user']

# 2013 NFL football game id: 314
leaguesQuery = 'users;use_login=1/games;game_keys=314/leagues'
standingsQuery = 'league/314.l.' + league + '/standings'
matchupQuery = 'league/314.l.' + league + '/scoreboard;week=' + week

resp = yhandler.api_req(leaguesQuery)

#print resp
#print resp.headers
#print resp.text

resp = yhandler.api_req(standingsQuery)

print resp.text

print 'Extracting scoreboard standings data from XML...'

root = ET.fromstring(resp.text)

league = root.find('{http://fantasysports.yahooapis.com/fantasy/v2/base.rng}league')
leagueName = league.find('{http://fantasysports.yahooapis.com/fantasy/v2/base.rng}name').text

for team in root.iter('{http://fantasysports.yahooapis.com/fantasy/v2/base.rng}team'):
	teamKey = team.find('{http://fantasysports.yahooapis.com/fantasy/v2/base.rng}team_key').text
	manager = usermap[teamKey]
	teamName = team.find('{http://fantasysports.yahooapis.com/fantasy/v2/base.rng}name').text
	tmPoints = team.find('{http://fantasysports.yahooapis.com/fantasy/v2/base.rng}team_points')
	points = tmPoints.find('{http://fantasysports.yahooapis.com/fantasy/v2/base.rng}total').text
	team_standings = team.find('{http://fantasysports.yahooapis.com/fantasy/v2/base.rng}team_standings')
	outcome_totals = team_standings.find('{http://fantasysports.yahooapis.com/fantasy/v2/base.rng}outcome_totals')
	wins = outcome_totals.find('{http://fantasysports.yahooapis.com/fantasy/v2/base.rng}wins').text
	losses = outcome_totals.find('{http://fantasysports.yahooapis.com/fantasy/v2/base.rng}losses').text
	ties = outcome_totals.find('{http://fantasysports.yahooapis.com/fantasy/v2/base.rng}ties').text
	rank = team_standings.find('{http://fantasysports.yahooapis.com/fantasy/v2/base.rng}rank').text

	print manager+'\t'+teamName+'\t'+wins+'-'+ties+'-'+losses+'\t'+points+'\t'+leagueName

print
print

resp = yhandler.api_req(matchupQuery)

print 'Extracting scoreboard matchup data from XML...' 

root = ET.fromstring(resp.text)

for matchup in root.iter('{http://fantasysports.yahooapis.com/fantasy/v2/base.rng}matchup'):
	for team in matchup.iter('{http://fantasysports.yahooapis.com/fantasy/v2/base.rng}team'):
		teamName = team.find('{http://fantasysports.yahooapis.com/fantasy/v2/base.rng}name').text
		teamKey = team.find('{http://fantasysports.yahooapis.com/fantasy/v2/base.rng}team_key').text
		team_points = team.find('{http://fantasysports.yahooapis.com/fantasy/v2/base.rng}team_points')
		score = team_points.find('{http://fantasysports.yahooapis.com/fantasy/v2/base.rng}total').text
		print teamName+'\t'+score

