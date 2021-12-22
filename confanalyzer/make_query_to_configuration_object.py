import ipaddress



def get_ip_list_from_address_object_list(config_object, address_object_list):
    iplist = []
    #
    for name in address_object_list:
        iplist += get_ip_list_from_address_object(config_object, name)
    return iplist


def get_ip_list_from_address_object(config_object, address_object_id):
    obj_dict = config_object["firewall address"][0]
    #
    iplist = []
    for obj, obj_data in obj_dict.items():
        if address_object_id in obj:
            subnet = obj_data.get("subnet")
            startip = obj_data.get("start-ip")
            endip = obj_data.get("end-ip")
            
            if startip is not None:
                startip = ipaddress.IPv4Address(startip)
                endip = ipaddress.IPv4Address(endip)
                #
                iplist = list(ipaddress.summarize_address_range(startip, endip))
            elif subnet is not None: 
                iplist = [ipaddress.ip_network('{}/{}'.format(subnet[0], subnet[1]))]
            else:
                iplist = [ipaddress.ip_network("0.0.0.0/0")]
            break
    #
    return iplist