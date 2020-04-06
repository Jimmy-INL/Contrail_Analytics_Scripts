import requests
import library

alarms = requests.get("http://10.204.52.79:8081/analytics/alarms").json()

for role in alarms.keys():
    print "***** Found alarms for " + role + " type nodes *****\n"
    for node in alarms[role]:
        nodename=node['name']
        for issue in node['value']['UVEAlarms']['alarms']:
            descr=issue['description']
            print "Node called -> " + nodename + " - Issue: " + descr
            if descr == "Process(es) reporting as non-functional.":
                library.proc_non_funct(role, nodename)
            elif descr == "Process Failure.":
                library.proc_failure(role,nodename)
            elif descr == "BGP peer mismatch. Not enough BGP peers are up.":
                library.bgp_peer(role,nodename)
            print ""