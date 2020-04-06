import json
import pprint
import sseclient
import requests
import time

url = 'http://10.204.52.79:8081/analytics/alarm-stream'
alarms=requests.get(url, stream=True)
client = sseclient.SSEClient(alarms)

for event in client.events():
    if json.loads(event.data) == None:
        continue
    alarm=json.loads(event.data)
    print "New Event @ " + time.asctime()
    print "NODE: " + alarm['key'].split(":")[1]
    print "Object Type: " + alarm['key'].split(":")[0]
    for issue in alarm['value']['alarms']:
        descr=issue['description']
        ts=time.ctime(int(issue['timestamp'])/1000000)
        print "    ALARM: " + descr
        #pprint.pprint(json.loads(event.data))
    print ""