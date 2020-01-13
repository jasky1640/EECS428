/*
Copyright 2013-present Barefoot Networks, Inc. 

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
*/
#include <core.p4>
#include <v1model.p4>

// TODO: define headers & header instances

struct metadata {
    /* empty */
}

parser MyParser(packet_in packet,
	out headers hdr,
	inout metadata meta,
	inout standard_metadata_t standard_metadata) {
    // TODO: define parser states
}

control MyVerifyChecksum(inout headers hdr, inout metadata meta) {
    // leave empty
    apply {  }
}

control MyIngress (inout headers hdr,
		   inout metadata meta,
		   inout standard_metadata_t standard_metadata){

    action drop() {
	    mark_to_drop();
    }
    // TODO: route action to update packet headers & metadata
}

control MyEgress(inout headers hdr,
                 inout metadata meta,
                 inout standard_metadata_t standard_metadata) {
    // leave empty
    apply { }
}

control MyComputeChecksum(inout headers hdr, inout metadata meta) {
    // leave empty
    apply {  }
}

control MyDeparser(packet_out packet, in headers hdr) {
    // TODO: implement deparser
}

V1Switch(
MyParser(),
MyVerifyChecksum(),
MyIngress(),
MyEgress(),
MyComputeChecksum(),
MyDeparser()
) main;
