#### Paper Review October 31th 

##### Jiaqi Yang (jxy530)

------

##### Panopticon: Reaping the Benefits of Incremental SDN Deployment in Enterprise Networks

------

###### What problem is the paper solving and why is it important?

The problem that this paper addresses and tries to solve is that the conflict between the difficulty of SDN adoption and deployment in an enterprise network consisting of both legacy and SDN switches and the convenience of simplified management and enhanced flexibility brought by Software-Defined Networking (SDN) technology. The topic is important since it addresses the most challenging yet crucial problem in the SDN deployment in the enterprise network: how to start deploying and managing it in a complicated situation of a mixture of SDN and legacy switches. If this problem is not solved, then the deployment in mid to large enterprise network is doomed to failure. 

------

###### What is the main idea of the paper?

The main insight of this paper is that the benefits of SDN to enterprise networks can be realized for every source-destination path that includes at least one SDN switch. Therefore, instead of conducting a complete overhaul of switching hardware before realizing the benefits of SDN deployment, the SDN deployment on a small subset of all switches may suffice. That's the center idea of Panopticon: utilizing Solitary Confinement Tree mechanism, it ensures that traffic destined to operator-selected switchports on legacy devices passes through at least one SDN switch.

------

###### How does the paper differ from previous work?

The traditional approach to deploy SDN network is to spend years to fully deployed and only achieve benefits after a complete overhaul of the switching hardware, for example Google's software-defined WAN. However, the authors of this paper argue that even though considering all the opportunities and potentiality opened up by the SDN deployed, the enterprises are reluctant and even undesired to completely overhaul the network infrastructure before realizing the benefits; instead, they propose an alternative of SDN deployment in an incremental manner.

------

###### Are there any flaws in the paper? How would you improve the paper or build on it in future work?

The ability to accommodate more SDNc ports with the proposed methodology is largely based on the number of VLAN IDs supported for use by the legacy hardware since the method assign a unique VLAN ID to every end-to-end path and configure the legacy switches accordingly. Therefore, to deal with the major constraint in the way that small number of SDN switches support large amount of legacy switches, the future work might improve the current methodology by customizing the hardware or using something else than VLAN ID to represent the path.