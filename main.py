"""
Simple Facebook Echo bot: Respond with exactly what it receives
Standalone version
"""

import sys, json, traceback, requests
import urllib
from flask import Flask, request
#sys.tracebacklimit=0

keys=open('keys.txt',mode='rt')


application = Flask(__name__)
app = application
PAT = 'EAABgg5A4unABAGCGk9tW8SWLzZALMLh0M9ZCDrXHZBGIZABy80ZBW3m2x49xsFa7ZC0kGLRoWNO25uZBZC7SUvX2ZC8ehAvszxbekePu4AUdOllDvCr4ahiX8PQYQF37wSERLGzFpFECjsW72F5eP2WhnXeE0fR6VhVgFWRCzrZB11mAZDZD'
api_key=keys.readline().strip()
VERIFICATION_TOKEN =keys.readline().strip()
print '\n\n',api_key,VERIFICATION_TOKEN,'\n\n'
keys.seek(0)


result= False
faculty_number = False
enrolment_number= False
string=''
string_list=['']

result_input = []

@app.route('/', methods=['GET'])
def handle_verification():
    print "Handling Verification."
    if request.args.get('hub.verify_token', '') == VERIFICATION_TOKEN:
        print "Webhook verified!"
        return request.args.get('hub.challenge', '')
    else:
        return "Wrong verification token!"

# ======================= Bot processing ===========================
@app.route('/', methods=['POST'])
def handle_messages():
    print ('\n\n\nGetting mesages...')
    payload = request.get_data()

    # Handle messages
    for sender_id, message in messaging_events(payload):
        # Start processing valid requests
        try:
            response = processIncoming(sender_id, message)
            
            if response is not None:
                send_message(PAT, sender_id, response)

            else:
                send_message(PAT, sender_id, "I dont get it")
        except Exception, e:
            print e
            traceback.print_exc()
    return "ok"

def processIncoming(user_id, message):
    if message['type'] == 'text':
        message_text =text_message_response(message['data'],user_id)
        print('I received : ', message['data'])
        print('This is the message that i will return to handle_messages function that will be forwarded to send_message function. ',message_text )
        print('To : ',user_id)
        
        
        return message_text

    elif message['type'] == 'location':
        response = "I've received location (%s,%s) (y)"%(message['data'][0],message['data'][1])
        return response

    elif message['type'] == 'audio':
        audio_url = message['data']
        return "I've received audio %s"%(audio_url)

    # Unrecognizable incoming, remove context and reset all data to start afresh
    else:
        return "*scratch my head*"


def send_message(token, user_id, text):
    """Send the message text to recipient with id recipient.
    """
    if isinstance(text,list):
        #text.pop()

        for text2 in text:


            r = requests.post("https://graph.facebook.com/v2.6/me/messages",
                              params={"access_token": token},
                              data=json.dumps({
                                  "recipient": {"id": user_id},
                                  "message": {"text": text2}
                              }),
                              headers={'Content-type': 'application/json'})
            if r.status_code != requests.codes.ok:
                print r.text2
        #print(text[-1])


    else:
        r = requests.post("https://graph.facebook.com/v2.6/me/messages",
                          params={"access_token": token},
                          data=json.dumps({
                              "recipient": {"id": user_id},
                              "message": {"text": text.decode('unicode_escape')}
                          }),
                          headers={'Content-type': 'application/json'})

        if r.status_code != requests.codes.ok:
            print r.text

# Generate tuples of (sender_id, message_text) from the provided payload.
# This part technically clean up received data to pass only meaningful data to processIncoming() function
def messaging_events(payload):

    data = json.loads(payload)
    messaging_events = data["entry"][0]["messaging"]

    for event in messaging_events:
        sender_id = event["sender"]["id"]

        # Not a message
        if "message" not in event:
            yield sender_id, None

        # Pure text message
        if "message" in event and "text" in event["message"] and "quick_reply" not in event["message"]:
            data = event["message"]["text"].encode('unicode_escape')
            yield sender_id, {'type':'text', 'data': data, 'message_id': event['message']['mid']}

        # Message with attachment (location, audio, photo, file, etc)
        elif "attachments" in event["message"]:

            # Location
            if "location" == event['message']['attachments'][0]["type"]:
                coordinates = event['message']['attachments'][
                    0]['payload']['coordinates']
                latitude = coordinates['lat']
                longitude = coordinates['long']

                yield sender_id, {'type':'location','data':[latitude, longitude],'message_id': event['message']['mid']}

            # Audio
            elif "audio" == event['message']['attachments'][0]["type"]:
                audio_url = event['message'][
                    'attachments'][0]['payload']['url']
                yield sender_id, {'type':'audio','data': audio_url, 'message_id': event['message']['mid']}

            else:
                yield sender_id, {'type':'text','data':r"I don't\n understand what \ntype of messageg is this!", 'message_id': event['message']['mid']}

        # Quick reply message type
        elif "quick_reply" in event["message"]:
            data = event["message"]["quick_reply"]["payload"]
            yield sender_id, {'type':'quick_reply','data': data, 'message_id': event['message']['mid']}

        else:
            yield sender_id, {'type':'text','data':"I don't understand this", 'message_id': event['message']['mid']}


def text_message_response(text_data,user_id):
    global result,result_input,enrolment_number,faculty_number,string,string_list,api_key
    text_data_list= []

    if 'result' in text_data.lower():
        text_data_list=text_data.lower().split()

        for i in text_data_list:
            if len(i)==8:
                if i[0].isdigit() and i[-1].isdigit():
                    check(i,'fac')
            elif len(i)==6:
                if not i[0].isdigit() and i[-1].isdigit():
                    check(i,'enr')

        if len(result_input)==2:

            responseurl=urllib.urlopen("http://ctengg-api.appspot.com/result/btech?api_key="+api_key+"&fac="+result_input[0]+"&en="+result_input[1])
            data = json.loads(responseurl.read().decode())

            message_response =  make_string_list(data,0)
            result_input= [] //to be removed
            string_list=['']

        else:
            message_response='I can fetch result if the keywords <result>, <faculty_number>, <enrollment_number> are there in your message!. '

        result_input= []
        string_list=['']





    else:
        message_response=text_data
    result_input= [] //to be removed
    string_list=['']
    return message_response


def make_string(data,indent):           //to be removed
    global string
    for key,value in data.items():
        if isinstance(value,list):
            for i in value:
                make_string(i,1)
                string=string+r'\n'
        else:
            if indent==1:
                string=string+r'\n'+r'\t'+str(key)+' : '+str(value)
            else:
                string=string+r'\n'+str(key)+' : '+str(value)

    return string




def make_string_list(data,indent):          //improve this codes
    global string_list
    for key,value in data.items():
        if isinstance(value,list):
            string_list.append('Subject wise ' + str(key) + ' are :' )
            for i in value:
                string_list.append('')
                make_string_list(i,1)
                #string_list.append(r'\n')
            string_list.append('')
        else:
            if indent==1:
                string_list[-1]=string_list[-1]+'\n'+str(key)+' : '+str(value) 
            else:
                string_list[-1]=string_list[-1]+'\n'+str(key)+' : '+str(value)


    return string_list

def check(i,fac_enr):
    global result_input
    if fac_enr=='fac':
        if (i[1].isdigit() and
            not i[2].isdigit() and
            not i[3].isdigit() and
            not i[4].isdigit() and
            i[5].isdigit() and
            i[6].isdigit()):
            result_input.insert(0,i)

    if fac_enr=='enr':
        if (not i[1].isdigit() and
            i[2].isdigit() and
            i[3].isdigit() and
            i[4].isdigit()):
            result_input.insert(1,i)

# Allows running with simple `python <filename> <port>`
if __name__ == '__main__':
    if len(sys.argv) == 2: # Allow running on customized ports
        app.run(port=int(sys.argv[1]))
    else:
        app.run() # Default port 5000
