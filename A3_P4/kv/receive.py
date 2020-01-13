#!/usr/bin/python

# Copyright 2013-present Barefoot Networks, Inc. 
# 
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# 
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from scapy.all import sniff, sendp
from scapy.all import Packet
from scapy.all import ShortField, IntField, LongField, BitField

import sys
import struct

def handle_pkt(pkt):
    pkt = str(pkt)
    if len(pkt) < 12: return
    preamble = pkt[:8]
    preamble_exp = "\x00" * 7 + "\x01"
    if preamble != preamble_exp: return
    msg_type =  ord(pkt[13])
    key = struct.unpack("!I", pkt[14:18])[0]
    value = struct.unpack("!I", pkt[18:])[0]
    if msg_type == 2:
	if value != 0:
	    print "GET Response: ", "key ", key, "has value ", value
	else:
	    print "GET Response: ", "key ", key, "does not exist"
    if msg_type == 3:
	print "PUT Response: ", "update key ", key, "with value ", value
    sys.stdout.flush()

def main():

    if len(sys.argv) != 2:
        print "Usage: receive.py [intf_name]"
        print "For example: receive.py h1-eth0"
        sys.exit(1)

    sniff(iface = sys.argv[1],
          prn = lambda x: handle_pkt(x))

if __name__ == '__main__':
    main()
