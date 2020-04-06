import requests
from prettytable import PrettyTable
import time

def proc_non_funct(role, nodename):
    url="http://10.204.52.79:8081/analytics/uves/"+role+"/"+nodename+"?flat"
    nodeinfo=requests.get(url).json()
    tab = PrettyTable()
    tab.field_names=["Module Name", "Issue","Troubling Connections"]
    for module in nodeinfo['NodeStatus']['process_status']:
        noconn = ""
        for conn in module['connection_infos']:
            if conn['status'] != "Up":
                noconn+=conn['name']+"("+conn['type']+")"+"\n"+str(conn['server_addrs'])+"\n"+conn['description']+"\n\n"
        if noconn == "":
            noconn="-"
        if module['state'] == "Non-Functional":
            issue = module['description']
            moduleid = module['module_id']
            tab.add_row([moduleid, issue, noconn])
    print tab

def proc_failure(role, nodename):
    url="http://10.204.52.79:8081/analytics/uves/"+role+"/"+nodename+"?flat"
    nodeinfo=requests.get(url).json()
    tab = PrettyTable()
    tab.field_names=["Process", "State","Last Exit Time","Exit count"]
    for process in nodeinfo['NodeStatus']['process_info']:
        if "RUNNING" not in process['process_state']:
            tab.add_row([process['process_name'],process['process_state'],time.ctime(int(process['last_exit_time'])/1000000),process['exit_count']])
    print tab

def bgp_peer(role, nodename):
    url="http://10.204.52.79:8081/analytics/uves/"+role+"/"+nodename+"?flat"
    nodeinfo=requests.get(url).json()
    tab = PrettyTable()
    tab.field_names=["Peer", "Router Type","State","Last State","BGP type","Peer ASN","Last event"]
    for peer in nodeinfo['BgpRouterState']['bgp_config_peer_list']:
        peer_url="http://10.204.52.79:8081/analytics/uves/bgp-peer/"+peer+"?flat"
        peer_info=requests.get(peer_url).json()
        peer_info=peer_info['BgpPeerInfoData']
        if peer_info['state_info']['state']!="Established":
            tab.add_row([peer_info['peer_address'] , peer_info['router_type'] , peer_info['state_info']['state'] , peer_info['state_info']['last_state'] , peer_info['peer_type'] , peer_info['peer_asn'] , peer_info['event_info']['last_event'] +" @ " + time.ctime(int(peer_info['event_info']['last_event_at'])/1000000)])
    print tab