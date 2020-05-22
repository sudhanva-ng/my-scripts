from flask import Flask, request
import json
import requests
import csv

app = Flask(__name__)
app.debug = False


access_token = "MmYyYmQ2Y2QtNGIxOC00ODZkLWExMjEtNTZlYzA3ODE4ZmFlZGE0Y2U0NjYtODYx_PF84_1eb65fdf-9643-417f-9974-ad72cae0e10f"

httpHeaders = {"Content-type" : "application/json", "Authorization" : "Bearer " + access_token}

msg_thankYou = 'Thank you; your response has been recorded'

def listMsgs(roomId,person):
	global access_token, httpHeaders, msg
	person_name = person.replace('@cisco.com','')
	apiUrl = "https://webexapis.com/v1/messages"

	queryParams = {'roomId' : roomId}

	response = requests.get(url=apiUrl, headers=httpHeaders, params=queryParams)
	print(response.status_code)
	json_text = json.loads(response.text)
	if response.status_code == 200:
		for items in json_text['items']:
			if items['text'] not in [msg,msg_thankYou]:
				print ('!! Found new Msg from %s'%person)
				print (items['text'])
				sendMsg(person, msg_thankYou)
			else:
				break


def sendMsg(to, msg):
	global access_token, httpHeaders
	apiUrl = "https://webexapis.com/v1/messages"
	queryParams = {"toPersonEmail" : to, "text" : msg}

	response = requests.post(url=apiUrl, json=queryParams, headers=httpHeaders)

	print (response.status_code)
	#print (response.text)


def getPerson(json_content):
	print ('geet Person!')
	return(json_content['data']['personEmail'], json_content['data']['roomId'] )

@app.route('/', methods=['POST'])
def inboundsms():
    json_content = request.json
    #print (json.dumps(json_content))

    #print ('!!!!!')
    #print (json_content)

    person, roomId = getPerson(json_content)
    if person!=None:
    	#print(person)
    	listMsgs(roomId, person)



    return "OK"

msg = 'Are you happy with webex teams?'
sendMsg('sudng@cisco.com',  msg)
sendMsg('sindhu.br06@gmail.com',  msg)


if __name__ == '__main__':
    app.run(
        host="127.0.0.1",
        port=int("5000")
    )
