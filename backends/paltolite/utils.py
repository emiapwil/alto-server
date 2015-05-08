#!/usr/bin/env python3

import SubnetTree
from palto.utils import correct_inet_format

def reverse_networkmap(networkmap_data, mapping = {}):
    for pid, groups in networkmap_data.items():
        for family, prefixes in groups.items():
            if not family in mapping:
                mapping[family] = SubnetTree.SubnetTree()
            prefixes = [ p for p in prefixes if correct_inet_format(family, p) ]
            for p in prefixes:
                mapping[family][p] = pid

    return mapping

def encode_addr(family, addr):
    return ':'.join([family, addr])

def decode_addr(addr):
    return addr.split(':')


