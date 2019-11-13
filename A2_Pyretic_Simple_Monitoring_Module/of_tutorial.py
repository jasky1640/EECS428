# Jiaqi Yang (jxy530)

from pyretic.lib.corelib import *
from pyretic.lib.std import *
from pyretic.lib.query import *

class act_like_switch(DynamicPolicy):

    def __init__(self):
        super(act_like_switch,self).__init__()
        
        # Set up the initial forwarding behavior for your mac learning switch
        self.forward = flood()
        
        # Set up a query that will receive new incoming packets
        self.query = packets(limit=1, group_by=['srcmac', 'switch'])

        # Set up a query that will monitor new incoming packets
        self.monitor_query = count_packets(interval=1, group_by=['srcip','dstip'])
        
        # A method to learn the new rule
        def learn_from_a_packet(pkt):
            print pkt
            
            # set the forwarding policy
            self.forward = if_(match(dstmac=pkt['srcmac'], switch=pkt['switch']), fwd(pkt['port']), self.forward)
            print self.forward
            
            # update the dynamic policy to forward and query
            self.policy = self.forward + self.query

        # A method to print the incoming packet
        def packet_count_printer(counts):
                print '-----counts-----'
                print counts
            
        # learn_from_a_packet is called back every time our query sees a new packet
        self.query.register_callback(learn_from_a_packet)

        # packet_count_printer is called back every time our query sees a new packet
        self.monitor_query.register_callback(packet_count_printer)
        
        # update the dynamic policy to forward and query
        self.policy = self.forward + self.query + self.monitor_query


def main():
    return act_like_switch()
