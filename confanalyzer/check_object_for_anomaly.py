import ipaddress
import json
from .make_query_to_configuration_object import get_ip_list_from_address_object_list




def check_object_for_anomaly(config_object):
    #
    report = []
    report.append(_services_and_security_profiles(config_object))
    report.append(_webfilter_to_local_resource(config_object))
    report.append(_unused_vip_objects(config_object))
    report.append(_check_admin_access_on_interfaces(config_object))
    report.append(_check_ha_configuration(config_object))
    report.append(_best_practices(config_object))
    #
    print(_check_admin_access_on_interfaces(config_object))
    # print(json.dumps(report, indent=4, sort_keys=True))
    return report







def _best_practices(config_object):
    report = {
        "name": "Anomaly Module #6: Рекомендации при настройке межсетевого экрана.",
        "description": 
"""список возможных рекомендаций по настройке межсетевого экрана.
""",
        "anomalies": []
    }


    #
    # check if backup on admin logout is enabled
    try:
        if "global" in config_object:
            backup_on_logout = config_object["global"][0][0]["system global"][0]["revision-backup-on-logout"]
        else: 
            backup_on_logout = config_object["root"][0][0]["system global"][0]["revision-backup-on-logout"]
        if backup_on_logout == "disable":
            raise 
    except:
        report["anomalies"].append({
            "problem": "Рекомендуется включить автоматический backup конфигурации при наличии изменений.",
            "solution": "[revision-backup-on-logout] => [enable]",
        })

    return report






















def _check_ha_configuration(config_object):
    report = {
        "name": "Anomaly Module #5: Проверка конфигурации в части High Availability (HA)",
        "description": 
"""Проверка нежелательной конфигурации HA.
Например: рекомендуется как минимум 2 heartbeat интерфейса между узлами кластера""",
        "anomalies": []
    }

    if "global" in config_object:
        ha_data = config_object["global"][0][0]["system ha"][0]
    else: 
        ha_data = config_object["root"][0][0]["system ha"][0]
    #
    #
    # if HA is not configured then bypass the test
    if ha_data.get("mode") is None or ha_data.get("mode") == "standalone":
        return report
    #
    # check amount of heartbeat interfaces 
    heartbeats = ha_data["hbdev"][::2]
    if len(heartbeats) <= 1:
        report["anomalies"].append({
                "heartbeats": "[{}]".format(", ".join(heartbeats)),
                "problem": "Рекомендуется как минимум 2 heartbeat интерфейса между узлами кластера."
        })

    # 
    # 
    configuration = False
    # 
    # check configuration of heartbeat interfaces
    for vdom, vdom_data in config_object.items():
        #
        if "system interface" not in vdom_data[0][0]:
            continue
        #
        for intf, intf_data in vdom_data[0][0]["system interface"][0].items():
            intf_name = "".join(intf.split("___")[1:])
            if intf_name in heartbeats:
                configuration = any([
                    configuration,
                    intf_data.get("allowaccess") is not None,
                    intf_data.get("ip") is not None
                ])
    if configuration:
        report["anomalies"].append({
                "heartbeats": "[{}]".format(", ".join(heartbeats)),
                "problem": "Не рекомендуется настраивать IP & Allowaccess для heartbeat интерфейсов."
        })


    return report














def _check_admin_access_on_interfaces(config_object):
    unsafe_protocols = [
        "telnet",
        "http"
    ]

    nonmgmt_protocol = [
        "ping"
    ]

    mgmt_protocol = [
        "https",
        "ssh",
        "snmp",
        "fabric",
        "fgfm", 
        "radius-acct"
    ]
    
    report = {
        "name": "Anomaly Module #4: Проверка аномалий при настройке административного доступа на интерфейсах",
        "description": 
"""Проверяем наличие аномалий административного доступа, позволяющие несанкционированный доступ к устройству.
Например: административный доступ по протоколу Telnet повышает вероятность утечки пароля в силу отсутствия шифрования""",
        "anomalies": []
    }
    
    for vdom, vdom_data in config_object.items():
        #
        if "system interface" not in vdom_data[0][0]:
            continue
        #
        #
        # Check unsafe admin access according to the <unsafe_protocols>
        for intf, intf_data in vdom_data[0][0]["system interface"][0].items():
            intf_name = "".join(intf.split("___")[1:])
            #
            if "allowaccess" not in intf_data:
                continue
            #
            configured_protocols = intf_data["allowaccess"] if isinstance(intf_data["allowaccess"], list) else [intf_data["allowaccess"]]
            #
            if "https" in configured_protocols and "http" in configured_protocols:
                configured_protocols.remove("http")
                configured_protocols.append("http (redirect)")
            #
            unsafe_mgmt = any([ proto in unsafe_protocols for proto in configured_protocols ])
            if unsafe_mgmt:
                report["anomalies"].append({
                        "vdom": vdom,
                        "interface": "{} [{}]".format(intf_name, intf_data["ip"][0]),
                        "protocols": configured_protocols,
                        "problem": "Обнаружены протоколы административного доступа без шифрования: [{}]".format(", ".join(unsafe_protocols)),
                })
        #
        #
        # Check protocols on public interfaces
        for intf, intf_data in vdom_data[0][0]["system interface"][0].items():
            intf_name = "".join(intf.split("___")[1:])
            #
            if "allowaccess" not in intf_data:
                continue
            if intf_data.get("ip") is None or ipaddress.IPv4Address("{}".format(intf_data["ip"][0])).is_private:
                continue
            #
            configured_protocols = intf_data["allowaccess"] if isinstance(intf_data["allowaccess"], list) else [intf_data["allowaccess"]]
            #
            mgmt_on_public_ip = any([ proto not in nonmgmt_protocol for proto in configured_protocols ])
            if mgmt_on_public_ip:
                report["anomalies"].append({
                        "vdom": vdom,
                        "interface": "{} [{}]".format(intf_name, intf_data["ip"][0]),
                        "protocols": configured_protocols,
                        "problem": "Обнаружен административный доступ на публичном интерфесе: [{}]".format(", ".join(nonmgmt_protocol)),
                })
        #
        #
        # Check how many interfaces are configured for MGMT access. 
        mgmt_interfaces = []
        for intf, intf_data in vdom_data[0][0]["system interface"][0].items():
            intf_name = "".join(intf.split("___")[1:])
            #
            if "allowaccess" not in intf_data:
                continue
            #
            configured_protocols = intf_data["allowaccess"] if isinstance(intf_data["allowaccess"], list) else [intf_data["allowaccess"]]
            #
            if any([ proto in mgmt_protocol for proto in configured_protocols ]):
                mgmt_interfaces += [ intf_name ]
        #
        # It's expected to have only single MGMT interface per FG unit
        if len(mgmt_interfaces) > 1:
            report["anomalies"].append({
                    "vdom": vdom,
                    "MGMT interfaces": "{}".format(", ".join(mgmt_interfaces)),
                    "MGMT protocols": ", ".join(mgmt_protocol),
                    "problem": "Обнаружено более одного MGMT интерфейса. Точно все верно?",
            })

    #
    #
    return report











def _unused_vip_objects(config_object):
    report = {
        "name": "Anomaly Module #3: Неиспользуемые объекты Virtual IP",
        "description": 
"""Неиспользуемые объекты Virtual IP необходимо удалять, поскольку маршрут к таким объектам все равно присутствует в таблице маршрутизации. 
""",
        "anomalies": []
    }

    #
    #
    #
    # if central nat is enabled we have to bypass this test
    try: 
        if config_object["root"][0][0]["system settings"][0]["central-nat"] == "enable":
            return report 
    except:
        pass
    try: 
        if config_object["global"][0][0]["system settings"][0]["central-nat"] == "enable":
            return report 
    except:
        pass
    # if central nat is enabled we have to bypass this test
    #
    #
    #
    #
    #

    for vdom, vdom_data in config_object.items():
        #
        if "firewall vip" not in vdom_data[0][0]:
            continue
        #
        vip_to_find_in_policy = []
        #
        for vip, vip_data in vdom_data[0][0]["firewall vip"][0].items():
            vip_name = "".join(vip.split("___")[1:])
            vip_to_find_in_policy += [vip_name]
        #
        #
        if "firewall vipgrp" in vdom_data[0][0]:
            #
            # excludes vip which are already in vip group
            members = []
            for vip_group, vip_group_data in vdom_data[0][0]["firewall vipgrp"][0].items():
                members += vip_group_data["member"]
            vip_to_find_in_policy = list(set(vip_to_find_in_policy) - set(members))
            #
            # include vip groups to <vip_to_find_in_policy>
            for vip_group, vip_group_data in vdom_data[0][0]["firewall vipgrp"][0].items():
                vip_to_find_in_policy += ["".join(vip_group.split("___")[1:])]
        #
        #
        #
        if "firewall policy" in vdom_data[0][0]:
            for policy, policy_data in vdom_data[0][0]["firewall policy"][0].items():
                #
                if "dstaddr" not in policy_data:
                    continue
                #
                #
                if isinstance(policy_data["dstaddr"], list):
                    dstaddr = policy_data["dstaddr"]
                else:
                    dstaddr = [policy_data["dstaddr"]]
                #
                #
                vip_to_find_in_policy = list(set(vip_to_find_in_policy) - set(dstaddr))
        #
        for vip in vip_to_find_in_policy:
            report["anomalies"].append({
                    "vdom": vdom,
                    "Virtual IP": vip
            })
    #
    #
    return report

























def _webfilter_to_local_resource(config_object):
    """
    This check is performed in order to understand
    if there are webfilter profile is applied to local webserver
    """

    report = {
        "name": "Anomaly Module #2: Веб-фильтрация, применяемая к локальному веб-серверу",
        "description": 
"""Не стоит применять веб-фильтрацию по категориям для запросов к локальному веб-серверу.
""",
        "anomalies": []
    }

    for vdom, vdom_data in config_object.items():
        #
        if "firewall policy" not in vdom_data[0][0]:
            continue
        #
        for policy, policy_data in vdom_data[0][0]["firewall policy"][0].items():
            profile = "webfilter-profile"
            if profile in policy_data:
                #
                if "dstaddr" not in policy_data:
                    continue
                #
                #
                if isinstance(policy_data["dstaddr"], list):
                    dstaddr = policy_data["dstaddr"]
                else:
                    dstaddr = [policy_data["dstaddr"]]
                #
                if "all" in dstaddr: 
                    continue
                #
                dstaddr = get_ip_list_from_address_object_list(vdom_data[0][0], dstaddr)
                webfilter_to_private = any([ ipnet[0].is_private or ipnet[-1].is_private for ipnet in dstaddr ])
                
                if webfilter_to_private:
                    report["anomalies"].append({
                            "vdom": vdom,
                            "policy_id": "".join(policy.split("___")[1:]),
                            "policy_name": policy_data.get("name") or policy_data.get("comments") or "None",
                            "profile": policy_data[profile],
                            "dstaddr": policy_data["dstaddr"],
                    })
    #
    return report














def _services_and_security_profiles(config_object):
    """
    This check is performed in order to understand
    if security profiles are compatible with configured services
    DNS + AntiVirus <-- Antivirus inspect files, not DNS requests
    """

    mail = ["SMTP", "SMTPS", "POP3", "POP3S", "IMAP", "IMAPS"]
    web = ["HTTPS", "HTTP"]
    files = ["SAMBA", "SMB", "FTP", "FTP_GET", "FTP_PUT", "NFS", "TFTP", "AFS3"]
    connectivity = ["PING", "ICMP", "ALL_ICMP", "ICMP_ANY"]
    voiceip = ["H323", "IRC", "SCCP", "SIP", "SIP-MSNmessenger", "MS-SQL", "MYSQL", "RTSP"]
    dns = ["DNS"]
    ntp = ["NTP"]
    remoteaccess = ["RDP", "VNC", "DCE-RPC", "PC-Anywhere", "ONC-RPC", "SSH", "TELNET", "X-WINDOWS", "WINS"]
    allprotocols = ["ALL", "ANY"]

    profile_is_allowed_for = {
        "webfilter-profile": web + allprotocols,
        "dnsfilter-profile": dns + allprotocols,
        
        "emailfilter-profile": mail + allprotocols,
        "spamfilter-profile": mail + allprotocols,

        "ips-sensor": [],                                    # empty list is allowed all
        "av-profile": files + web + mail + allprotocols,
        "file-filter-profile": files + web + mail + allprotocols,
        
        "application-list": [],                              # empty list is allowed all

        "voip-profile": voiceip + allprotocols,
    }
    report = {
        "name": "Anomaly Module #1: Проверка совместимости сервиса фильтрации и протокола",
        "description": 
"""Сервис фильтрации и протокол передачи данных должны быть совместимы.
Например: не стоит применять антивирусную защиту к DNS трафику, поскольку DNS трафик не передает файлы.""",
        "anomalies": []
    }

    for vdom, vdom_data in config_object.items():
        #
        if "firewall policy" not in vdom_data[0][0]:
            continue
        #
        for policy, policy_data in vdom_data[0][0]["firewall policy"][0].items():
            #
            if "service" not in policy_data:
                continue
            #
            # is profile enabled in policy? 
            configured_services = policy_data["service"] if isinstance(policy_data["service"], list) else [ policy_data["service"] ]
            excess_profiles = []
            #
            #
            for profile, compatible_services in profile_is_allowed_for.items():

                if profile in policy_data and len(compatible_services) > 0:
                    common = list(set(compatible_services).intersection(configured_services))
                    if len(common) > 0:
                        continue
                    #
                    excess_profiles += [profile]

            #
            #
            if len(excess_profiles):
                report["anomalies"].append({
                        "vdom": vdom,
                        "policy_id": "".join(policy.split("___")[1:]),
                        "policy_name": policy_data.get("name") or policy_data.get("comments") or "None",
                        "profile": excess_profiles,
                        "services": configured_services
                })
    #
    return report