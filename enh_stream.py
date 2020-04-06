import json
import sseclient
import requests
import time
import library

nodemapping={
        'ObjectConfigDatabaseInfo':'config-database-node',
        'ObjectAnalyticsAlarmInfo':'analytics-alarm-node',
        'ObjectBgpRouter':'control-node',
        'ObjectDatabaseInfo':'database-node',
        'ObjectConfigNode':'config-node',
        'ObjectVRouter':'vrouter',
        'ObjectCollectorInfo':'analytics-node'
    }

url = 'http://10.204.52.79:8081/analytics/alarm-stream'
alarms=requests.get(url, stream=True)
client = sseclient.SSEClient(alarms)

for event in client.events():
    if json.loads(event.data) == None:
        continue
    alarm=json.loads(event.data)
    nodename=alarm['key'].split(":")[1]
    role=nodemapping[alarm['key'].split(":")[0]]
    for issue in alarm['value']['alarms']:
        descr=issue['description']
        print "Node called -> " + nodename + " - Issue: " + descr
        print "Object: " + alarm['key'].split(":")[0]
        if descr == "Process(es) reporting as non-functional.":
            library.proc_non_funct(role, nodename)
        elif descr == "Process Failure.":
            library.proc_failure(role,nodename)
        elif descr == "BGP peer mismatch. Not enough BGP peers are up.":
            library.bgp_peer(role,nodename)
        print ""
    print ""