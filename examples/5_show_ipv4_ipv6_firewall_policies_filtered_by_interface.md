```
$filter_interface: ["ssl.root", "srv1"];

@.entries().({vdom: $["key"], 
ipv4: $["value"][0][0]["firewall policy"][0].values().[ "any" in $filter_interface or $["dstintf"] in $filter_interface or $["srcintf"] in $filter_interface].({
"status": $["status"] ? "disable" : "enable",
...$  }),
ipv6: $["value"][0][0]["firewall policy6"][0].values().[ "any" in $filter_interface or $["dstintf"] in $filter_interface or $["srcintf"] in $filter_interface].({
"status": $["status"] ? "disable" : "enable",
...$  })
})
```