```
@.values().[$[0]["system interface"]][0][0]["system interface"][0].entries().({int: key, ...value}).[$["allowaccess"]].({
interface: $["int"].split("___")[1], 
vdom: $["vdom"],
ip_mask: $["ip"],

vlanid: $["vlanid"],
master_interface: $["interface"],
})
```