from ryu.base import app_manager
from ryu.controller import ofp_event
from ryu.controller.handler import MAIN_DISPATCHER
from ryu.controller.handler import set_ev_cls
from ryu.lib import mac
from ryu.lib.packet import packet
from ryu.lib.packet import ipv4
from ryu.lib.packet import arp
from ryu.ofproto import ofproto_v1_3
from ryu.ofproto import ether
from ryu import cfg

import json
import random
import netaddr


# Jiaqi Yang jxy530
class LoadBalancer(app_manager.RyuApp):
    OFP_VERSIONS = [ofproto_v1_3.OFP_VERSION]
    RYU_MAC = mac.haddr_to_bin('fe:ee:ee:ee:ee:ef')
    RYU_IP = int(netaddr.IPAddress('10.0.0.100'))
    ZERO_MAC = mac.haddr_to_bin('00:00:00:00:00:00')
    BROADCAST_MAC = mac.haddr_to_bin('ff:ff:ff:ff:ff:ff')

    # define the own attributes and states maintained by the controller
    def __init__(self, *args, **kwargs):
        super(LoadBalancer, self).__init__(*args, **kwargs)

        # Hopefully read the json file
        config_dict = cfg.CONF.user - flags
        # Exposed mac address to clients
        self.service_mac = config_dict.service_mac
        # Exposed ip address to clients for blue service
        self.service_blue_ip = config_dict.service_ips[0]
        # Exposed ip address to clients for red service
        self.service_red_ip = config_dict.service_ips[1]
        # List of real ip addresses for blue service
        self.server_blue_ips = config_dict.server_ips[0]
        # List of real ip addresses for red service
        self.server_red_ips = config_dict.server_ips[1]
        # Dictionary to store a ip address and its corresponding mac address
        self.ip_to_mac = {}
        self.mac_to_port = {}

    # Send arp requests to servers to learn their mac addresses
    def send_arp_requests(self, dp, ip_dst):
        # create ether and arp packets
        ether_pkt = ethernet.ethernet(self.BROADCAST_MAC, self.RYU_MAC, ether.ETH_TYPE_ARP)
        arp_pkt = arp.arp(hwtype=1, proto=ether.ETH_TYPE_IP, hlen=6, plen=4, opcode=arp.ARP_REQUEST,
                          src_mac=self.RYU_MAC, src_ip=self.RYU_IP, dst_mac=self.ZERO_MAC, dst_ip=ip_dst)
        pkt = packet.Packet()
        pkt.add_protocol(ether_pkt)
        pkt.add_protocol(arp_pkt)
        pkt.serialize()
        data = pkt.data

        # send the arp request packet
        buffer_id = 0xffffffff
        in_port = dp.ofproto.OFPP_LOCAL
        actions = [dp.ofproto_parser.OFPActionOutput(ofproto.OFPP_FLOOD)]
        msg = dp.ofproto_parser.OFPPacketOut(dp, buffer_id, in_port, actions, data)
        dp.send_msg(msg)

    # Send arp responds to server to acknowledge them the requested mac address
    def send_arp_responds(self, dp, eth_dst, ip_dst, ip_src):
        # create ether and arp packets
        ether_pkt = ethernet.ethernet(eth_dst, self.service_mac, ether.ETH_TYPE_ARP)
        arp_pkt = arp.arp(hwtype=1, proto=ether.ETH_TYPE_IP, hlen=6, plen=4, opcode=arp.ARP_REPLY,
                          src_mac=self.service_mac, src_ip=ip_src, dst_mac=eth_dst, dst_ip=ip_dst)
        pkt = packet.Packet()
        pkt.add_protocol(ether_pkt)
        pkt.add_protocol(arp_pkt)
        pkt.serialize()
        data = pkt.data

        # send the arp request packet
        buffer_id = 0xffffffff
        in_port = dp.ofproto.OFPP_LOCAL
        actions = [dp.ofproto_parser.OFPActionOutput(1, 0)]
        msg = dp.ofproto_parser.OFPPacketOut(dp, buffer_id, in_port, actions, data)
        dp.send_msg(msg)

    # def send_proxied_arp_response(self):
    # relay arp response to clients or servers
    # no need to insert entries into the flow table
    # WRITE YOUR CODE HERE

    # def send_proxied_arp_request(self):
    # relay arp requests to clients or servers
    # no need to insert entries into the flow table
    # WRITE YOUR CODE HERE

    # helper function to insert flow entries into flow table
    # by default, the idle_timeout is set to be 10 seconds
    def add_flow_entry(self, datapath, priority, match, actions, timeout=10):
        # A module which exports OpenFlow definitions for the negotiated OpenFlow version
        ofproto = datapath.ofproto
        # A module which exports OpenFlow wire message encoder and decoder for the negotiated OpenFlow version
        parser = datapath.ofproto_parser
        # Actions instruction to apply the action
        inst = [parser.OFPInstructionActions(ofproto.OFPIT_APPLY_ACTIONS, actions)]
        # The controller sends this message to modify the flow table
        mod = parser.OFPFlowMod(datapath=datapath, priority=priority, idle_timeout=timeout, match=match,
                                instruction=inst)
        # Queue an OpenFlow message to send to the corresponding switch
        datapath.send_msg(mod)

    # During the configuration/negotiation phase, Flood arp requests to all clients and servers
    @set_ev_cls(ofp_event.EventOFPSwitchFeatures, CONFIG_DISPATCHER)
    def switch_features_handler(self, ev):
        # Datapath is a class to describe an OpenFlow switch connected to this controller
        dp = ev.msg.datapath
        # A module which exports OpenFlow definitions for the negotiated OpenFlow version
        ofproto = dp.ofproto
        # A module which exports OpenFlow wire message encoder and decoder for the negotiated OpenFlow version
        parser = dp.ofproto_parser

        for blue_server_ip in self.server_blue_ips:
            self.send_arp_requests(dp=dp, ip_dst=blue_server_ip)
        for red_server_ip in self.server_red_ips:
            self.send_arp_requests(dp=dp, ip_dst=red_server_ip)

        # install table-miss flow entry
        match = parser.OFPMatch()
        actions = [parser.OFPActionOutput(ofproto.OFPP_CONTROLLER,
                                          ofproto.OFPCML_NO_BUFFER)]
        self.add_flow(datapath, 0, match, actions)

    # The switch sends the packet that received to the controller by this message
    @set_ev_cls(ofp_event.EventOFPPacketIn, MAIN_DISPATCHER)
    def packet_in_handler(self, ev):
        msg = ev.msg
        # Datapath is a class to describe an OpenFlow switch connected to this controller
        dp = msg.datapath
        # A module which exports OpenFlow definitions for the negotiated OpenFlow version
        ofproto = dp.ofproto
        # A module which exports OpenFlow wire message encoder and decoder for the negotiated OpenFlow version
        parser = dp.ofproto_parser
        # The port that the packet is transmitted in
        in_port = msg.match['in_port']

        pkt = packet.Packet(msg.data)
        # Return the firstly found protocol that matches to the specified protocol
        eth = pkt.get_protocol(ethernet.ethernet)
        # The destination mac address
        mac_dst = eth.dst
        # The source mac address
        mac_src = eth.src
        self.mac_to_port[src] = in_port
        self.logger.info("packet in %s %s %s", mac_src, mac_dst, in_port)

        # Ignore the request not to the service mac address
        if mac_dst != self.service_mac:
            return

        # learn a mac address and its corresponding in_port
        # in_port is valid to represent a client/server in this specific topology
        if mac_src not in self.mac_to_port:
            self.mac_to_port[mac_src] = in_port

        # Handle arp packets
        if eth.ethertype == ether_types.ETH_TYPE_ARP:
            p_arp = pkt.get_protocol(arp.arp)
            ip_dst = p_arp.dst_ip
            ip_src = p_arp.src_ip
            # Update ip_to_mac dictionary
            if ip_src not in self.ip_to_mac:
                self.ip_to_mac[ip_src] = mac_src

            # Handle arp request packet
            if p_arp.opcode == arp.ARP_REQUEST:
                # send arp response with exposed mac address
                self.send_arp_responds(dp=dp, eth_dst=mac_src, ip_dst=ip_src, ip_src=ip_dst)

            # Ignore any other types of arp packet, arp reply is already handled by updating dict
            else:
                return

        # Handle ip packets
        elif eth.ethertype == ether_types.ETH_TYPE_IP:
            # Return the firstly found protocol that matches to the specified protocol
            p_ip = pkt.get_protocol(ipv4.ipv4)
            ip_dst = p_ip.dst
            ip_src = p_ip.src
            # Update ip_to_mac dictionary
            if ip_src not in self.ip_to_mac:
                self.ip_to_mac[ip_src] = mac_src

            if ip_dst == self.service_blue_ip:
                # Randomly select one of blue ips
                selected_ip = random.choice(self.server_blue_ips)
            elif ip_dst == self.service_red_ip:
                # Randomly select one of red ips
                selected_ip = random.choice(self.server_red_ips)
            else:
                # Ignore the packets that don't call blue and red ips
                return

            # Insert the rule into the flow table
            selected_mac_addr = self.ip_to_mac[selected_ip]
            match = parser.OFPMatch(eth_type=ether_types.ETH_TYPE_IP, ipv4_src=ip_src, ipv4_dst=ip_dst,
                                    eth_src=mac_src, eth_dst=self.service_mac)
            actions = [parser.OFPActionOutput(self.mac_to_port[selected_mac_addr])]
            self.add_flow_entry(datapath=dp, priority=1, match=match, actions=actions)

            # Send the packet to the server
            data = None
            if msg.buffer_id == ofproto.OFP_NO_BUFFER:
                data = msg.data
            out = parser.OFPPacketOut(datapath=dp, buffer_id=msg.buffer_id,
                                      in_port=in_port, actions=actions, data=data)
            dp.send_msg(out)

        # Ignore any other types of packets
        else:
            return

    # When flow entries time out or are deleted, the switch notifies controller with this message
    @set_ev_cls(ofp_event.EventOFPFlowRemoved, MAIN_DISPATCHER)
    def flow_removed_handler(self, ev):
        msg = ev.msg
        dp = msg.datapath
        ofproto = dp.ofproto

        if msg.reason == ofproto.OFPRR_IDLE_TIMEOUT:
            reason = 'IDLE TIMEOUT'
        elif msg.reason == ofproto.OFPRR_HARD_TIMEOUT:
            reason = 'HARD TIMEOUT'
        elif msg.reason == ofproto.OFPRR_DELETE:
            reason = 'DELETE'
        elif msg.reason == ofproto.OFPRR_GROUP_DELETE:
            reason = 'GROUP DELETE'
        else:
            reason = 'unknown'

        self.logger.debug('OFPFlowRemoved received: '
                          'cookie=%d priority=%d reason=%s table_id=%d '
                          'duration_sec=%d duration_nsec=%d '
                          'idle_timeout=%d hard_timeout=%d '
                          'packet_count=%d byte_count=%d match.fields=%s',
                          msg.cookie, msg.priority, reason, msg.table_id,
                          msg.duration_sec, msg.duration_nsec,
                          msg.idle_timeout, msg.hard_timeout,
                          msg.packet_count, msg.byte_count, msg.match)
