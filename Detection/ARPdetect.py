from scapy.all import Ether, ARP, srp, sniff
import subprocess
import re
import sys

#Ghadi wrote the function below but logic from https://github.com/mpostument/hacking_tools/blob/master/arp_spoof_detector/arp_spoof_detector.py
def get_mac(ip):
    #Send an ARP Request Broadcast with an IP address to get the real mac address of that IP
    Broadcast = Ether(dst='ff:ff:ff:ff:ff:ff')
    ARP_request = ARP(pdst=ip)
    ARP_request_broadcast = Broadcast/ARP_request
    Result = srp(ARP_request_broadcast, timeout=1, verbose=False)[0]
    return Result[0][1].hwsrc

#Imad wrote the function below
def process(packet):
    # if the packet is an ARP packet
    data = str(subprocess.check_output("arp -a", shell=True))
    arp_dict = {}
    duplicate_mac=0
    if packet.haslayer(ARP):
        for line in re.findall('([-.0-9]+)\s+([-0-9a-f]{17})\s+(\w+)', data): #scan ARP table and check for duplicate entries
            mac= line[1]
            if 'static' == line[2]: #if static entry, probably means default entry and okay to have duplicates (mask,etc...)
                continue
            if mac in arp_dict:
                print("[!] You are under attack: Duplicate MAC")
                duplicate_mac=1
                break
            else:
                arp_dict[line[1]] = line[0]
        if not duplicate_mac:
            if packet[ARP].op == 1:
                try:
                    real_mac = get_mac(packet[ARP].psrc)
                    response_mac = packet[ARP].hwsrc
                    if response_mac == '00:00:00:00:00:00' or response_mac == packet[ARP].hwdst:
                        pass
                    elif real_mac != response_mac:
                        print("[!] You are under attack, REAL-MAC:",real_mac.upper(), "FAKE-MAC:", response_mac.upper())
                except IndexError:
                    pass
            #the section below is from https://github.com/mpostument/hacking_tools/blob/master/arp_spoof_detector/arp_spoof_detector.py
            #note that this section is only needed if the attacker's MAC is randomized
            elif packet[ARP].op == 2: # if it is an ARP response (ARP reply)
                try:
                    # get the real MAC address of the sender
                    real_mac = get_mac(packet[ARP].psrc)
                    # get the MAC address from the packet sent to us
                    response_mac = packet[ARP].hwsrc
                    # if they're different, definitely there is an attack
                    if real_mac != response_mac:
                        print("[!] You are under attack, REAL-MAC:", real_mac.upper(), "FAKE-MAC:", response_mac.upper())
                # else:
                # print("Working fine")
                except IndexError:
                    # unable to find the real mac
                    # may be a fake IP or firewall is blocking packets
                    pass

#Ghadi wrote the code below
choice = input("Would you like to initialize the ARP spoof detection? Press Y or y to initialize, press any other letter to exit: \n")

if choice == "Y" or choice == "y":
    print("ARP Spoof Detection initialized\n")
else:
    print("Exiting...")
    sys.exit()
sniff(store=False, prn=process)
