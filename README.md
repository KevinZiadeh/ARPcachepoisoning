# ARPcachepoisoning
> University Project (EECE 655 @ AUB) where we implement an ARP attack and try to detect it

## Requirements

  For this attack to be performed, you need the following tools to be installed on the machine you will be performing this attacking from:
```
* Python 3
* Scapy 2.4.4
* Nmap 
```
  
## Overview
  The project consisted of two main parts:
    ARP spoofing attack launching
    ARP attack detection and prevention
  With the help of NMap, the attacker can view all potential victims on the LAN network to launch three types of ARP spoofing attacks.//talk about defense (1 phrase)//. The project resulted in launching successful ARP attacks that could be prevented by deploying a defensive monitor.
  
## Attack
  The first part of the attack consists of collecting the network data specially the IP/MAC pairs of all network components using NMap. After this step, the user can choose to launch three types of attack: Man-in-the-middle, Specific DOS (perturbation of victim's connection), and "Take down the network". 
  
  -->The first type is based on sending one gratuitous ARP message to the victim and one to the router. When the victim wants to send a message to the router or the inverse, it will pass by the attacker who will be working as an intermediary without the victim or router's knowledge. The victim will be storing the attacker's MAC address as the router MAC address and the router will be storing the attacker MAC address as the victim MAC address.
  
  -->The second type of attack is conceptually simple. It consists in falsifying the router MAC address in the victim ARP table. The victim won't be able to communicate anymore with the router!
  
  -->The last type of attack is based on sending an ARP message to all network devices and falsifying the router MAC address in all their tables. This attack was performed by specifying the victim IP address as the broadcast IP of the network.
 
 
The last two types of attacks perform by sending asynchronous and diversified ARP packets. Randomness is an important pillar to fool the defense system. The sending frequency and type of ARP message differ each iteration.

### Gathering Device Information - optional
You might want to insert the IP or MAC address manually of your device, router or other information. There are many ways to do it. 
On any linux distribution, you can run `ifconfig` and from it you can get your IP(inet), MAC(ether) and broadcast address. Also using the netmask and inet, you can get your router ip address. 
![](https://github.com/KevinZiadeh/ARPcachepoisoning/blob/main/res/ifconfig.png?raw=true)

Another way on linux is to go to Settings -> Network -> Press the wheel icon next to your connection and you will get a window similar to this.
![](https://github.com/KevinZiadeh/ARPcachepoisoning/blob/main/res/settings.png?raw=true)

On windows, you can run `ipconfig` to get the IP of the device and the router, from the IP and Subnet Mask you can get the broadcast IP. Running '`getmac` can give you the MAC of your device.

![](https://github.com/KevinZiadeh/ARPcachepoisoning/blob/main/res/ipconfig.png?raw=true)

![](https://github.com/KevinZiadeh/ARPcachepoisoning/blob/main/res/getmac.png?raw=true)

### Performing the Attack
After making sure you have all the requirements installed, all you need to do is navigate the the attack folder and run `python3 main_[OS].py`
You will just have to follow the instructions after it
```
$ git clone https://github.com/KevinZiadeh/ARPcachepoisoning.git
$ cd ARPcachepoisoning/Attack/
$ python3 main_Linux.py
```
Here is an example of how it should look like
![](https://github.com/KevinZiadeh/ARPcachepoisoning/blob/main/res/attack1.png?raw=true)

If all runs well and you give the correct information, you should see something similar to this
![](https://github.com/KevinZiadeh/ARPcachepoisoning/blob/main/res/attack2.png?raw=true)

To check if the attack is working, run `arp -a` before and while the attack if happening, and look at the entry in the ARP table.
![](https://github.com/KevinZiadeh/ARPcachepoisoning/blob/main/res/attack3.png?raw=true)

We can see that the MAC associated with the IP for the router `192.168.1.1` on interface `192.168.1.201` changed from `0c:80:63:52:f7:f6` to `90:34:ff:78:dd:2e`

## Detection
The detection tool works with the help of the Scapy package which allowed us to use commands to process all incoming packets and easily retrieve packet information. The tool was implemented for Windows (because they are usually the victims #Linux4Life :) ). It can be used to detect previous attacks, currently occurring attacks, or even future attacks as long as it is operating. It has a simple user interface that simply allows the user to select whether to initialize the tool or not. Please note that it may take some time to detect the attack for the first time. This was not always happening so we were not sure what was causing this. 
### How it works
The tool initially scans the host's ARP table on the fly, and checks if the entry that is to be added is a duplicate entry or not. If it is, then there is a problem, i.e. the attacker is poisoning our ARP table. This detection works against man-in-the-middle attacks since the attacker cannot spoof his MAC address. However, it does not work if the attacker is using a random MAC, i.e. not a duplicate one.

The screenshot below shows a sample run of the detection of man-in-the-middle attacks
![](https://github.com/KevinZiadeh/ARPcachepoisoning/blob/main/res/man-in-the-middle.png?raw=true)

The tool can also detect more complex attacks, in which the attacker randomizes the MAC address or uses a non-existing one, by sending out an ARP broadcast request with the IP address received in the attack packet to get the real MAC address of this IP. It then compares the MAC address it received from the broadcast with the source MAC address in the attack packet to detect any falsified association between an IP address and its MAC address. This works for both ARP requests and ARP reply attacks. 

The screenshot below shows a sample run of the detection of attacks where the attacker's MAC address is spoofed
![](https://github.com/KevinZiadeh/ARPcachepoisoning/blob/main/res/specific.png?raw=true)

## References
<https://github.com/mpostument/hacking_tools/blob/master/arp_spoof_detector/arp_spoof_detector.py>
