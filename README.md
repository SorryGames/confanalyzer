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



##### Use cases


1. Show all security profiles configured in VDOM policies:
```
@.entries().[$["value"][0][0]["firewall policy"]].({vdom: $["key"], 
  webfilter: [...$["value"][0][0]["firewall policy"][0].values().[$["webfilter-profile"]].([$["webfilter-profile"]])],
  dnsfilter: [...$["value"][0][0]["firewall policy"][0].values().[$["dnsfilter-profile"]].([$["dnsfilter-profile"]])],
  antivirus: [...$["value"][0][0]["firewall policy"][0].values().[$["av-profile"]].([$["av-profile"]])],
  ips: [...$["value"][0][0]["firewall policy"][0].values().[$["ips-sensor"]].([$["ips-sensor"]])],
  spamfilter: [...$["value"][0][0]["firewall policy"][0].values().[$["emailfilter-profile"]].([$["emailfilter-profile"]]), 
  				...$["value"][0][0]["firewall policy"][0].values().[$["spamfilter-profile"]].([$["spamfilter-profile"]])],
  filefilter: [...$["value"][0][0]["firewall policy"][0].values().[$["file-filter-profile"]].([$["file-filter-profile"]])],
  appcontrol: [...$["value"][0][0]["firewall policy"][0].values().[$["application-list"]].([$["application-list"]])],
  voiceip: [...$["value"][0][0]["firewall policy"][0].values().[$["voip-profile"]].([$["voip-profile"]])],
  waf: [...$["value"][0][0]["firewall policy"][0].values().[$["waf-profile"]].([$["waf-profile"]])],
  profilegroup: [...$["value"][0][0]["firewall policy"][0].values().[$["profile-group"]].([$["profile-group"]])]
})
```


2. Show configuration for all security profiles in VDOM:
```
@.entries().[$["value"][0][0]["firewall policy"]].({vdom: $["key"], 
webfilter: $["value"][0][0]["webfilter profile"][0],
dnsfilter: $["value"][0][0]["dnsfilter profile"][0],
antivirus: $["value"][0][0]["antivirus profile"][0],
ips: $["value"][0][0]["ips sensor"][0],
spamfilter: {...$["value"][0][0]["spamfilter profile"][0], ...$["value"][0][0]["emailfilter profile"][0]},
appcontrol: $["value"][0][0]["application list"][0],
waf: $["value"][0][0]["waf profile"][0],
profilegroup: $["value"][0][0]["firewall profile-group"][0]
})
```

3. Show `interface`,`vdom`,`allowaccess` for all interfaces: 
```
global[0][0]["system interface"][0].entries().({int: key, ...value}).[$["allowaccess"]].({interface: $["int"], allowaccess: $["allowaccess"], ip:$["ip"]})
```

4. Show all policies filtered by "srcintf" == "port2":
```
@.entries().[$["value"][0][0]["firewall policy"]].({vdom: $["key"], 
policies: $["value"][0][0]["firewall policy"][0].values().[$["srcintf"] = "port2"].({
"srcintf": $["srcintf"], 
"dstintf": $["dstintf"], 
"service": $["service"], 
"action": $["action"], 
})
})
```

5. Show security profiles which are used in firewall policy:
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