import pymongo
import netcompare



def compare(jobs):

    result = {'checks': {} }


    #Database conneciton
    client = pymongo.MongoClient()

    #define database
    db = client['network_state']

    #define metadata colleciton
    db_meta = db['MetaData']

    job_a, job_b = jobs

    #Get devices and check for first job
    query_a = {'name': job_a}
    dict_a = db_meta.find_one(query_a)
    devices_a = dict_a['devices']
    checks_a = dict_a['checks']


    # Get devices and check for second job
    query_b = {'name': job_b}
    dict_b = db_meta.find_one(query_b)
    devices_b = dict_b['devices']
    checks_b = dict_b['checks']

    final_devices = [x for x in devices_a if x in devices_b]
    final_checks = [x for x in checks_a if x in checks_b]

    #start checks

    if "ospf_neighbors_state" in final_checks:
        response = netcompare.ospf_neighbors(job_a, job_b, final_devices)
        result['checks'].update(response)

    if "ospf_int_state" in final_checks:
        response = netcompare.ospf_interfaces(job_a, job_b, final_devices)
        result['checks'].update(response)

    if "ospf_spf_state" in final_checks:
        response = netcompare.ospf_spf(job_a, job_b, final_devices)
        result['checks'].update(response)

    if "route_state" in final_checks:
        response = netcompare.routing_table(job_a, job_b, final_devices)
        result['checks'].update(response)

    if "acl_state" in final_checks:
        response = netcompare.acl_change(job_a, job_b, final_devices)
        result['checks'].update(response)

    if "frag_state" in final_checks:
        response = netcompare.fragmentation_check(job_a, job_b, final_devices)
        result['checks'].update(response)

    if "interface_state" in final_checks:
        response = netcompare.interface_check(job_a, job_b, final_devices)
        result['checks'].update(response)

    if "bgp_neighbors_state" in final_checks:
        response = netcompare.bgp_neighbors(job_a, job_b, final_devices)
        result['checks'].update(response)

    if "eigrp_neighbors_state" in final_checks:
        response = netcompare.eigrp_neighbors(job_a, job_b, final_devices)
        result['checks'].update(response)

    if "hsrp_state" in final_checks:
        response = netcompare.hsrp(job_a, job_b, final_devices)
        result['checks'].update(response)

    if "dmvpn_state" in final_checks:
        response = netcompare.dmvpn(job_a, job_b, final_devices)
        result['checks'].update(response)

    return result