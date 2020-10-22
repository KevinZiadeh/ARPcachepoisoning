# ARPcachepoisoning
University Project (EECE 655 @ AUB) where we implement a attack and try to detect it
Tested in Linux and Windows
## Requirements

  Python (version greater than 2.7)
  
  NMap
  
  Scapy
  
## Overview
  The project consisted of two main parts:
    ARP spoofing attack launching
    ARP attack detection and prevention
  With the help of NMap, the attacker can view all potential victims on the LAN network to launch three types of ARP spoofing attacks.//talk about defense (1 phrase)//. The project resulted in launching successful ARP attacks that could be prevented by deploying a defensive monitor.
  
## Attack
  The first part of the attack consists of collecting the network data specially the IP/MAC pairs of all network components using NMap. After this step, the user can choose to launch three types of attack: Man-in-the-middle, Specific DOS (perturbation of victim's connection), and "Take down the network". 
  
  -->The first type is based on sending one gracious ARP message to the victim and one to the router. When the victim wants to send a message to the router or the inverse, it will pass by the attacker who will be working as an intermediary without the victim or router's knowledge. The victim will be storing attacker's MAC address as the router MAC address and the router will be storing the attacker MAC address as the victim MAC address.
  
  -->The second type of attack is conceptually simple. It consists in falsifying the router MAC address in the victim ARP table. The victim won't be able to communicate anymore with the router!
  
  -->The last type of attack is based on sending an ARP message to all network devices and falsifying the router MAC address in all their tables. This attack was performed by specifying the victim IP address as the broadcast IP of the network.
 
 
The last two types of attacks perform by sending asynchronous and diversified ARP packets. Randomness is an important pillar to fool the defense system. The sending frequency and type of ARP message differ each iteration.


## Defense and Detection


### References
