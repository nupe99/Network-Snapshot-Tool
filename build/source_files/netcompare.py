from pyats import aetest
from genie.testbed import load
from genie.conf.base import Interface
import time
from genie.utils.diff import Diff
import logging
from unicon.core.errors import ConnectionError
from genie.metaparser.util.exceptions import SchemaEmptyParserError
import pymongo
import sys
from datetime import datetime
import bson
import nested_lookup


def ospf_neighbors(job_a, job_b, devices):

    #Create Outer results dictionary
    results = {}
    results['OSPF Neighbor State Check'] = {}

    # Database conneciton
    client = pymongo.MongoClient()

    # define database
    db = client['network_state']

    # check meta data to determine pre and post state jobs

    db_meta = db['MetaData']
    try:
        job_a_date = db_meta.find_one({"name": job_a})['date']
        job_b_date = db_meta.find_one({"name": job_b})['date']
    except Exception as e:
        sys.exit(f'{e} - Failure Querying MetaData Database for Jobs - {job_a} and {job_b}')

    if job_a_date < job_b_date:
        pre_job = job_a
        post_job = job_b
    elif job_a_date > job_b_date:
        pre_job = job_b
        post_job = job_a
    else:
        sys.exit("Something went wrong could not compare jobs dates")

    pre_job_collection = db[pre_job]
    post_job_collection = db[post_job]

    pre_job_bson = pre_job_collection.find_one({"name": "ospf_neighbors_state"})['data']
    pre_dic = bson.decode(pre_job_bson)

    post_job_bson = post_job_collection.find_one({"name": "ospf_neighbors_state"})['data']
    post_dic = bson.decode(post_job_bson)



    ###################
    #Start Diff testing
    ###################

    diff = Diff(pre_dic, post_dic)
    diff.findDiff()
    diff = str(diff)
    if not diff:
        print(f'No OSPF neighbor adjacency changes detected - Test Passed')
    else:
        print(f'There have been OSPF neighbor adjacency changes - Test Failed -  {diff}')

        for device in devices:

            logs = []

            missing_dic = {neighbor: other for (neighbor, other) in pre_dic[device].items() if
                       neighbor not in post_dic[device].keys()}

            if missing_dic:

                for missing in missing_dic.keys():

                    print(f'{device} -- Missing OSPF neighbor: {missing}')
                    logs.append(f'Missing OSPF neighbor: {missing}')

            added_dic = {neighbor: other for (neighbor, other) in post_dic[device].items() if
                     neighbor not in pre_dic[device].keys()}

            if added_dic:

                for added in added_dic.keys():
                    print(f'{device} -- New OSPF neighbor: {added}')
                    logs.append(f'New OSPF neighbor: {added}')

            for peer in pre_dic[device].keys():
                pre_peer = pre_dic[device][peer]
                if peer in post_dic[device]:
                    post_peer = post_dic[device][peer]
                else:
                    continue

                if pre_peer['state'] != post_peer['state']:

                    if not post_peer["state"]:
                        post_peer["state"] = "Down"

                    print(f'{device} -- OSPF neighbor {peer} state changed from {pre_peer["state"]} to {post_peer["state"]}')
                    logs.append(f'OSPF neighbor {peer} state changed from {pre_peer["state"]} to {post_peer["state"]}')

            results['OSPF Neighbor State Check'][device] = logs

    return results



def ospf_interfaces(job_a, job_b, devices):

    #Create Outer results dictionary
    results = {}
    results['OSPF Interface State Check'] = {}

    # Database conneciton
    client = pymongo.MongoClient()

    # define database
    db = client['network_state']

    # check meta data to determine pre and post state jobs

    db_meta = db['MetaData']
    try:
        job_a_date = db_meta.find_one({"name": job_a})['date']
        job_b_date = db_meta.find_one({"name": job_b})['date']
    except Exception as e:
        sys.exit(f'{e} - Failure Querying MetaData Database for Jobs - {job_a} and {job_b}')

    if job_a_date < job_b_date:
        pre_job = job_a
        post_job = job_b
    elif job_a_date > job_b_date:
        pre_job = job_b
        post_job = job_a
    else:
        sys.exit("Something went wrong could not compare jobs dates")

    pre_job_collection = db[pre_job]
    post_job_collection = db[post_job]

    pre_dic = pre_job_collection.find_one({"name": "ospf_int_state"})['data']
    

    post_dic = post_job_collection.find_one({"name": "ospf_int_state"})['data']

    ###################
    # Start Diff testing
    ###################

    diff = Diff(pre_dic, post_dic)
    diff.findDiff()
    diff = str(diff)
    if not diff:
        print(f'No OSPF interface changes detected - Test Passed')
    else:
        print(f'New OSPF interfaces detected - Test Failed -  {diff}')

        for device in devices:

            logs = []

            missing = [x for x in pre_dic[device] if x not in post_dic[device]]

            if missing:

                for device_missing in missing:
                    print(f'{device} -- OSPF no longer enabled on interface {device_missing}')
                    logs.append(f'OSPF no longer enabled on interface {device_missing}')

            added = [x for x in post_dic[device] if x not in pre_dic[device]]

            if added:

                for device_added in added:
                    print(f'{device} -- New OSPF interface added {device_added}')
                    logs.append(f'New OSPF interface added {device_added}')

            results['OSPF Interface State Check'][device] = logs

    return results


def ospf_spf(job_a, job_b, devices):
    # Create Outer results dictionary
    results = {}
    results['OSPF SPF State Check'] = {}

    # Database conneciton
    client = pymongo.MongoClient()

    # define database
    db = client['network_state']

    # check meta data to determine pre and post state jobs

    db_meta = db['MetaData']
    try:
        job_a_date = db_meta.find_one({"name": job_a})['date']
        job_b_date = db_meta.find_one({"name": job_b})['date']
    except Exception as e:
        sys.exit(f'{e} - Failure Querying MetaData Database for Jobs - {job_a} and {job_b}')

    if job_a_date < job_b_date:
        pre_job = job_a
        post_job = job_b
    elif job_a_date > job_b_date:
        pre_job = job_b
        post_job = job_a
    else:
        sys.exit("Something went wrong could not compare jobs dates")

    pre_job_collection = db[pre_job]
    post_job_collection = db[post_job]

    pre_dic = pre_job_collection.find_one({"name": "ospf_spf_state"})['data']

    post_dic = post_job_collection.find_one({"name": "ospf_spf_state"})['data']

    ###################
    # Start Diff testing
    ###################

    diff = Diff(pre_dic, post_dic)
    diff.findDiff()
    diff = str(diff)
    if not diff:
        print(f'No new OSPF SPF calculations detected - Test Passed')
    else:
        print(f'New OSPF calculations detected - Test Failed -  {diff}')

        for device in devices:
            logs = []

            before = pre_dic[device]
            after = post_dic[device]
            if before > after:
                print(f"Hostname {device}: Invalid. Pre state is greater than Post state. Counters may have been cleared. Skipping ")
                logs.append(f"Invalid. Pre state is greater than Post state. Counters may have been cleared. Skipping ")
            else:
                delta = after - before
                if delta >= 1:
                    print(f"Hostname {device}: New SPF calculations have occurred. There have been {delta} new SPF calculations")
                    logs.append(f"New SPF calculations have been detected. There have been {delta} new SPF runs")

            results['OSPF SPF State Check'][device] = logs

    return results



def routing_table(job_a, job_b, devices):
    # Create Outer results dictionary
    results = {}
    results['Routing Table State Check'] = {}

    # Database conneciton
    client = pymongo.MongoClient()

    # define database
    db = client['network_state']

    # check meta data to determine pre and post state jobs

    db_meta = db['MetaData']
    try:
        job_a_date = db_meta.find_one({"name": job_a})['date']
        job_b_date = db_meta.find_one({"name": job_b})['date']
    except Exception as e:
        sys.exit(f'{e} - Failure Querying MetaData Database for Jobs - {job_a} and {job_b}')

    if job_a_date < job_b_date:
        pre_job = job_a
        post_job = job_b
    elif job_a_date > job_b_date:
        pre_job = job_b
        post_job = job_a
    else:
        sys.exit("Something went wrong could not compare jobs dates")

    pre_job_collection = db[pre_job]
    post_job_collection = db[post_job]

    pre_job_bson = pre_job_collection.find_one({"name": "route_state"})['data']
    pre_dic = bson.decode(pre_job_bson)

    post_job_bson = post_job_collection.find_one({"name": "route_state"})['data']
    post_dic = bson.decode(post_job_bson)

    ###################
    # Start Diff testing
    ###################

    diff = Diff(pre_dic, post_dic)
    diff.findDiff()
    diff = str(diff)
    if not diff:
        print(f'No new OSPF SPF calculations detected - Test Passed')
    else:
        print(f'New OSPF calculations detected - Test Failed -  {diff}')

        for device in devices:
            logs = []

            print(f'Route Table Change Summary for device - {device}')
            pre_list_of_route = pre_dic[device]
            post_list_of_route = post_dic[device]

            # Create master pre-chenge route list
            before_route_list = []
            for pre_route in pre_list_of_route:
                for pre_subnet in pre_route.keys():
                    before_route_list.append(pre_subnet)

            # Create master pre-chenge route list
            after_route_list = []
            for post_route in post_list_of_route:
                for post_subnet in post_route.keys():
                    after_route_list.append(post_subnet)

            # Find missing routes from pre change to post
            missing_routes = [x for x in before_route_list if x not in after_route_list]
            if missing_routes:
                for missing_route in missing_routes:
                    print(f'Route {missing_route} is missing')
                    logs.append(f'Route {missing_route} is missing')

            # Find added routes from pre change to post
            added_routes = [x for x in after_route_list if x not in before_route_list]
            if added_routes:
                for added_route in added_routes:
                    print(f'Route {added_route} has been added')
                    logs.append(f'Route {added_route} has been added')

            # Find routers that haven't changes from pre to post
            # common_routes = [x for x in before_route_list if in after_route_list]

            # evaluate route parameter differences
            for pre_route in pre_list_of_route:
                for pre_subnet in pre_route.keys():
                    for post_route in post_list_of_route:
                        for post_subnet in post_route.keys():
                            if pre_route[pre_subnet]['route'] == post_route[post_subnet]['route']:
                                if pre_route[pre_subnet]['outgoing_int'] == post_route[post_subnet][
                                    'outgoing_int']:
                                    pass
                                else:
                                    if not pre_route[pre_subnet]['outgoing_int']:
                                        pre_route[pre_subnet]['outgoing_int'] = "Null"
                                    if not post_route[post_subnet]['outgoing_int']:
                                        post_route[post_subnet]['outgoing_int'] = "Null"

                                    print(
                                        f"Outgoing interface of route {pre_route[pre_subnet]['route']} changed from {pre_route[pre_subnet]['outgoing_int']} to {post_route[post_subnet]['outgoing_int']}")
                                    logs.append(f"Outgoing interface of route {pre_route[pre_subnet]['route']} changed from {pre_route[pre_subnet]['outgoing_int']} to {post_route[post_subnet]['outgoing_int']}")

                                if pre_route[pre_subnet]['next_hop'] == post_route[post_subnet]['next_hop']:
                                    pass
                                else:
                                    print(
                                        f"Next-hop of route {pre_route[pre_subnet]['route']} changed from {pre_route[pre_subnet]['next_hop']} to {post_route[post_subnet]['next_hop']}")
                                    logs.append(f"Next-hop of route {pre_route[pre_subnet]['route']} changed from {pre_route[pre_subnet]['next_hop']} to {post_route[post_subnet]['next_hop']}")

                                if pre_route[pre_subnet]['source_protocol'] == post_route[post_subnet][
                                    'source_protocol']:
                                    pass
                                else:
                                    print(
                                        f"Source Protocol for route {pre_route[pre_subnet]['route']} changed from {pre_route[pre_subnet]['source_protocol']} to {post_route[post_subnet]['source_protocol']}")
                                    logs.append(f"Source Protocol for route {pre_route[pre_subnet]['route']} changed from {pre_route[pre_subnet]['source_protocol']} to {post_route[post_subnet]['source_protocol']}")

                                if pre_route[pre_subnet]['metric'] == post_route[post_subnet][
                                    'metric']:
                                    pass
                                else:
                                    print(
                                        f"Routing Metric for route {pre_route[pre_subnet]['route']} changed from {pre_route[pre_subnet]['metric']} to {post_route[post_subnet]['metric']}")
                                    logs.append(f"Routing metric for route {pre_route[pre_subnet]['route']} changed from {pre_route[pre_subnet]['metric']} to {post_route[post_subnet]['metric']}")

                            else:
                                pass

            results['Routing Table State Check'][device] = logs

    return results



def acl_change(job_a, job_b, devices):
    # Create Outer results dictionary
    results = {}
    results['ACL Change State Check'] = {}

    # Database conneciton
    client = pymongo.MongoClient()

    # define database
    db = client['network_state']

    # check meta data to determine pre and post state jobs

    db_meta = db['MetaData']
    try:
        job_a_date = db_meta.find_one({"name": job_a})['date']
        job_b_date = db_meta.find_one({"name": job_b})['date']
    except Exception as e:
        sys.exit(f'{e} - Failure Querying MetaData Database for Jobs - {job_a} and {job_b}')

    if job_a_date < job_b_date:
        pre_job = job_a
        post_job = job_b
    elif job_a_date > job_b_date:
        pre_job = job_b
        post_job = job_a
    else:
        sys.exit("Something went wrong could not compare jobs dates")

    pre_job_collection = db[pre_job]
    post_job_collection = db[post_job]

    pre_job_bson = pre_job_collection.find_one({"name": "acl_state"})['data']
    pre_dic = bson.decode(pre_job_bson)

    post_job_bson = post_job_collection.find_one({"name": "acl_state"})['data']
    post_dic = bson.decode(post_job_bson)

    ###################
    # Start Diff testing
    ###################

    diff = Diff(pre_dic, post_dic)
    diff.findDiff()
    diff = str(diff)
    if not diff:
        print(f'No ACL changes detected - Test Passed')
    else:
        print(f'ACL changes detected - Test Failed -  {diff}')

        for device in devices:
            logs = []

            print(f'ACL Change Summary for device - {device}')
            pre_list_of_acl = pre_dic[device]
            post_list_of_acl = post_dic[device]

            pre_acl_names = {}
            post_acl_names = {}

            # Start Pre state validation
            for acl_set in pre_list_of_acl:
                if 'acls' in acl_set:
                    acls = acl_set['acls']
                    for acl in acls.keys():
                        pre_aces = []
                        acl_type = acls[acl]['type']
                        try:
                            aces = acls[acl]['aces']
                        except KeyError:
                            print(f"ACL {acl} doesn't have any entries")
                            pre_acl_names.update({acls[acl]['name']: {'type': acls[acl]['type'], 'aces': None}})
                            continue

                        for ace in aces.keys():
                            seq = aces[ace]['name']
                            pre_aces.append(aces[ace])

                        pre_acl_names.update(
                            {acls[acl]['name']: {'type': acls[acl]['type'], 'aces': pre_aces}})
                else:
                    pre_acl_names.update(
                        {'name': None, 'type': None, 'aces': None})

            # Start Post state validation
            for acl_set in post_list_of_acl:
                if 'acls' in acl_set:
                    acls = acl_set['acls']
                    for acl in acls.keys():
                        post_aces = []
                        acl_type = acls[acl]['type']
                        try:
                            aces = acls[acl]['aces']
                        except KeyError:
                            print(f"ACL {acl} doesn't have any entries")
                            post_acl_names.update({acls[acl]['name']: {'type': acls[acl]['type'], 'aces': None}})
                            continue

                        for ace in aces.keys():
                            seq = aces[ace]['name']
                            post_aces.append(aces[ace])

                        post_acl_names.update(
                            {acls[acl]['name']: {'type': acls[acl]['type'], 'aces': post_aces}})
                else:
                    post_acl_names.update(
                        {'name': None, 'type': None, 'aces': None})

            # Start comparision

            # List of ACLs that were removed
            missing_acls = {x: y for x, y in pre_acl_names.items() if x not in post_acl_names.keys()}
            if missing_acls:
                for miss_acl in missing_acls.keys():
                    print(f"Hostname: {device} --- ACL {miss_acl} is missing")
                    logs.append(f"ACL {miss_acl} is missing")
            else:
                pass

            # List of ACLs that were added
            added_acls = {x: y for x, y in post_acl_names.items() if x not in pre_acl_names.keys()}
            if added_acls:
                for add_acl in added_acls.keys():
                    print(f" Hostname: {device} --- ACL {add_acl} was added")
                    logs.append(f"ACL {add_acl} was added")
            else:
                pass

            # Check for modified ACLs
            # Loop thru pre ACLs as primary
            for pre_acl_name in pre_acl_names.keys():

                try:
                    # process each pre ACE individually and compare to post
                    pre_aces_list = pre_acl_names[pre_acl_name]['aces']
                    nested_lookup.nested_delete(pre_aces_list, 'statistics', in_place=True)

                    # use pre-acl name as key to ensure we're comparing the same ACL name
                    post_aces_list = post_acl_names[pre_acl_name]['aces']
                    nested_lookup.nested_delete(post_aces_list, 'statistics', in_place=True)

                # if ACL is removed and empty KeyError is thrown.
                except KeyError:
                    continue

                if pre_aces_list and post_aces_list:
                    for pre_acl in pre_aces_list:
                        if pre_acl in post_aces_list:

                            pass
                        else:
                            print(f"Hostname: {device} --- ACL {pre_acl_name} seq {pre_acl['name']} has been been modified")
                            logs.append(f"ACL {pre_acl_name} seq {pre_acl['name']} has been changed")

            # Check for modified ACLs
            # Loop thru post ACLs as primary
            for post_acl_name in post_acl_names.keys():

                try:
                    # process each pre ACE individually and compare to post
                    post_aces_list = post_acl_names[post_acl_name]['aces']
                    nested_lookup.nested_delete(post_aces_list, 'statistics', in_place=True)

                    # use pre-acl name as key to ensure we're comparing the same ACL name
                    pre_aces_list = pre_acl_names[post_acl_name]['aces']
                    nested_lookup.nested_delete(pre_aces_list, 'statistics', in_place=True)

                # If ACL is removed/empty then KeyError is thrown
                except KeyError:
                    continue

                if post_aces_list and pre_aces_list:
                    for post_acl in post_aces_list:
                        if post_acl in pre_aces_list:

                            pass
                        else:
                            print(f"Hostname: {device} --- ACL {post_acl_name} seq {post_acl['name']} has been been modified")
                            logs.append(
                                f"ACL {post_acl_name} seq {post_acl['name']} has been changed")

            results['ACL Change State Check'][device] = logs

    return results



def fragmentation_check(job_a, job_b, devices):
    # Create Outer results dictionary
    results = {}
    
    results['Fragmentation State Check'] = {}

    # Database conneciton
    client = pymongo.MongoClient()

    # define database
    db = client['network_state']

    # check meta data to determine pre and post state jobs

    db_meta = db['MetaData']
    try:
        job_a_date = db_meta.find_one({"name": job_a})['date']
        job_b_date = db_meta.find_one({"name": job_b})['date']
    except Exception as e:
        sys.exit(f'{e} - Failure Querying MetaData Database for Jobs - {job_a} and {job_b}')

    if job_a_date < job_b_date:
        pre_job = job_a
        post_job = job_b
    elif job_a_date > job_b_date:
        pre_job = job_b
        post_job = job_a
    else:
        sys.exit("Something went wrong could not compare jobs dates")

    pre_job_collection = db[pre_job]
    post_job_collection = db[post_job]

    pre_dic = pre_job_collection.find_one({"name": "frag_state"})['data']

    post_dic = post_job_collection.find_one({"name": "frag_state"})['data']

    ###################
    # Start Diff testing
    ###################

    diff = Diff(pre_dic, post_dic)
    diff.findDiff()
    diff = str(diff)
    if not diff:
        print(f'No ACL changes detected - Test Passed')
    else:
        print(f'ACL changes detected - Test Failed -  {diff}')

        for device in devices:
            logs = []

            # Checking for fragmentaitons
            # print(f'the pre dictionary {pre_dic[name]}')
            # print(f'the psot dictionary {post_dic[name]}')
            if pre_dic[device] and post_dic[device]:
                before_fragmented = pre_dic[device]['ip_frags_fragmented']
                after_fragmented = post_dic[device]['ip_frags_fragmented']

                if before_fragmented > after_fragmented:
                    print(
                        f"Hostname {device}: Invalid. Pre state is greater than Post state. Counters may have been cleared. Skipping ")
                    logs.append(
                        f"Invalid results. Pre state is greater than Post state. Counters may have been cleared. Re-run ")
                else:
                    delta = after_fragmented - before_fragmented
                    if delta >= 1:
                        print(
                            f"Hostname {device}: Fragmentation as occured. {delta} packets fragmented")
                        logs.append(
                            f"Fragmentation detected. {delta} new fragmented packets")

                # Checking for drops due to not being able to fragment
                before_fragmented = pre_dic[device]['ip_frags_no_fragmented']
                after_fragmented = post_dic[device]['ip_frags_no_fragmented']

                if before_fragmented > after_fragmented:
                    print(
                        f"Hostname {device}: Invalid. Pre state is greater than Post state. Counters may have been cleared. Skipping ")
                    logs.append(
                        f"Invalid results. Pre state is greater than Post state. Counters may have been cleared. Re-run ")
                else:
                    delta = after_fragmented - before_fragmented
                    if delta >= 1:
                        print(
                            f"Hostname {device}: New packet drops have occured due to failure to fragment one or more packets. {delta} new drops")
                        logs.append(
                            f"New packet drops detected due to failure to fragment packets. {delta} new packet drops detected")

                results['Fragmentation State Check'][device] = logs

    return results


def interface_check(job_a, job_b, devices):
    # Create Outer results dictionary
    results = {}

    results['Interface State Check'] = {}

    # Database conneciton
    client = pymongo.MongoClient()

    # define database
    db = client['network_state']

    # check meta data to determine pre and post state jobs

    db_meta = db['MetaData']
    try:
        job_a_date = db_meta.find_one({"name": job_a})['date']
        job_b_date = db_meta.find_one({"name": job_b})['date']
    except Exception as e:
        sys.exit(f'{e} - Failure Querying MetaData Database for Jobs - {job_a} and {job_b}')

    if job_a_date < job_b_date:
        pre_job = job_a
        post_job = job_b
    elif job_a_date > job_b_date:
        pre_job = job_b
        post_job = job_a
    else:
        sys.exit("Something went wrong could not compare jobs dates")

    pre_job_collection = db[pre_job]
    post_job_collection = db[post_job]

    pre_job_bson = pre_job_collection.find_one({"name": "interface_state"})['data']
    pre_dic = bson.decode(pre_job_bson)

    post_job_bson = post_job_collection.find_one({"name": "interface_state"})['data']
    post_dic = bson.decode(post_job_bson)

    ###################
    # Start Diff testing
    ###################

    diff = Diff(pre_dic, post_dic)
    diff.findDiff()
    diff = str(diff)
    if not diff:
        print(f'No Interface changes detected - Test Passed')
    else:
        print(f'Interfaces changes detected - Test Failed -  {diff}')

        for device in devices:
            logs = []
            print(f'pre---- {pre_dic}')
            print(f'post---- {post_dic}')
            for pre_interface in pre_dic[device].keys():
                # Check to ensure interface exists in both pre and post dictionary. To ensure interface hasn't been removed
                if pre_interface in post_dic[device]:

                    # special handling for loopbacks. They have limited data
                    if 'loop' in pre_interface or 'Loop' in pre_interface:
                        # check Loopback interface operational state
                        if pre_dic[device][pre_interface]['int_oper_state'] != \
                                post_dic[device][pre_interface]['int_oper_state']:
                            print(
                                f"{device} -- {pre_interface} operational state changed to {post_dic[device][pre_interface]['int_oper_state']}")

                        # No further checks for loopbacks
                    else:
                        # All other interfaces that are not loopbacks

                        # check speed
                        if pre_dic[device][pre_interface]['speed'] != post_dic[device][pre_interface][
                            'speed'] and post_dic[device][pre_interface]['speed']:
                            print(
                                f"{device} -- {pre_interface} speed changed to {post_dic[device][pre_interface]['speed']}")
                            logs.append(
                                f"{pre_interface} speed changed to {post_dic[device][pre_interface]['speed']}")

                        # check duplex
                        if pre_dic[device][pre_interface]['duplex'] != post_dic[device][pre_interface][
                            'duplex'] and post_dic[device][pre_interface]['duplex']:
                            print(
                                f"{device} -- {pre_interface} duplex changed to {post_dic[device][pre_interface]['duplex']}")
                            logs.append(
                                f"{pre_interface} duplex changed to {post_dic[device][pre_interface]['duplex']}")

                        # check interface operational state
                        if pre_dic[device][pre_interface]['int_oper_state'] != \
                                post_dic[device][pre_interface]['int_oper_state']:
                            print(
                                f"{device} -- {pre_interface} operational state changed to {post_dic[device][pre_interface]['int_oper_state']}")
                            logs.append(
                                f"{pre_interface} operational state changed to {post_dic[device][pre_interface]['int_oper_state']}")

                        # check interface operational state
                        if pre_dic[device][pre_interface]['int_link_state'] != \
                                post_dic[device][pre_interface]['int_link_state']:
                            print(
                                f"{device} -- {pre_interface} link state changed to {post_dic[device][pre_interface]['int_link_state']}")
                            logs.append(
                                f"{pre_interface} link state changed to {post_dic[device][pre_interface]['int_link_state']}")

                        # check ipv4 address
                        print(f'pre --- {pre_dic[device][pre_interface]}')
                        print(f'post --- {post_dic[device][pre_interface]}')
                        if pre_dic[device][pre_interface]['ipv4_ip'] != \
                                post_dic[device][pre_interface]['ipv4_ip']:
                            for pre_ip in pre_dic[device][pre_interface]['ipv4_ip'].keys():
                                for post_ip in post_dic[device][pre_interface]['ipv4_ip'].keys():
                                    print(
                                        f"{device} -- {pre_interface} ip address changed to {post_dic[device][pre_interface]['ipv4_ip'][post_ip]}")
                                    logs.append(
                                        f"{pre_interface} ip address changed to {post_ip}")

                        # check interface MTU
                        if pre_dic[device][pre_interface]['mtu'] != \
                                post_dic[device][pre_interface]['mtu']:
                            print(
                                f"{device} -- {pre_interface} interface MTU changed to {post_dic[device][pre_interface]['mtu']}")
                            logs.append(
                                f"{pre_interface} interface MTU changed to {post_dic[device][pre_interface]['mtu']}")

                        # check interface output drops
                        if pre_dic[device][pre_interface]['output_drops'] != post_dic[device][pre_interface][
                            'output_drops']:
                            difference = post_dic[device][pre_interface]['output_drops'] - \
                                         pre_dic[device][pre_interface]['output_drops']
                            print(
                                f"{device} -- {pre_interface} interface output drops have increased to {difference}")
                            logs.append(
                                f"{pre_interface} interface output drops have increased to {difference}")

                        # check input errors
                        if pre_dic[device][pre_interface]['input_errors'] != post_dic[device][pre_interface][
                            'input_errors']:
                            difference = post_dic[device][pre_interface]['input_errors'] - \
                                         pre_dic[device][pre_interface]['input_errors']
                            print(
                                f"{device} -- {pre_interface} interface input errors have increased by {difference}")
                            logs.append(
                                f"{pre_interface} interface input errors have increased by {difference}")

                        # check output errors
                        if pre_dic[device][pre_interface]['output_errors'] != post_dic[device][pre_interface][
                            'output_errors']:
                            difference = post_dic[device][pre_interface]['output_errors'] - \
                                         pre_dic[device][pre_interface]['output_errors']
                            print(
                                f"{device} -- {pre_interface} interface output errors have increased by {difference}")
                            logs.append(
                                f"{pre_interface} interface output errors have increased by {difference}")

                        # check for switchport mode
                        if pre_dic[device][pre_interface]['switchport_mode'] != \
                                post_dic[device][pre_interface]['switchport_mode']:
                            print(
                                f"{device} -- {pre_interface} interface switchport mode changed from {pre_dic[device][pre_interface]['switchport_mode']} to {post_dic[device][pre_interface]['switchport_mode']}")
                            logs.append(
                                f"{pre_interface} interface switchport mode changed from {pre_dic[device][pre_interface]['switchport_mode']} to {post_dic[device][pre_interface]['switchport_mode']}")

            results['Interface State Check'][device] = logs

    return results


def bgp_neighbors(job_a, job_b, devices):
    # Create Outer results dictionary
    results = {}
    results['BGP Neighbors State Check'] = {}

    # Database conneciton
    client = pymongo.MongoClient()

    # define database
    db = client['network_state']

    # check meta data to determine pre and post state jobs

    db_meta = db['MetaData']
    try:
        job_a_date = db_meta.find_one({"name": job_a})['date']
        job_b_date = db_meta.find_one({"name": job_b})['date']
    except Exception as e:
        sys.exit(f'{e} - Failure Querying MetaData Database for Jobs - {job_a} and {job_b}')

    if job_a_date < job_b_date:
        pre_job = job_a
        post_job = job_b
    elif job_a_date > job_b_date:
        pre_job = job_b
        post_job = job_a
    else:
        sys.exit("Something went wrong could not compare jobs dates")

    pre_job_collection = db[pre_job]
    post_job_collection = db[post_job]

    pre_job_bson = pre_job_collection.find_one({"name": "bgp_neighbors_state"})['data']
    pre_dic = bson.decode(pre_job_bson)

    post_job_bson = post_job_collection.find_one({"name": "bgp_neighbors_state"})['data']
    post_dic = bson.decode(post_job_bson)



    ###################
    # Start Diff testing
    ###################

    diff = Diff(pre_dic, post_dic)
    diff.findDiff()
    diff = str(diff)
    print(diff)

    if not diff:
        print(f'No BGP neighbor changes detected - Test Passed')
    else:
        print(f'BGP neighbor changes detected - Test Failed')


        for device in devices:

            logs =[]

            # identify missing peers
            missing_peer = [x for x in pre_dic[device].keys() if x not in post_dic[device].keys()]

            if missing_peer:
                for x in missing_peer:
                    print(f"{device} -- BGP neighbor {x} is missing")
                    logs.append(f"BGP neighbor {x} is missing")

            # identify new peers
            new_peer = [x for x in post_dic[device].keys() if x not in pre_dic[device].keys()]

            if new_peer:
                for x in new_peer:
                    print(f"{device} -- BGP neighbor {x} has been added")
                    logs.append(f"BGP neighbor {x} has been added")

            # Identify existing peers with changes in state

            common_neighbors = [x for x in pre_dic[device].keys() if x in post_dic[device].keys()]

            for neighbor in common_neighbors:

                # ccheck for changes in peering state
                if pre_dic[device][neighbor]['state'] != post_dic[device][neighbor]['state']:
                    print(
                        f"{device} -- Change in BGP peering state detected. State change from {pre_dic[device][neighbor]['state']} to {post_dic[device][neighbor]['state']}")
                    logs.append(
                        f"Change in BGP peering state detected. State change from {pre_dic[device][neighbor]['state']} to {post_dic[device][neighbor]['state']}")
    
                # check for local AS change
                if pre_dic[device][neighbor]['local_as'] != post_dic[device][neighbor]['local_as']:
                    print(
                        f"{device} -- Local BGP AS changed. Changed from {pre_dic[device][neighbor]['state']} to {post_dic[device][neighbor]['state']}")
                    logs.append(
                        f"Local BGP AS changed. Changed from {pre_dic[device][neighbor]['state']} to {post_dic[device][neighbor]['state']}")
                    # Check for neighbor AS change

                    if pre_dic[device][neighbor]['peer_as'] != post_dic[device][neighbor]['peer_as']:
                        print(
                            f"{device} -- The AS number of neighbor {neighbor} has changed.  change from {pre_dic[device][neighbor]['state']} to {post_dic[device][neighbor]['state']}")
                        logs.append(f"The AS number of neighbor {neighbor} has changed.  Changed from {pre_dic[device][neighbor]['state']} to {post_dic[device][neighbor]['state']}")

            results['BGP Neighbors State Check'][device] = logs

    return results


def eigrp_neighbors(job_a, job_b, devices):
    # Create Outer results dictionary
    results = {}
    results['EIGRP Neighbors State Check'] = {}

    # Database conneciton
    client = pymongo.MongoClient()

    # define database
    db = client['network_state']

    # check meta data to determine pre and post state jobs

    db_meta = db['MetaData']
    try:
        job_a_date = db_meta.find_one({"name": job_a})['date']
        job_b_date = db_meta.find_one({"name": job_b})['date']
    except Exception as e:
        sys.exit(f'{e} - Failure Querying MetaData Database for Jobs - {job_a} and {job_b}')

    if job_a_date < job_b_date:
        pre_job = job_a
        post_job = job_b
    elif job_a_date > job_b_date:
        pre_job = job_b
        post_job = job_a
    else:
        sys.exit("Something went wrong could not compare jobs dates")

    pre_job_collection = db[pre_job]
    post_job_collection = db[post_job]

    pre_job_bson = pre_job_collection.find_one({"name": "eigrp_neighbors_state"})['data']
    pre_dic = bson.decode(pre_job_bson)

    post_job_bson = post_job_collection.find_one({"name": "eigrp_neighbors_state"})['data']
    post_dic = bson.decode(post_job_bson)

    ###################
    # Start Diff testing
    ###################

    diff = Diff(pre_dic, post_dic)
    diff.findDiff()
    diff = str(diff)
    print(diff)

    if not diff:
        print(f'No EIGRP neighbor changes detected - Test Passed')
    else:
        print(f'EIGRP neighbor changes detected - Test Failed')


        for device in devices:

            logs =[]

            # EIGRP neighbor results could be string or list. Do a conversion to list to ensure consistent data type
            if pre_dic[device]:

                pre_peer_list = []
                post_peer_list = []

                if isinstance(pre_dic[device]['neighbors'], str):
                    pre_peer_list.append(pre_dic[device]['neighbors'])
                elif isinstance(pre_dic[device]['neighbors'], list):
                    pre_peer_list = [str(x[0]) for x in pre_dic[device]['neighbors']]

                if isinstance(post_dic[device]['neighbors'], str):
                    post_peer_list.append(post_dic[device]['neighbors'])
                elif isinstance(post_dic[device]['neighbors'], list):
                    post_peer_list = [str(x[0]) for x in post_dic[device]['neighbors']]

                missing_peer = [x for x in pre_peer_list if x not in post_peer_list]

                if missing_peer:
                    print(f"{device} -- The following neighbors are missing {missing_peer}")
                    logs.append(f"The following neighbors are missing {missing_peer}")

                new_peer = [x for x in post_peer_list if x not in pre_peer_list]

                if new_peer:
                    print(f"{device} -- The following eigrp peers have been added {new_peer}")
                    logs.append(f"The following eigrp peers have been added {new_peer}")

            results['EIGRP Neighbors State Check'][device] = logs

    return results


def dmvpn(job_a, job_b, devices):
    # Create Outer results dictionary
    results = {}
    results['DMVPN State Check'] = {}

    # Database conneciton
    client = pymongo.MongoClient()

    # define database
    db = client['network_state']

    # check meta data to determine pre and post state jobs

    db_meta = db['MetaData']
    try:
        job_a_date = db_meta.find_one({"name": job_a})['date']
        job_b_date = db_meta.find_one({"name": job_b})['date']
    except Exception as e:
        sys.exit(f'{e} - Failure Querying MetaData Database for Jobs - {job_a} and {job_b}')

    if job_a_date < job_b_date:
        pre_job = job_a
        post_job = job_b
    elif job_a_date > job_b_date:
        pre_job = job_b
        post_job = job_a
    else:
        sys.exit("Something went wrong could not compare jobs dates")

    pre_job_collection = db[pre_job]
    post_job_collection = db[post_job]

    pre_job_bson = pre_job_collection.find_one({"name": "dmvpn_state"})['data']
    pre_dic = bson.decode(pre_job_bson)

    post_job_bson = post_job_collection.find_one({"name": "dmvpn_state"})['data']
    post_dic = bson.decode(post_job_bson)

    ###################
    # Start Diff testing
    ###################

    diff = Diff(pre_dic, post_dic)
    diff.findDiff()
    diff = str(diff)
    print(diff)

    if not diff:
        print(f'No DMVPN changes detected - Test Passed')
    else:
        print(f'DMVPN changes detected - Test Failed')


        for device in devices:

            logs = []

            # Find removed DMVPN interfaces

            missing = [x for x in pre_dic[device].keys() if x not in post_dic[device].keys()]
            if missing:
                for inter in missing:
                    print(f'{device} -- DMVPN no longer enabled on interface {inter}')
                    logs.append(f'DMVPN no longer enabled on interface {inter}')

            # Find new DMVPN interfaces

            added = [x for x in post_dic[device].keys() if x not in pre_dic[device].keys()]
            if added:
                for inter in added:
                    print(f'{device} -- New DMVPN interface detected, {inter}')
                    logs.append(f'{device} -- New DMVPN interface detected, {inter}')

            # Create list of common DMVPN interfaces beween pre and post state capture

            common_ints = [x for x in pre_dic[device].keys() if x in post_dic[device].keys()]

            for interface in common_ints:

                # Check DMVPN Peer Count
                if pre_dic[device][interface]['peer_count'] != post_dic[device][interface]['peer_count']:
                    print(
                        f"{device} -- DMVPN peer count changed. Peer count was {pre_dic[device][interface]['peer_count']}. Now it is {post_dic[device][interface]['peer_count']}")
                    logs.append(f"DMVPN peer count changed. Peer count was {pre_dic[device][interface]['peer_count']}. Now it is {post_dic[device][interface]['peer_count']}")
                    # Check NBMA Address for peer

                    print(f"pre --- {pre_dic[device][interface]['nbma_peers']}")
                    print(f"post --- {post_dic[device][interface]['nbma_peers']}")

                    # NBMA peer results could be string or list. Do a conversion to list to ensure consistent data type

                    pre_peer_list = []
                    post_peer_list = []

                    if isinstance(pre_dic[device][interface]['nbma_peers'], str):
                        pre_peer_list.append(pre_dic[device][interface]['nbma_peers'])
                    elif isinstance(pre_dic[device][interface]['nbma_peers'], list):
                        pre_peer_list = [str(x[0]) for x in pre_dic[device][interface]['nbma_peers']]

                    if isinstance(post_dic[device][interface]['nbma_peers'], str):
                        post_peer_list.append(post_dic[device][interface]['nbma_peers'])
                    elif isinstance(post_dic[device][interface]['nbma_peers'], list):
                        post_peer_list = [str(x[0]) for x in post_dic[device][interface]['nbma_peers']]

                    missing_peer = [x for x in pre_peer_list if x not in post_peer_list]

                    if missing_peer:
                        print(f"{device} -- The following peers are missing {missing_peer}")
                        logs.append(f"The following peers are missing {missing_peer}")

                    new_peer = [x for x in post_peer_list if x not in pre_peer_list]

                    if new_peer:
                        print(f"{device} -- The following peers have been added {new_peer}")
                        logs.append(f"The following peers have been added {new_peer}")

            results['DMVPN State Check'][device] = logs

    return results


def hsrp(job_a, job_b, devices):
    # Create Outer results dictionary
    results = {}
    results['HSRP State Check'] = {}

    # Database conneciton
    client = pymongo.MongoClient()

    # define database
    db = client['network_state']

    # check meta data to determine pre and post state jobs

    db_meta = db['MetaData']
    try:
        job_a_date = db_meta.find_one({"name": job_a})['date']
        job_b_date = db_meta.find_one({"name": job_b})['date']
    except Exception as e:
        sys.exit(f'{e} - Failure Querying MetaData Database for Jobs - {job_a} and {job_b}')

    if job_a_date < job_b_date:
        pre_job = job_a
        post_job = job_b
    elif job_a_date > job_b_date:
        pre_job = job_b
        post_job = job_a
    else:
        sys.exit("Something went wrong could not compare jobs dates")

    pre_job_collection = db[pre_job]
    post_job_collection = db[post_job]

    pre_job_bson = pre_job_collection.find_one({"name": "hsrp_state"})['data']
    pre_dic = bson.decode(pre_job_bson)

    post_job_bson = post_job_collection.find_one({"name": "hsrp_state"})['data']
    post_dic = bson.decode(post_job_bson)

    ###################
    # Start Diff testing
    ###################

    diff = Diff(pre_dic, post_dic)
    diff.findDiff()
    diff = str(diff)
    print(diff)

    if not diff:
        print(f'No HSRP changes detected - Test Passed')
    else:
        print(f'HSRP changes detected - Test Failed')

        for device in devices:

            logs = []

            missing_hsrp_int = [x for x in pre_dic[device].keys() if x not in post_dic[device].keys()]

            if missing_hsrp_int:
                for interface in missing_hsrp_int:
                    print(f"{device} -- Interface {interface} no longer has HSRP enabled ")
                    logs.append(f"Interface {interface} no longer has HSRP enabled")

            added_hsrp_int = [x for x in post_dic[device].keys() if x not in pre_dic[device].keys()]

            if added_hsrp_int:
                for interface in added_hsrp_int:
                    print(f"{device} -- HSRP enabled on new interface - {interface}")
                    logs.append(f"HSRP enabled on new interface - {interface}")

            common_hsrp_ints = [x for x in post_dic[device].keys() if x in pre_dic[device].keys()]

            for pre_int in common_hsrp_ints:
                for post_int in common_hsrp_ints:

                    if 'ipv4' in pre_dic[device][pre_int].keys() and 'ipv4' not in post_dic[device][
                        pre_int].keys():
                        print(f"{device} -- IPv4 no longer enabled on interface {pre_int}")
                        logs.append(f"IPv4 no longer enabled on interface {pre_int}")

                    if 'ipv6' in pre_dic[device][pre_int].keys() and 'ipv6' not in post_dic[device][
                        pre_int].keys():
                        print(f"{device} -- IPv6 no longer enabled on interface {pre_int}")
                        logs.append(f"IPv6 no longer enabled on interface {pre_int}")

                    if 'ipv4' in post_dic[device][pre_int].keys() and 'ipv4' not in pre_dic[device][
                        pre_int].keys():
                        print(f"{device} -- IPv4 now enabled on interface {pre_int}")
                        logs.append(f"IPv4 now enabled on interface {pre_int}")

                    if 'ipv6' in post_dic[device][pre_int].keys() and 'ipv6' not in pre_dic[device][
                        pre_int].keys():
                        print(f"{device} -- IPv6 now enabled on interface {pre_int}")
                        logs.append(f"IPv6 now enabled on interface {pre_int}")

                    # execute ipv4 flow
                    if 'ipv4' in post_dic[device][pre_int].keys() and 'ipv4' in pre_dic[device][
                        pre_int].keys():

                        missing_hsrp_group = [x for x in pre_dic[device][pre_int]['ipv4'].keys() if
                                              x not in post_dic[device][pre_int]['ipv4'].keys()]

                        # identify missing HSRP groups
                        if missing_hsrp_group:
                            for group in missing_hsrp_group:
                                print(f"{device} -- IPv4 HSRP group {group} has been removed")
                                logs.append(f"IPv4 HSRP group {group} has been removed")

                        # identify added HSRP groups
                        added_hsrp_group = [x for x in post_dic[device][pre_int]['ipv4'].keys() if
                                            x not in pre_dic[device][pre_int]['ipv4'].keys()]

                        if added_hsrp_group:
                            for group in missing_hsrp_group:
                                print(f"{device} -- IPv4 HSRP group {group} has been added")
                                logs.append(f"IPv4 HSRP group {group} has been added")

                        common_hsrp_groups = [x for x in post_dic[device][pre_int]['ipv4'].keys() if
                                              x in pre_dic[device][pre_int]['ipv4'].keys()]

                        for indi_group in common_hsrp_groups:
                            pre_priority = pre_dic[device][pre_int]['ipv4'][indi_group]['priority']
                            pre_vmac = pre_dic[device][pre_int]['ipv4'][indi_group]['v_mac']
                            pre_state = pre_dic[device][pre_int]['ipv4'][indi_group]['state']
                            pre_pri_router = pre_dic[device][pre_int]['ipv4'][indi_group]['active_router']
                            post_priority = post_dic[device][pre_int]['ipv4'][indi_group]['priority']
                            post_vmac = post_dic[device][pre_int]['ipv4'][indi_group]['v_mac']
                            post_state = post_dic[device][pre_int]['ipv4'][indi_group]['state']
                            post_pri_router = post_dic[device][pre_int]['ipv4'][indi_group]['active_router']

                            if pre_priority != post_priority:
                                print(
                                    f"{device} -- IPv4 HSRP group {indi_group} priority changed from {pre_priority} to {post_priority}")
                                logs.append(f"IPv4 HSRP group {indi_group} priority changed from {pre_priority} to {post_priority}")

                            if pre_vmac != post_vmac:
                                print(
                                    f"{device} -- IPv4 HSRP group {indi_group} virtual mac changed from {pre_vmac} to {post_vmac}")
                                logs.append(f"IPv4 HSRP group {indi_group} virtual mac changed from {pre_vmac} to {post_vmac}")

                            if pre_state != post_state:
                                print(
                                    f"{device} -- IPv4 HSRP group {indi_group} HSRP state changed from {pre_state} to {post_state}")
                                logs.append(f"IPv4 HSRP group {indi_group} HSRP state changed from {pre_state} to {post_state}")

                            if pre_pri_router != post_pri_router:
                                print(
                                    f"{device} -- IPv4 HSRP group {indi_group} primary router changed from {pre_pri_router} to {post_pri_router}")
                                logs.append(f"IPv4 HSRP group {indi_group} primary router changed from {pre_pri_router} to {post_pri_router}")

                    # execute ipv6 flow
                    if 'ipv6' in post_dic[device][pre_int].keys() and 'ipv6' in \
                            pre_dic[device][pre_int].keys():

                        missing_hsrp_group = [x for x in
                                              pre_dic[device][pre_int]['ipv6'].keys() if
                                              x not in post_dic[device][pre_int][
                                                  'ipv6'].keys()]

                        # identify missing HSRP groups
                        if missing_hsrp_group:
                            for group in missing_hsrp_group:
                                print(f"{device} -- IPv6 HSRP group {group} has been removed")
                                logs.append(f"IPv6 HSRP group {group} has been removed")

                        # identify added HSRP groups
                        added_hsrp_group = [x for x in post_dic[device][pre_int]['ipv6'].keys()
                                            if
                                            x not in pre_dic[device][pre_int]['ipv6'].keys()]

                        if added_hsrp_group:
                            for group in missing_hsrp_group:
                                print(f"{device} -- IPv6 HSRP group {group} has been added")
                                logs.append(f"IPv6 HSRP group {group} has been added")

                        common_hsrp_groups = [x for x in
                                              post_dic[device][pre_int]['ipv6'].keys() if
                                              x in pre_dic[device][pre_int]['ipv6'].keys()]

                        for indi_group in common_hsrp_groups:
                            pre_priority = pre_dic[device][pre_int]['ipv6'][indi_group][
                                'priority']
                            pre_vmac = pre_dic[device][pre_int]['ipv6'][indi_group]['v_mac']
                            pre_state = pre_dic[device][pre_int]['ipv6'][indi_group]['state']
                            pre_pri_router = pre_dic[device][pre_int]['ipv6'][indi_group][
                                'active_router']
                            post_priority = post_dic[device][pre_int]['ipv6'][indi_group][
                                'priority']
                            post_vmac = post_dic[device][pre_int]['ipv6'][indi_group]['v_mac']
                            post_state = post_dic[device][pre_int]['ipv6'][indi_group]['state']
                            post_pri_router = post_dic[device][pre_int]['ipv6'][indi_group][
                                'active_router']

                            if pre_priority != post_priority:
                                print(
                                    f"{device} -- IPv6 HSRP group {indi_group} priority changed from {pre_priority} to {post_priority}")
                                logs.append(f"IPv6 HSRP group {indi_group} priority changed from {pre_priority} to {post_priority}")

                            if pre_vmac != post_vmac:
                                print(
                                    f"{device} -- IPv6 HSRP group {indi_group} virtual mac changed from {pre_vmac} to {post_vmac}")
                                logs.append(f"IPv6 HSRP group {indi_group} virtual mac changed from {pre_vmac} to {post_vmac}")

                            if pre_state != post_state:
                                print(
                                    f"{device} -- IPv6 HSRP group {indi_group} HSRP state changed from {pre_state} to {post_state}")
                                logs.append(f"IPv6 HSRP group {indi_group} HSRP state changed from {pre_state} to {post_state}")

                            if pre_pri_router != post_pri_router:
                                print(
                                    f"{device} -- IPv6 HSRP group {indi_group} primary router changed from {pre_pri_router} to {post_pri_router}")
                                logs.append(f"IPv6 HSRP group {indi_group} primary router changed from {pre_pri_router} to {post_pri_router}")

            results['HSRP State Check'][device] = logs
            print(results)
    return results
