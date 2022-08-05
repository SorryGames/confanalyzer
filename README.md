# ForiOS Configuration Analyzer


## Introduction
The goals of the project are:
1. to convert FortiOS configuration to JSON file.
2. to check FortiOS configuration for well-known misconfigurations.


> It's supposed to use advanced JSON viewer for exploring converted configuration.
> 
> I'd like to advise you powerful JSON viewer that can be installed as browser extension: [JSON Discovery](https://github.com/discoveryjs/browser-extension-json-discovery)


## How to run
1. Install as Python package:
```
pip3 install git+https://github.com/mdraevich/fortios_config_analyzer
```

2. Execute to convert FortiOS configuration to JSON file (the converted file will be opened in default browser automatically):
```
python3 -m confanalyzer -f <path_to_fg_config>
```

3. Add option `-a` if you wanna check FortiOS configuration against well-known misconfigurations:
```
python3 -m confanalyzer -f <path_to_fg_config> -a
```

## JSON Discovery use cases

JSON Discovery extension uses Jora queries to extract useful information from JSON file.
Here is a list of useful Jora queries for FortiOS configuration analysis:


| #   | File        | Description |
| --- | ----------- | ----------- |
| 1   | [click](./examples/1_show_security_profiles_which_are_used_in_ipv4_firewall_policies.md)   | Show all security profiles which are used in IPv4 firewall policies (per-VDOM)  |
| 2   | [click](./examples/2_show_configuration_of_security_profiles.md)   | Show configuration for all security profiles (per-VDOM)    |
| 3   | [click](./examples/3_show_inspection_mode_for_ipv4_firewall_policies.md)   | Show inspection mode for all IPv4 firewall policies (per-VDOM)    |
| 4   | [click](./examples/4_show_ip_allowaccess_vdom_for_all_interfaces.md)   | Show `interface`,`vdom`, `ip/mask`, `allowaccess` attributes for all interfaces    |
| 5   | [click](./examples/5_show_ipv4_ipv6_firewall_policies_filtered_by_interface.md)   | Show IPv4 & IPv6 firewall policies filtered by interface (per-VDOM)    |
| 6   | [click](./examples/6_show_security_profiles_for_ipv4_firewall_policies.md)   | Show security profiles for every IPv4 firewall policy    |
| 7   | [click](./examples/7_show_ip_vlanid_interface_for_all_interfaces.md)   | Show `interface`, `vdom`, `ip/mask`, `master_interface`, `vlanid` attributes for all interfaces    |
| 8   | [click](./examples/8_show_routing_protocols_static_rip_ospf_bgp.md)   | Show configuration for routing protocols (static, RIP, OSPF, BGP) per-VDOM    |
| 9   | [click](./examples/9_show_profile_group_configuration_for_ipv4_ipv6_policies.md)   | Show profile group configuration and usage in IPv4 & IPv6 firewall policies    |
| 10  | [click](./examples/10_show_firewall_dos_policies_filtered_by_interface.md)   | Show firewall DoS-policies filtered by interface (per-VDOM)    |


