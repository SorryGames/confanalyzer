# Configuration Analyzer


### Introduction 
This project is designed as pip-package.
> Tested on **Python 3.8.5**

### Description

This tool is able to convert configuration of FortiGate to JSON format to simplify analyzing of configuration. 

The converted configuration is saved as temporary JSON file and opened in a browser.
To analyze JSON file through the browser you have to install a JSON viewer which is available as an browser extension.

> I'd recommend you very powerful web browser tool for JSON analyzing [JSON Discovery](https://github.com/discoveryjs/browser-extension-json-discovery)

## How to run
1. Install as pip-package:
```
pip3 install git+<repository url>
```

2. Run to convert:
```
python3 -m confanalyzer -f <path_to_fg_config>
```

3. Run to convert & look for anomalies:
```
python3 -m confanalyzer -f <path_to_fg_config> -a
```

### Jora queries

To extract useful reports about configuration file you can use Jora queries (comes in a bundle with [JSON Discovery](https://github.com/discoveryjs/browser-extension-json-discovery))


##### Useful queries

| # | Example      | Description |
| ------- | ----------- | ----------- |
| 1   | [more](./examples/1_show_security_profiles_which_are_used_in_ipv4_firewall_policies.md)      | Show all security profiles which are used in IPv4 firewall policies (per-VDOM)  |
| 2   | [more](./examples/2_show_configuration_of_security_profiles.md)   | Show configuration for all security profiles (per-VDOM)    |
| 3   | [more](./examples/3_show_inspection_mode_for_ipv4_firewall_policies.md)   | Show inspection mode for all IPv4 firewall policies (per-VDOM)    |
| 4   | [more](./examples/4_show_ip_allowaccess_vdom.md)   | Show `interface`,`vdom`,`allowaccess` attributes for all interfaces    |
| 5   | [more](./examples/5_show_ipv4_firewall_policies_filtered_by_interface.md)   | Show IPv4 firewall policies filtered by interface name    |
| 6   | [more](./examples/6_show_security_profiles_for_ipv4_firewall_policies.md)   | Show security profiles for every IPv4 firewall policy    |



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