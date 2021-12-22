# Configuration Analyzer

This project is designed as pip-package.
> Tested on **Python 3.8.5**

## Description

This tool is able to convert configuration of FortiGate to JSON format. The converted configuration is saved as temporary and is opened in browser.
For comfortable analyzing you should consider using a JSON viewer, which is available as an extension in browser.

> Very powerful and useful tool for JSON analyzing: [JSON Discovery](https://github.com/discoveryjs/browser-extension-json-discovery)

## How to run
1. Install as pip-package:
```
pip3 install git+http://git.solidex.minsk.by:3000/Solidex/confanalyzer.git
```

2. Run to convert:
```
python3 -m confanalyzer <fortigate.conf>
```

## Jora queries

Sounds sadly, but Jora (query language for **JSON Discovery**) is not documented well enough. So, I provided some use cases with Jora queries:

##### VDOM-disabled

1. Show `action` and `service` of firewall policy: 
```
@['firewall policy'][0].values().({name: $["name"], action: $["action"], services: $["service"]})
```

2. Show all interfaces:
```
@['system interface']
```

3. Show `ip` for interfaces, which have `ip` field:
```
@['system interface'][0].entries().({int: $["key"], ...value}).[$["ip"]].({interface: $["int"], ip: $["ip"]})
```

##### VDOM-enabled


1. Show all interfaces:
```
global[0][0]["system interface"]
```

2. Show `interface`,`vdom`,`allowaccess` for all interfaces: 
```
global[0][0]["system interface"][0].entries().({int: key, ...value}).[$["allowaccess"]].({interface: $["int"], allowaccess: $["allowaccess"], ip:$["ip"]})
```

3. Show security profile configuration for all VDOMs:
```
@.entries().({vdom: key, ...value[0][0]}).({vdom: vdom, sslssh_profile: $["firewall ssl-ssh-profile"], protocol_options: $["firewall profile-protocol-options"], webfilter: $["webfilter profile"], av: $["antivirus profile"], ips: $["ips sensor"], dnsfilter: $["dnsfilter profile"], dlp: $["dlp sensor"], appcontrol: $["application list"]})
```

4. Show security profiles which are used in firewall policy:
```
@.entries().({vdom: key, profiles: {...value[0][0]["firewall policy"][0].values().({name: $["name"], sslssh_profile: $["ssl-ssh-profile"], protocol_options: $["profile-protocol-options"], av: $["av-profile"], webfilter: $["webfilter-profile"], ips: $["ips-sensor"], appcontrol: $["application-list"], spamfilter: $["emailfilter-profile"]}) }  })
```

5. Show routing protocols for all VDOMs:
```
@.entries().({vdom: key, static: {...value[0][0]["router static"][0] }, rip: {...value[0][0]["router rip"][0] }, ospf: {...value[0][0]["router ospf"][0] }, bgp: {...value[0][0]["router bgp"][0] }  })
```

6. Show security profile groups are used in **IPv4** and **IPv6** policies as well as profile groups themselves: 
```
@.entries().({vdom: key, profiles_ipv4: {...value[0][0]["firewall policy"][0].values().({group: $["profile-group"], name: $["name"]}) }, profiles_ipv6: {...value[0][0]["firewall policy6"][0].values().({group: $["profile-group"], name: $["name"]}) }, profilegroup: {...value[0][0]["firewall profile-group"][0]}  })
```

7. Show **IPv4, IPv6, Proxy, DOS** policies for all VDOMs:
``` 
@.entries().({vdom: key, ...value[0][0]}).({vdom: $["vdom"], ipv4: $["firewall policy"], ipv6: $["firewall policy6"], dos: $["firewall DoS-policy"], proxy: $["firewall proxy-policy"]})
```

8. Show static URL filter configuration for all VDOMs:
```
@.entries().({vdom: key, ...value[0][0]}).({vdom: $["vdom"], ipv4: $["webfilter urlfilter"]})
```