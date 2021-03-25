from genie.testbed import load
from genie.conf.base import Interface
from unicon.core.errors import ConnectionError
from genie.metaparser.util.exceptions import SchemaEmptyParserError
import sys

def ospf_interfaces_state(devices):

    #Create empty dictionary for storing all route results
    pre_dic = {}


    #Loop over device dictionary
    for name, dev_name in devices.items():



        #create empty list to store route entries emdeded within complete_dic dictionary
        inner_entries = []

        #create outer dictionary entry per device
        pre_dic.update({name: []})
        #pre_dic.update({'data': {name: []}})


        #determine if OS type is XE or XR and unpack ospf neighbors output and add to dictionary
        if dev_name.os == 'iosxr':
            try:
                ospf = dev_name.parse('show ospf vrf all-inclusive interface')
            except SchemaEmptyParserError:
                ospf = {}
            if ospf:
                for vrf in ospf['vrf'].keys():
                    ospf_instances = ospf['vrf'][vrf]['address_family']['ipv4']['instance']
                    for instance in ospf_instances.keys():
                        areas = ospf_instances[instance]['areas']
                        for area in areas:
                            ospf_interfaces = areas[area]['interfaces']
                            for ospf_interface in ospf_interfaces.keys():
                                int_name = ospf_interfaces[ospf_interface]['name']
                                inner_entries.append(int_name)
                pre_dic.update({name: inner_entries})
            else:
                log.info(f'{name} Not running OSPF. Skipping')

        elif (dev_name.os == 'iosxe') or (dev_name.os == 'ios'):
            try:
                ospf = dev_name.parse('show ip ospf interface')
            except SchemaEmptyParserError:
                ospf = {}
            if ospf:
                for vrf in ospf['vrf'].keys():
                    ospf_instances = ospf['vrf'][vrf]['address_family']['ipv4']['instance']
                    for instance in ospf_instances.keys():
                        areas = ospf_instances[instance]['areas']
                        for area in areas:
                            ospf_interfaces = areas[area]['interfaces']
                            for ospf_interface in ospf_interfaces.keys():
                                int_name = ospf_interfaces[ospf_interface]['name']
                                inner_entries.append(int_name)
                pre_dic.update({name: inner_entries})
            else:
                log.info(f'{name} Not running OSPF. Skipping')

        elif dev_name.os == 'nxos':
            try:
                ospf = dev_name.parse('show ip ospf interface')
            except SchemaEmptyParserError:
                ospf = {}
            if ospf:
                for vrf in ospf['vrf'].keys():
                    ospf_instances = ospf['vrf'][vrf]['address_family']['ipv4']['instance']
                    for instance in ospf_instances.keys():
                        areas = ospf_instances[instance]['areas']
                        for area in areas:
                            ospf_interfaces = areas[area]['interfaces']
                            for ospf_interface in ospf_interfaces.keys():
                                int_name = ospf_interfaces[ospf_interface]['name']
                                inner_entries.append(int_name)
                pre_dic.update({name: inner_entries})
            else:
                print(f'{name} Not running OSPF. Skipping')

        else:
            print(f'{dev_name.os} OS type not supported')


    return pre_dic


def ospf_neighbors_state(devices):
    # Create empty dictionary for storing all route results
    pre_dic = {}

    # Loop over device dictionary
    for name, dev_name in devices.items():


        # create outer dictionary entry per device
        pre_dic[name] = {}

        # determine if OS type is XE or XR and unpack ospf neighbors output and add to dictionary
        if dev_name.os == 'iosxr':
            try:
                ospf = dev_name.parse('show ospf vrf all-inclusive neighbor detail')
            except SchemaEmptyParserError:
                ospf = {}

            if ospf:
                for vrf in ospf['vrf'].keys():
                    ospf_instances = ospf['vrf'][vrf]['address_family']['ipv4']['instance']
                    for instance in ospf_instances.keys():
                        areas = ospf_instances[instance]['areas']
                        for area in areas.keys():
                            ospf_interfaces = areas[area]['interfaces']
                            for interface in ospf_interfaces.keys():
                                neighbors = ospf_interfaces[interface]['neighbors']
                                for ospf_id in neighbors.keys():
                                    peer_addresses = neighbors[ospf_id]['address']
                                    peer_router_id = neighbors[ospf_id]['neighbor_router_id']
                                    peer_state = neighbors[ospf_id]['state']
                                    pre_dic[name].update({peer_router_id: {
                                        'peer_router_id': peer_router_id, 'peer_addresses': peer_addresses,
                                        'state': peer_state}})

            else:
                print(f'{name} Not running OSPF. Skipping')

        elif (dev_name.os == 'iosxe') or (dev_name.os == 'ios'):
            try:
                ospf = dev_name.parse('show ip ospf neighbor detail')
            except SchemaEmptyParserError:
                ospf = {}
            if ospf:
                for vrf in ospf['vrf'].keys():
                    ospf_instances = ospf['vrf'][vrf]['address_family']['ipv4']['instance']
                    for instance in ospf_instances.keys():
                        areas = ospf_instances[instance]['areas']
                        for area in areas.keys():
                            ospf_interfaces = areas[area]['interfaces']
                            for interface in ospf_interfaces.keys():
                                neighbors = ospf_interfaces[interface]['neighbors']
                                for ospf_id in neighbors.keys():
                                    peer_addresses = neighbors[ospf_id]['address']
                                    peer_router_id = neighbors[ospf_id]['neighbor_router_id']
                                    peer_state = neighbors[ospf_id]['state']
                                    pre_dic[name].update({peer_router_id: {
                                        'peer_router_id': peer_router_id, 'peer_addresses': peer_addresses,
                                        'state': peer_state}})

            else:
                print(f'{name} Not running OSPF. Skipping')


        elif (dev_name.os == 'nxos'):
            try:
                ospf = dev_name.parse('show ip ospf neighbors detail')
            except SchemaEmptyParserError:
                ospf = {}
            if ospf:
                for vrf in ospf['vrf'].keys():
                    ospf_instances = ospf['vrf'][vrf]['address_family']['ipv4']['instance']
                    for instance in ospf_instances.keys():
                        areas = ospf_instances[instance]['areas']
                        for area in areas.keys():
                            ospf_interfaces = areas[area]['interfaces']
                            for interface in ospf_interfaces.keys():
                                neighbors = ospf_interfaces[interface]['neighbors']
                                for ospf_id in neighbors.keys():
                                    peer_addresses = neighbors[ospf_id]['address']
                                    peer_router_id = neighbors[ospf_id]['neighbor_router_id']
                                    peer_state = neighbors[ospf_id]['state']
                                    pre_dic[name].update({peer_router_id: {
                                        'peer_router_id': peer_router_id, 'peer_addresses': peer_addresses,
                                        'state': peer_state}})


            else:
                print(f'{name} Not running OSPF. Skipping')
        else:
            print(f'{dev_name.os} OS type not supported')


    return pre_dic


def ospf_spf_state(devices):

    # Create empty dictionary for storing all route results
    pre_dic = {}

    # Loop over device dictionary
    for name, dev_name in devices.items():

        # create empty list to store route entries emdeded within complete_dic dictionary
        inner_entries = []

        # create outer dictionary entry per device
        pre_dic.update({name: []})

        # determine if OS type is XE or XR and unpack ospf neighbors output and add to dictionary
        if dev_name.os == 'iosxr':
            try:
                ospf = dev_name.parse('show ospf vrf all-inclusive')
            except SchemaEmptyParserError:
                ospf = {}

            if ospf:
                for vrf in ospf['vrf'].keys():
                    instances = ospf['vrf'][vrf]['address_family']['ipv4']['instance']
                    for instance in instances.keys():
                        areas = instances[instance]['areas']
                        for area in areas.keys():
                            spf_runs = areas[area]['statistics']['spf_runs_count']

                pre_dic.update({name: spf_runs})
            else:
                log.info(f'{name} Not running OSPF. Skipping')

        elif (dev_name.os == 'iosxe') or (dev_name.os == 'ios') or (dev_name.os == 'nxos'):
            try:
                ospf = dev_name.parse('show ip ospf')
            except SchemaEmptyParserError:
                ospf = {}

            if ospf:
                for vrf in ospf['vrf'].keys():
                    instances = ospf['vrf'][vrf]['address_family']['ipv4']['instance']
                    for instance in instances.keys():
                        areas = instances[instance]['areas']
                        for area in areas.keys():
                            spf_runs = areas[area]['statistics']['spf_runs_count']

                pre_dic.update({name: spf_runs})

            else:
                log.info(f'{name} Not running OSPF. Skipping')

        else:
            sys.exit(f'{dev_name.os} OS type not supported')
    
    return pre_dic