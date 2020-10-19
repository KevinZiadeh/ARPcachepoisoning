import subprocess, time
from victim import Victim
from attacker import Attacker
from network import Network
from color import Color #used to output to the terminals with colors

def initialize():
    Color.pl("{?} Doing pings to discover clients and build the ARP table")
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

    command = "nmap "+ routerIP +"/24 -n -sP | grep 'report\|MAC'" # discover users connected
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

    '''
    Insert info you need to use for the attack 
    User may want to use different values from what we found
    Do the attack 
    
    Detecting router needs testing
    
    Optional:
        Implement different ARP spoofing techniques that user can select
    '''
