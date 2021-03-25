from genie.testbed import load
import pymongo
import ospf
import netgen
import pymongo
from datetime import datetime
import random
import bson
import time
import json
import sys

# function to connect to devices and return network object dictionary
def connect_devices(topology, form_dev_list):
    try:
        device_list = {}
        # connect to devices
        testbed = load(topology)
        temp_devices = testbed.devices
        devices = {x:y for (x,y) in temp_devices.items() if x in form_dev_list}
        for name in devices.keys():
            device = devices[name]

            #attampt to connect to each device
            retries = 0
            while retries < 3:
                try:
                    if retries > 0:
                        print(f'this is retry attempt #{retries}')
                    device.connect(connection_timeout=5)
                    device_list[name] = device
                    break
                except Exception as e:

                    print(f'Thumbs down connecting to device. Error Msg...{e}')
                    if retries == 2:
                        # Create a log when we are unable to connect to a device
                        datetime_now = datetime.now()
                        print(f'{datetime_now} -- ERROR -- {e}')
                        f = open("/var/www/logs/errors.txt", "a")
                        f.write(f'\n{datetime_now} -- ERROR -- {e}')
                        f.close()
                        f = open("/var/www/templates/error_log.html", "a")
                        f.write(f'<br /><strong>{datetime_now}</strong> -- <span style="color:red">ERROR</span> -- {e}')
                        f.close()
                    time.sleep(5)
                    retries = retries + 1
    except Exception as e:
        # Get date and time
        datetime_now = datetime.now()
        print(f'{datetime_now} -- ERROR -- {e}')
        f = open("/var/www/logs/errors.txt", "a")
        f.write(f'\n{datetime_now} -- ERROR -- {e}')
        f.close()
        f = open("/var/www/templates/error_log.html", "a")
        f.write(f'<br /><strong>{datetime_now}</strong> -- <span style="color:red">ERROR</span> -- {e}')
        f.close()
        sys.exit("check error logs")

    return device_list


# Create a string based name list of devices
def create_device_name_list(devices):
    device_names = []
    for device_name in devices.keys():
        device_names.append(device_name)
    return device_names



################
#Main Code Block
################
def main(form_dev_list, job_id, topology, net_checks_list):
    checks = []

    #Connect to devices
    devices = connect_devices(topology, form_dev_list)


    #Get list of devices
    device_name_list_out = create_device_name_list(devices)

    if len(device_name_list_out) == 0:
        # Get date and time
        datetime_now = datetime.now()
        error_msg = "Collection failed. All Devices are unreachable. Check network connectivity"
        print(f'{datetime_now} -- ERROR -- {error_msg}')
        f = open("/var/www/logs/errors.txt", "a")
        f.write(f'\n{datetime_now} -- ERROR -- {error_msg}')
        f.close()
        f = open("/var/www/templates/error_log.html", "a")
        f.write(f'<br /><strong>{datetime_now}</strong> -- <span style="color:red">ERROR</span> -- {error_msg}')
        f.close()
        sys.exit("collection failed. Check network connectivity to devices")


    if "ospf_int_state" in net_checks_list:
        #get OSPF interface info
        ospf_int_state = ospf.ospf_interfaces_state(devices)
        print(ospf_int_state)
        checks.append('ospf_int_state')

    if "ospf_spf_state" in net_checks_list:
        #get OSPF SPF info
        ospf_spf_state = ospf.ospf_spf_state(devices)
        print(ospf_spf_state)
        checks.append('ospf_spf_state')

    if "ospf_neighbors_state" in net_checks_list:
        #get OSPF neighbors info
        ospf_neighbors_state = ospf.ospf_neighbors_state(devices)
        print(ospf_neighbors_state)
        b_ospf_neighbors_state = bson.encode(ospf_neighbors_state)
        checks.append('ospf_neighbors_state')

    if "route_state" in net_checks_list:
        #get route changes info. Need to encode in BSON format because keys have IP with "." and mongo doesn't like
        route_change_state = netgen.route_state(devices)
        print(route_change_state)
        b_route_change_state = bson.encode(route_change_state)
        checks.append('route_state')


    if "acl_state" in net_checks_list:
        #get ACL info. Need to encode in BSON format because keys have IP with "." and mongo doesn't like
        acl_state = netgen.acl_state(devices)
        print(acl_state)
        #Must ensure that all dictonary keys are strings. MongoDB requirement. Covert to JSON first as a workaround
        json_acl = json.dumps(acl_state)
        acl_state = json.loads(json_acl)
        b_acl_state = bson.encode(acl_state)
        checks.append('acl_state')

    if "frag_state" in net_checks_list:
        #get fagmentation info. Only applies to ios due to pyats parser support
        frag_state = netgen.fragmentation_state(devices)
        print(frag_state)
        checks.append('frag_state')

    if "interface_state" in net_checks_list:
        #get interface state info. Only applies to ios due to pyats parser support.
        #Need to encode in BSON format because keys have IP with "." and mongo doesn't like
        interface_state = netgen.interface_state(devices)
        print(interface_state)
        b_interface_state = bson.encode(interface_state)
        checks.append('interface_state')

    if "bgp_neighbors_state" in net_checks_list:
        #get BGP neighbors info
        bgp_neighbors_state = netgen.bgp_neighbors_state(devices)
        b_bgp_neighbors_state = bson.encode(bgp_neighbors_state)
        checks.append('bgp_neighbors_state')

    if "eigrp_neighbors_state" in net_checks_list:
        #get EIGRP neighbors info
        eigrp_neighbors_state = netgen.eigrp_neighbors_state(devices)
        b_eigrp_neighbors_state = bson.encode(eigrp_neighbors_state)
        checks.append('eigrp_neighbors_state')

    if "hsrp_state" in net_checks_list:
        # get HSRP info. Need to encode in BSON format because keys have IP with "." and mongo doesn't like
        hsrp_state = netgen.hsrp_state(devices)
        # Must ensure that all dictonary keys are strings. MongoDB requirement. Covert to JSON first as a workaround
        json_hsrp = json.dumps(hsrp_state)
        hsrp_state = json.loads(json_hsrp)
        b_hsrp_state = bson.encode(hsrp_state)
        checks.append('hsrp_state')

    if "dmvpn_state" in net_checks_list:
        #get DMVPN neighbors info
        dmvpn_state = netgen.dmvpn_state(devices)
        b_dmvpn_state = bson.encode(dmvpn_state)
        checks.append('dmvpn_state')


    #Get date and time
    datetime_now = datetime.now()

    #Assign Job owner
    owner = "system"


    ##########################
    #Enter records in Mongo DB
    ##########################

    #Database conneciton
    client = pymongo.MongoClient()

    #define database
    db = client['network_state']

    #define Job collection
    job = db[job_id]

    #define metadata colleciton
    db_meta = db['MetaData']

    #insert meta data document per job
    result = db_meta.insert_one({"name": job_id, "owner": owner, "checks": checks, "devices": device_name_list_out, "date": datetime_now})
    print(result.inserted_id)

    if "ospf_neighbors_state" in net_checks_list:
        #insert ospf neighbors document
        result = job.insert_one({"name": "ospf_neighbors_state", "data": b_ospf_neighbors_state})
        print(result.inserted_id)

    if "ospf_int_state" in net_checks_list:
        #insert ospf interface document
        result = job.insert_one({"name": "ospf_int_state", "data": ospf_int_state})
        print(result.inserted_id)

    if "ospf_spf_state" in net_checks_list:
        #insert ospf spf document
        result = job.insert_one({"name": "ospf_spf_state", "data": ospf_spf_state})
        print(result.inserted_id)

    if "frag_state" in net_checks_list:
        #insert fragmentation state
        result = job.insert_one({"name": "frag_state", "data": frag_state})
        print(result.inserted_id)

    if "route_state" in net_checks_list:
        #insert route change document
        result = job.insert_one({"name": "route_state", "data": b_route_change_state})
        print(result.inserted_id)

    if "acl_state" in net_checks_list:
        #insert acl state
        result = job.insert_one({"name": "acl_state", "data": b_acl_state})
        print(result.inserted_id)

    if "interface_state" in net_checks_list:
        #insert interface state
        result = job.insert_one({"name": "interface_state", "data": b_interface_state})
        print(result.inserted_id)

    if "bgp_neighbors_state" in net_checks_list:
        #insert bgp neighbors document
        result = job.insert_one({"name": "bgp_neighbors_state", "data": b_bgp_neighbors_state})
        print(result.inserted_id)

    if "eigrp_neighbors_state" in net_checks_list:
        #insert eigrp neighbors document
        result = job.insert_one({"name": "eigrp_neighbors_state", "data": b_eigrp_neighbors_state})
        print(result.inserted_id)

    if "hsrp_state" in net_checks_list:
        #insert hsrp document
        result = job.insert_one({"name": "hsrp_state", "data": b_hsrp_state})
        print(result.inserted_id)

    if "dmvpn_state" in net_checks_list:
        #insert dmvpn document
        result = job.insert_one({"name": "dmvpn_state", "data": b_dmvpn_state})
        print(result.inserted_id)


