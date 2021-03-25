from genie.testbed import load
from genie.conf.base import Interface
from unicon.core.errors import ConnectionError
from genie.metaparser.util.exceptions import SchemaEmptyParserError
import sys


def route_state(devices):

    #Create empty dictionary for storing all route results
    pre_dic = {}

    #Loop over device dictionary
    for name, dev_name in devices.items():

        #create empty list to store route entries emdeded within complete_dic dictionary
        route_entries = []

        #create enbedded dictionary entry per device
        pre_dic.update({name: []})

        #learn routes from device
        routing = dev_name.learn('routing')
        print(routing.info)
        for vrf in routing.info['vrf'].keys():
            af = routing.info['vrf'][vrf]['address_family']
            for protocol in af.keys():
                routes = af[protocol]['routes']

                #Loop through list of learned routes, one interation per route
                for network in routes.keys():

                    #extract rotue and add to string variable
                    route = routes[network]['route']
                    #attempt to extract next hop info. If not available, use next-hop
                    outgoing_int = dev_name.api.get_dict_items(routes[network]['next_hop'], 'outgoing_interface')
                    next_hop = dev_name.api.get_dict_items(routes[network]['next_hop'], 'next_hop')
                    source_protocol =  dev_name.api.get_dict_items(routes[network], 'source_protocol')
                    metric = dev_name.api.get_dict_items(routes[network], 'metric')
                    # Add route entry to list
                    route_entries.append({route: {'outgoing_int': outgoing_int, 'next_hop': next_hop,
                                                  'source_protocol': source_protocol, 'metric': metric, 'route': route}})

        #Add group of routes to dictionary per-device
        pre_dic[name] = route_entries

    return pre_dic


def acl_state(devices):

    # Create empty dictionary for storing all route results
    pre_dic = {}

    # Loop over device dictionary
    for name, dev_name in devices.items():
        # create empty list to store route entries embedded within complete_dic dictionary
        acl_entries = []

        # create enbedded dictionary entry per device
        pre_dic.update({name: []})

        # learn routes from device
        acls = dev_name.learn('acl')
        try:
            acl_entries.append(acls.info)
            # Add group of routes to dictionary per-device
            pre_dic[name] = acl_entries
        except AttributeError:
            pass
    return pre_dic


def fragmentation_state(devices):

    # Create empty dictionary for storing all route results
    pre_dic = {}

    # Loop over device dictionary
    for name, dev_name in devices.items():

        # create empty list to store route entries emdeded within complete_dic dictionary
        inner_entries = []
        # create outer dictionary entry per device
        pre_dic.update({name: []})

        # determine if OS type is XE or XR and unpack ospf neighbors output and add to dictionary
        if dev_name.os == 'ios' or dev_name.os == 'iosxe':
            try:
                traffic = dev_name.parse('show ip traffic')
            except SchemaEmptyParserError:
                traffic = {}

            fragmented = traffic['ip_statistics']['ip_frags_fragmented']
            failed_to_fragment = traffic['ip_statistics']['ip_frags_no_fragmented']

            pre_dic.update({name: {'ip_frags_fragmented': fragmented,
                                             'ip_frags_no_fragmented': failed_to_fragment}})

        else:
            continue

    return pre_dic


def interface_state(devices):
    # Create empty dictionary for storing all route results
    pre_dic = {}

    # Loop over device dictionary
    for name, dev_name in devices.items():

        # create outer dictionary entry per device
        pre_dic[name] = {}

        # determine if OS type is XE or XR and unpack ospf neighbors output and add to dictionary
        if dev_name.os == 'iosxr':
            try:
                interfaces = dev_name.parse('show interfaces')
            except SchemaEmptyParserError:
                interfaces = {}

            if interfaces:
                for interface in interfaces.keys():

                    # limited data colleciton for loopback interfaces
                    if 'loop' in interface or 'Loop' in interface:
                        int_oper_state = interfaces[interface]['oper_status']
                        int_enabled = interfaces[interface]['enabled']

                        pre_dic[name].update(
                            {interface: {'int_oper_state': int_oper_state,
                                         'int_enabled': int_enabled}})
                        continue

                    elif "Null" in interface:
                        continue

                    int_link_state = interfaces[interface]['line_protocol']
                    int_oper_state = interfaces[interface]['oper_status']
                    int_enabled = interfaces[interface]['enabled']
                    mtu = interfaces[interface]['mtu']

                    # We can only pull IP address if it exists in dictionary
                    if 'ipv4' in interfaces[interface]:
                        ipv4_ip = interfaces[interface]['ipv4']
                    else:
                        ipv4_ip = ''

                    # We can only pull portmode info if it exists in dictionary. Only on switches
                    if 'port_mode' in interfaces[interface]:
                        switchport_mode = interfaces[interface]['port_mode']
                    else:
                        switchport_mode = ''

                    # We can only pull duplex mode info if it exists in dictionary
                    if 'duplex_mode' in interfaces[interface]:
                        duplex = interfaces[interface]['duplex_mode']
                    else:
                        duplex = ''

                    # We can only pull port speed info if it exists in dictionary
                    if 'port_speed' in interfaces[interface]:
                        speed = interfaces[interface]['port_speed']
                    else:
                        speed = ''

                    # Some interface details don't apply to MGMT
                    if ('mgmt' not in interface) or ('Mgmt' not in interface):
                        input_errors = interfaces[interface]['counters']['in_errors']
                        output_errors = interfaces[interface]['counters']['out_errors']
                        output_drops = interfaces[interface]['counters']['out_total_drops']
                    else:
                        input_errors = ''
                        output_errors = ''
                        output_drops = ''

                    pre_dic[name].update(
                        {interface: {'int_link_state': int_link_state, 'int_oper_state': int_oper_state,
                                     'ipv4_ip': ipv4_ip, 'mtu': mtu, 'input_errors': input_errors,
                                     'output_errors': output_errors, 'output_drops': output_drops,
                                     'int_enabled': int_enabled, 'duplex': duplex, 'speed': speed,
                                     'switchport_mode': switchport_mode}})


        elif dev_name.os == 'nxos':
            try:
                interfaces = dev_name.parse('show interface')
            except SchemaEmptyParserError:
                interfaces = {}

            if interfaces:
                for interface in interfaces.keys():

                    # limited data colleciton for loopback interfaces
                    if 'loop' in interface or 'Loop' in interface:
                        int_oper_state = interfaces[interface]['oper_status']
                        int_enabled = interfaces[interface]['enabled']

                        pre_dic[name].update(
                            {interface: {'int_oper_state': int_oper_state,
                                         'int_enabled': int_enabled}})
                        continue

                    int_link_state = interfaces[interface]['link_state']
                    int_oper_state = interfaces[interface]['oper_status']
                    int_enabled = interfaces[interface]['enabled']
                    mtu = interfaces[interface]['mtu']

                    # We can only pull IP address if it exists in dictionary
                    if 'ipv4' in interfaces[interface]:
                        ipv4_ip = interfaces[interface]['ipv4']
                    else:
                        ipv4_ip = ''

                    # We can only pull portmode info if it exists in dictionary. Only on switches
                    if 'port_mode' in interfaces[interface]:
                        switchport_mode = interfaces[interface]['port_mode']
                    else:
                        switchport_mode = ''

                    # We can only pull duplex mode info if it exists in dictionary
                    if 'duplex_mode' in interfaces[interface]:
                        duplex = interfaces[interface]['duplex_mode']
                    else:
                        duplex = ''

                    # We can only pull port speed info if it exists in dictionary
                    if 'port_speed' in interfaces[interface]:
                        speed = interfaces[interface]['port_speed']
                    else:
                        speed = ''

                    # Some interface details don't apply to MGMT
                    if 'mgmt' not in interface:
                        input_errors = interfaces[interface]['counters']['in_errors']
                        output_errors = interfaces[interface]['counters']['out_errors']
                        output_drops = interfaces[interface]['counters']['out_discard']
                    else:
                        input_errors = ''
                        output_errors = ''
                        output_drops = ''

                    pre_dic[name].update(
                        {interface: {'int_link_state': int_link_state, 'int_oper_state': int_oper_state,
                                     'ipv4_ip': ipv4_ip, 'mtu': mtu, 'input_errors': input_errors,
                                     'output_errors': output_errors, 'output_drops': output_drops,
                                     'int_enabled': int_enabled, 'duplex': duplex, 'speed': speed,
                                     'switchport_mode': switchport_mode}})

            else:
                log.info(f'{name} Trouble pulling interface data from interface. Skipping')


        elif dev_name.os == 'ios' or dev_name.os == 'iosxe':
            try:
                interfaces = dev_name.parse('show interfaces')
            except SchemaEmptyParserError:
                interfaces = {}

            if interfaces:
                for interface in interfaces.keys():

                    # limited data colleciton for loopback interfaces
                    if 'loop' in interface or 'Loop' in interface:
                        int_oper_state = interfaces[interface]['oper_status']
                        int_enabled = interfaces[interface]['enabled']

                        pre_dic[name].update(
                            {interface: {'int_oper_state': int_oper_state,
                                         'int_enabled': int_enabled}})
                        continue

                    elif "Null" in interface:
                        continue

                    int_link_state = interfaces[interface]['line_protocol']
                    int_oper_state = interfaces[interface]['oper_status']
                    int_enabled = interfaces[interface]['enabled']
                    mtu = interfaces[interface]['mtu']

                    # We can only pull IP address if it exists in dictionary
                    if 'ipv4' in interfaces[interface]:
                        ipv4_ip = interfaces[interface]['ipv4']
                    else:
                        ipv4_ip = ''

                    # We can only pull portmode info if it exists in dictionary. Only on switches
                    if 'port_mode' in interfaces[interface]:
                        switchport_mode = interfaces[interface]['port_mode']
                    else:
                        switchport_mode = ''

                    # We can only pull duplex mode info if it exists in dictionary
                    if 'duplex_mode' in interfaces[interface]:
                        duplex = interfaces[interface]['duplex_mode']
                    else:
                        duplex = ''

                    # We can only pull port speed info if it exists in dictionary
                    if 'port_speed' in interfaces[interface]:
                        speed = interfaces[interface]['port_speed']
                    else:
                        speed = ''

                    # Some interface details don't apply to MGMT
                    if ('mgmt' not in interface) or ('Mgmt' not in interface):
                        input_errors = interfaces[interface]['counters']['in_errors']
                        output_errors = interfaces[interface]['counters']['out_errors']
                        output_drops = interfaces[interface]['queues']['total_output_drop']
                    else:
                        input_errors = ''
                        output_errors = ''
                        output_drops = ''

                    pre_dic[name].update(
                        {interface: {'int_link_state': int_link_state, 'int_oper_state': int_oper_state,
                                     'ipv4_ip': ipv4_ip, 'mtu': mtu, 'input_errors': input_errors,
                                     'output_errors': output_errors, 'output_drops': output_drops,
                                     'int_enabled': int_enabled, 'duplex': duplex, 'speed': speed,
                                     'switchport_mode': switchport_mode}})

        else:
            sys.exit(f'{dev_name.os} OS type not supported')


    return pre_dic


def hsrp_state(devices):
    
    # Create empty dictionary for storing all route results
    pre_dic = {}

    # Loop over device dictionary
    for name, dev_name in devices.items():
        
        print(f'*******  Learning and Processing details for {name}  *******')

        # create outer dictionary entry per device
        pre_dic[name] = {}

        # determine if OS type is XE or XR and unpack ospf neighbors output and add to dictionary

        if dev_name.os == 'ios' or dev_name.os == 'iosxe' or dev_name.os == 'iosxr' or dev_name.os == 'nxos':
            try:
                hsrp = dev_name.learn('hsrp')
                if "info" in dir(hsrp):
                    hsrp = hsrp.info
                else:
                    hsrp = {}
            except SchemaEmptyParserError:
                hsrp = {}

            print(hsrp)
            if hsrp:
                for hsrp_int in hsrp.keys():
                    try:
                        pre_dic[name][hsrp_int] = {}
                        address_fams = hsrp[hsrp_int]['address_family']
                        for addr_fam in address_fams.keys():
                            hsrp_versions = address_fams[addr_fam]['version']
                            for version in hsrp_versions.keys():
                                hsrp_groups = hsrp_versions[version]['groups']
                                for group in hsrp_groups.keys():
                                    priority = hsrp_groups[group]['priority']
                                    virtual_mac = hsrp_groups[group]['virtual_mac_address']
                                    state = hsrp_groups[group]['hsrp_router_state']
                                    active_router = hsrp_groups[group]['active_router']

                                    pre_dic[name][hsrp_int].update({addr_fam: {
                                        group: {'priority': priority, 'v_mac': virtual_mac, 'state': state,
                                                'active_router': active_router}}})
                    except KeyError:
                        pre_dic[name] = {}

        else:
            sys.exit(f'{dev_name.os} OS type not supported')
    
    return pre_dic 



def eigrp_neighbors_state(devices):
    # Create empty dictionary for storing all route results
    pre_dic = {}

    # Loop over device dictionary
    for name, dev_name in devices.items():

        print(f'*******  Learning and Processing details for {name}  *******')

        # create outer dictionary entry per device
        pre_dic[name] = {}

        # determine if OS type is XE or XR and unpack ospf neighbors output and add to dictionary

        if dev_name.os == 'ios' or dev_name.os == 'iosxe' or dev_name.os == 'iosxr' or dev_name.os == 'nxos':
            try:
                eigrp = dev_name.learn('eigrp')
                if "info" in dir(eigrp):
                    eigrp = eigrp.info
                else:
                    eigrp = {}
            except SchemaEmptyParserError:
                eigrp = {}

            if eigrp:
                print(eigrp)
                eigrp_peers = dev_name.api.get_dict_items(eigrp, 'eigrp_nbr')
                print(eigrp_peers)

                pre_dic[name].update({'neighbors': eigrp_peers})


        else:
            sys.exit(f'{dev_name.os} OS type not supported')

    return pre_dic


def bgp_neighbors_state(devices):
    # Create empty dictionary for storing all route results
    pre_dic = {}

    # Loop over device dictionary
    for name, dev_name in devices.items():

        print(f'*******  Learning and Processing details for {name}  *******')

        # create outer dictionary entry per device
        pre_dic[name] = {}
        # determine if OS type is XE or XR and unpack ospf neighbors output and add to dictionary

        if dev_name.os == 'ios' or dev_name.os == 'iosxe' or dev_name.os == 'iosxr' or dev_name.os == 'nxos':
            try:
                bgp = dev_name.learn('bgp')
                if "info" in dir(bgp):
                    bgp = bgp.info
                else:
                    bgp = {}
            except SchemaEmptyParserError:
                bgp = {}

            if bgp:
                for instance in bgp['instance'].keys():
                    vrfs = bgp['instance'][instance]['vrf']
                    my_as = bgp['instance'][instance]['bgp_id']
                    for vrf in vrfs.keys():
                        if vrf == 'management':
                            continue
                        neighbors = vrfs[vrf]['neighbor']
                        for neighbor in neighbors.keys():
                            state = neighbors[neighbor]['session_state']
                            peer_as = neighbors[neighbor]['remote_as']
                            pre_dic[name].update(
                                {neighbor: {'ip': neighbor, 'state': state, 'local_as': my_as, 'peer_as': peer_as}})

        else:
            sys.exit(f'{dev_name.os} OS type not supported')

    return pre_dic


def dmvpn_state(devices):
    # Create empty dictionary for storing all route results
    pre_dic = {}

    # Loop over device dictionary
    for name, dev_name in devices.items():

        print(f'*******  Learning and Processing details for {name}  *******')

        # create outer dictionary entry per device
        pre_dic[name] = {}

        # determine if OS type is XE or XR and unpack ospf neighbors output and add to dictionary

        if dev_name.os == 'iosxe':
            try:
                dmvpn = dev_name.parse('show dmvpn')
            except SchemaEmptyParserError:
                dmvpn = {}

            if dmvpn:
                for dmvpn_int_list in dmvpn['interfaces'].keys():
                    interface = dmvpn['interfaces'][dmvpn_int_list]
                    interfaces = dmvpn_int_list
                    nhrp_peer_count = dev_name.api.get_dict_items(interface, 'nhrp_peers')
                    dmvpn_type = dev_name.api.get_dict_items(interface, 'type')
                    nbma_peers = dev_name.api.get_dict_items(interface, 'peers')
                    tunnel_peer_ip = dev_name.api.get_dict_items(interface, 'tunnel_addr')

                    pre_dic[name].update(
                        {interfaces: {'interface': interfaces, 'peer_count': nhrp_peer_count, 'type': dmvpn_type,
                                      'nbma_peers': nbma_peers, 'tunnel_peer': tunnel_peer_ip}})


        elif dev_name.os == 'ios' or dev_name.os == 'iosxr' or dev_name.os == 'nxos':
            pass

        else:
            sys.exit(f'{dev_name.os} OS type not supported')


    return pre_dic