import requests
import library
import yaml
from prettytable import PrettyTable

from keystoneauth1.identity import v3
from keystoneauth1 import session
import novaclient.client

datasource = open("polling.yaml", 'r')
info = yaml.load(datasource, Loader=yaml.FullLoader)

topoll=info['vms']

auth = v3.Password(auth_url=info['url'],
                   username=info['username'],
                   password=info['password'],
                   project_name=info['project_name'],
                   user_domain_name=info['user_domain_name'],
                   project_domain_name=info['project_domain_name'])

sess = session.Session(auth=auth, verify=False)

novac = novaclient.client.Client(2, session=sess)
vms=novac.servers.list()

for vm in vms:
    if vm.name in topoll and vm.status == 'ACTIVE':
        topoll.remove(vm.name)
        uuid=vm.id
        vmdet = requests.get("http://10.204.52.79:8081/analytics/uves/virtual-machine/"+uuid+"?flat").json()
        print "*** VM: " + vm.name + " ***"
        print "running on " + vmdet['UveVirtualMachineAgent']['vrouter']
        tab = PrettyTable()
        tab.field_names=["Interface Name", "IP Address", "Network","State", "Active", "Statistics"]
        for iface in vmdet['UveVirtualMachineAgent']['interface_list']:
            vmidet = requests.get("http://10.204.52.79:8081/analytics/uves/virtual-machine-interface/"+iface+"?flat").json()
            vn=vmidet['VMIStats']['virtual_network']
            ip=vmidet['UveVMInterfaceAgent']['ip_address']
            istate=vmidet['UveVMInterfaceAgent']['admin_state']
            active=vmidet['UveVMInterfaceAgent']['active']
            stats="Out Bytes: " + str(vmidet['VMIStats']['raw_if_stats']['out_bytes']) + "\n" + "In Bytes: " + str(vmidet['VMIStats']['raw_if_stats']['in_bytes']) + "\n" + "Out Packets: " + str(vmidet['VMIStats']['raw_if_stats']['out_pkts']) + "\n" + "Input Pakcets: " + str(vmidet['VMIStats']['raw_if_stats']['in_pkts']) + "\n"
            vminame=vmidet['ContrailConfig']['elements']['display_name']
            tab.add_row([vminame, ip, vn, istate, active, stats])
        print tab
        print ""

if len(topoll)>0:
    print "The following VMs could not not polled: " + str(topoll)
    print "Poosible reasons:"
    print "    - either not found with Nova"
    print "    - or not in ACTIVE state"
