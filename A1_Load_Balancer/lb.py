from ryu.base import app_manager
from ryu.controller import ofp_event
from ryu.controller.handler import MAIN_DISPATCHER
from ryu.controller.handler import set_ev_cls
from ryu.lib.packet import packet
from ryu.ofproto import ofproto_v1_3

import json

class LoadBalancer(app_manager.RyuApp):
    OFP_VERSIONS = [ofproto_v1_3.OFP_VERSION]

    def __init__(self, *args, **kwargs):
        super(LoadBalancer, self).__init__(*args, **kwargs)
        # define your own attributes and states maintained by the controller
        # WRITE YOUR CODE HERE

        # Hopefully read the json file
        with open('lb_config.json', 'r') as config_file:
            config_dict = json.load(config_file)
        # Exposed mac address to clients
        self.service_mac = config_dict['service_mac']
        # Exposed ip address to clients for blue service
        self.service_blue_ip = config_dict['service_ips'][0]
        # Exposed ip address to clients for red service
        self.service_red_ip = config_dict['service_ips'][1]
        # List of real ip addresses for blue service
        self.server_blue_ips = config_dict['server_ips'][0]
        # List of real ip addresses for red service
        self.server_red_ips = config_dict['server_ips'][1]

    def send_arp_requests(self, dp):
        # send arp requests to servers to learn their mac addresses
        # WRITE YOUR CODE HERE
		    
    def send_proxied_arp_response(self):
        # relay arp response to clients or servers
        # no need to insert entries into the flow table
        # WRITE YOUR CODE HERE

    def send_proxied_arp_request(self):
        # relay arp requests to clients or servers
        # no need to insert entries into the flow table
        # WRITE YOUR CODE HERE
         
    def add_flow_entry(self, datapath, priority, match, actions, timeout=10):
        # helper function to insert flow entries into flow table
        # by default, the idle_timeout is set to be 10 seconds
        # WRITE YOUR CODE HERE

        # A module which exports OpenFlow definitions for the negotiated OpenFlow version
        ofproto = datapath.ofproto
        # A module which exports OpenFlow wire message encoder and decoder for the negotiated OpenFlow version
        parser = datapath.ofproto_parser
        # Actions instruction to apply the action
        inst = [parser.OFPInstructionActions(ofproto.OFPIT_APPLY_ACTIONS, actions)]
        # The controller sends this message to modify the flow table
        mod = parser.OFPFlowMod(datapath=datapath, priority=priority, idle_timeout=10, match=match, instruction=inst)
        # Queue an OpenFlow message to send to the corresponding switch
        datapath.send_msg(mod)

    # The switch sends the packet that received to the controller by this message
    @set_ev_cls(ofp_event.EventOFPPacketIn, MAIN_DISPATCHER)
    def packet_in_handler(self, ev):
        msg = ev.msg
        # Datapath is a class to describe an OpenFlow switch connected to this controller
        dp = msg.datapath
        # 64-bit OpenFlow Datapath ID
        dpid = dp.id
        # A module which exports OpenFlow definitions for the negotiated OpenFlow version
        ofproto = dp.ofproto
        # A module which exports OpenFlow wire message encoder and decoder for the negotiated OpenFlow version
        parser = dp.ofproto_parser

        pkt = packet.Packet(msg.data)
        # Return the firstly found protocol that matches to the specified protocol
        eth = pkt.get_protocol(ethernet.ethernet)
        mac_dst = eth.dst
        mac_src = eth.src
        # Return the firstly found protocol that matches to the specified protocol
        ip = pkt.get_protocol(ipv6.ipv6)
        ip_dst = ip.dst
        ip_src = ip.src

        if eth.ethertype == ether_types.ETH_TYPE_ARP:
            # handle arp packets
            # WRITE YOUR CODE HERE
        
        elif eth.ethertype == ether_types.ETH_TYPE_IP:
            # handle ip packets
            # WRITE YOUR CODE HERE

    # When flow entries time out or are deleted, the switch notifies controller with this message
    @set_ev_cls(ofp_event.EventOFPFlowRemoved, MAIN_DISPATCHER)
    def flow_removed_handler(self, ev):
        # handle FlowRemoved event	
        # WRITE YOUR CODE HERE

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