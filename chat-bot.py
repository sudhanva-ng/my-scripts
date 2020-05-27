from flask import Flask, request
import json
import requests
import csv
from webex_person import webex_person
import random
import os
import subprocess, sys, time
from pyngrok import ngrok

app = Flask(__name__)
app.debug = False


access_token = "MmYyYmQ2Y2QtNGIxOC00ODZkLWExMjEtNTZlYzA3ODE4ZmFlZGE0Y2U0NjYtODYx_PF84_1eb65fdf-9643-417f-9974-ad72cae0e10f"

httpHeaders = {"Content-type" : "application/json", "Authorization" : "Bearer " + access_token}

msg = 'Do you want to play a game?'
msg_thankYou = 'Thank you; your response has been recorded'

AskQues = 1 

Questions = []


def createWebhook(url):
	apiUrl = 'https://webexapis.com/v1/webhooks'
	queryParams = {'name':'test', 'targetUrl':url, 'resource':'messages', 'event':'created'}
	response = requests.post(url=apiUrl, json=queryParams, headers=httpHeaders)

	print (response.status_code)

def runNgrok():
# 	p = subprocess.Popen('ngrok http 5000', shell=True, stderr=subprocess.PIPE)
# 	print ('hi')
 
# ## But do not wait till netstat finish, start displaying output immediately ##
# 	while True:
# 		out = p.stderr.read(1)
# 		if out == '' and p.poll() != None:
# 			break
# 		if out != '':
# 			#sys.stdout.write(out)
# 			print('!'+out)
# 			#sys.stdout.flush()

# 		if 'Forwarding' in out:
# 			url = re.search('Forwarding\s*(http.*)\s->')
# 			print (url)
# 			break

	public_url = ngrok.connect(5000,'http')
	return (public_url)

def sendMsg(to, msg):
	global access_token, httpHeaders
	apiUrl = "https://webexapis.com/v1/messages"
	queryParams = {"toPersonEmail" : to, "text" : msg}

	response = requests.post(url=apiUrl, json=queryParams, headers=httpHeaders)

	print (response.status_code)
	#print (response.text)


def getMsg(msgId):
	global access_token, httpHeaders
	apiUrl = "https://webexapis.com/v1/messages/"+msgId

	response = requests.get(url=apiUrl, headers=httpHeaders)
	#print(response.text)

	if response.status_code==200:
		out = json.loads(response.text)
		#print (type(out))
		return(out['text'])

def getQuestions():
	global Questions
	Questions = []
	url = 'https://opentdb.com/api.php'
	param = {'amount': '1', 'type':'multiple', 'category':'17'}

	response = requests.get(url=url, params=param)
	out = json.loads(response.text)
	if response.status_code == 200:

		for questions  in out['results']:
			ques = questions['question']
			opt = questions['incorrect_answers']
			opt.append(questions['correct_answer'])
			random.shuffle(opt)

			opt = '\n'.join(opt)

			ans = questions['correct_answer']

			Questions.append([ques, opt, ans])


@app.route('/', methods=['GET'])
def test():
	print ('Hello!!!!')
	return "OK"

@app.route('/', methods=['POST'])
def index():
	global  AskQues, Questions
	json_content = request.json

	if json_content['data']['personEmail'] == 'sudng-test@webex.bot':
		print ('My own msg; go to sleep')
	else:
		print ('real msg')
		msg = getMsg(json_content['data']['id'])
		person = json_content['data']['personEmail']
		print (len(Questions))

		if len(Questions) == 0 and 'yes' in msg:
			getQuestions()
			AskQues = 1

		elif len (Questions) == 0 and 'no' in msg:
			sendMsg(person, 'Bye!' )
			return "OK"

		elif (len(Questions)>0 and 'no' in msg) or ('Quit' in msg or 'quit' in msg):
			sendMsg(person, 'Bye!' )
			return "OK"

		elif 'start' in msg or 'Start' in msg:
			print ('here!!')

			getQuestions()
			AskQues = 1


		while len(Questions)>0:
			print ('inside while')

			if AskQues == 1 :
				print ('am here!')
				print(person)
				sendMsg(person, Questions[0][0] )
				sendMsg(person, Questions[0][1])
				AskQues = 0
				break

			elif  AskQues == 0:
				print ('elif?')
				if msg == Questions[0][2]:
					sendMsg(person, 'That is right!' )
					del(Questions[0])
					AskQues = 1

				else:
					AskQues = 1
					sendMsg(person, 'Sorry! Right answer is '+Questions[0][2] )
					del(Questions[0])



		if len (Questions) == 0 and 'yes' not in msg:
			sendMsg(person, 'Do you want to start again?')



	return "OK"

per = webex_person('sudng@cisco.com')

sendMsg(per.email,  'Do you want to play a game? Remeber I am just a yes/no bot but you can say "start" to startover or "quit" to end anytime')



if __name__ == '__main__':

	url = runNgrok()
	print (url)
	createWebhook(url)
	getQuestions()

	app.run(host="127.0.0.1",port=int("5000"))







