```
$filter_interfaces:["any"];

@.entries().[$["value"][0][0]["firewall DoS-policy"]].({vdom: $["key"], 
policies: $["value"][0][0]["firewall DoS-policy"][0].values().[ "any" in $filter_interfaces or $["interface"] in $filter_interfaces].({
...$
})
})
```