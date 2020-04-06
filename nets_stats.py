import requests
import library
import yaml
from prettytable import PrettyTable

datasource = open("networks.yaml", 'r')
info = yaml.load(datasource, Loader=yaml.FullLoader)

fqdn_l=["","",""]

fo=open("stats.txt","w")

for dom in info['domains']:
    fqdn_l[0]=dom['name']
    for proj in dom['projects']:
        fqdn_l[1]=proj['name']
        for net in proj['networks']:
            net_tot={"inb":0.1,"outb":0.1,"inp":0.1,"outp":0.1}
            vrs_tot={}
            vmis_tot={}
            fqdn_l[2]=net
            fqdn=":".join(fqdn_l)
            netdet = requests.get("http://10.204.52.79:8081/analytics/uves/virtual-network/"+fqdn+"?flat").json()
            if bool(netdet) == False:
                print "Network: " + fqdn + " not found."
                fo.write("***** Network: " + net + " (FQDN " + fqdn + ") not found *****\n")
                fo.write("\n\n")
                continue
            print "***** Network: " + net + " *****"
            print "  Network has " + str(len(netdet['UveVirtualNetworkAgent']['interface_list'])) + " interfaces attached to it"
            fo.write("***** Network: " + net + " (FQDN " + fqdn + ") *****\n")
            fo.write("  Network has " + str(len(netdet['UveVirtualNetworkAgent']['interface_list'])) + " interfaces attached to it\n")
            for iface in netdet['UveVirtualNetworkAgent']['interface_list']:
                vmidet=requests.get("http://10.204.52.79:8081/analytics/uves/virtual-machine-interface/"+iface+"?flat").json()
                vrouter=requests.get("http://10.204.52.79:8081/analytics/uves/virtual-machine/"+vmidet['UveVMInterfaceAgent']['vm_uuid']+"?flat").json()['UveVirtualMachineAgent']['vrouter']
                if not vrs_tot.has_key(vrouter):
                    vrs_tot[vrouter]={"inb":0.1,"outb":0.1,"inp":0.1,"outp":0.1}
                inb=vmidet['VMIStats']['raw_if_stats']['in_bytes']
                outb=vmidet['VMIStats']['raw_if_stats']['out_bytes']
                inp=vmidet['VMIStats']['raw_if_stats']['in_pkts']
                outp=vmidet['VMIStats']['raw_if_stats']['out_pkts']
                vminame=vmidet['ContrailConfig']['elements']['display_name']
                vmis_tot[vminame]={}
                vmis_tot[vminame]={}
                vmis_tot[vminame]['inb']=inb
                vmis_tot[vminame]['outb']=outb
                vmis_tot[vminame]['inp']=inp
                vmis_tot[vminame]['outp']=outp
                vmis_tot[vminame]['vr']=vrouter
                vrs_tot[vrouter]['inb']+=inb
                vrs_tot[vrouter]['outb']+=outb
                vrs_tot[vrouter]['inp']+=inp
                vrs_tot[vrouter]['outp']+=outp
                net_tot['inb']+=inb
                net_tot['outb']+=outb
                net_tot['inp']+=inp
                net_tot['outp']+=outp
            tab = PrettyTable()
            tab.field_names=["Interface Name", "Compute", "IN B","OUT B", "IN pkts", "OUT pkts", "IN B (%cmp)","OUT B (%cmp)", "IN pkts (%cmp)", "OUT pkts (%cmp)", "IN B (%tot)","OUT B (%tot)", "IN pkts (%tot)", "OUT pkts (%tot)"]
            for x in vmis_tot.keys():
                vrouter=vmis_tot[x]['vr']
                tab.add_row([x, vmis_tot[x]['vr'], vmis_tot[x]['inb'], vmis_tot[x]['outb'], vmis_tot[x]['inp'], vmis_tot[x]['outp'], round(vmis_tot[x]['inb']/vrs_tot[vrouter]['inb']*100.0,), round(vmis_tot[x]['outb']/vrs_tot[vrouter]['outb']*100.0,0), round(vmis_tot[x]['inp']/vrs_tot[vrouter]['inp']*100.0,0), round(vmis_tot[x]['outp']/vrs_tot[vrouter]['outp']*100.0,0), round(vmis_tot[x]['inb']/net_tot['inb']*100.0,0), round(vmis_tot[x]['outb']/net_tot['outb']*100.0,0), round(vmis_tot[x]['inp']/net_tot['inp']*100.0,0), round(vmis_tot[x]['outp']/net_tot['outp']*100.0,0)])
            print tab
            print ""
            fo.write(tab.get_string())
            fo.write("\n\n")
            tab = PrettyTable()
            tab.field_names=["Compute", "IN B","OUT B", "IN pkts", "OUT pkts", "IN B (%tot)","OUT B (%tot)", "IN pkts (%tot)", "OUT pkts (%tot)"]
            for x in vrs_tot.keys():
                tab.add_row([x, vrs_tot[x]['inb'], vrs_tot[x]['outb'], vrs_tot[x]['inp'], vrs_tot[x]['outp'], round(vrs_tot[x]['inb']/net_tot['inb']*100.0,0), round(vrs_tot[x]['outb']/net_tot['outb']*100.0,0), round(vrs_tot[x]['inp']/net_tot['inp']*100.0,0), round(vrs_tot[x]['outp']/net_tot['outp']*100.0,0)])
            tab.add_row(["TOTAL", net_tot['inb'], net_tot['outb'], net_tot['inp'], net_tot['outp'], "100.0", "100.0", "100.0", "100.0"])
            print tab
            print ""
            fo.write(tab.get_string())
            fo.write("\n\n")
