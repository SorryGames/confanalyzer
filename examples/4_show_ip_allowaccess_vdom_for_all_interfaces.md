```
@.values().[$[0]["system interface"]][0][0]["system interface"][0].entries().({int: key, ...value}).[$["allowaccess"]].({
interface: $["int"].split("___")[1], 
allowaccess: $["allowaccess"], 
ip_mask:$["ip"]})
```