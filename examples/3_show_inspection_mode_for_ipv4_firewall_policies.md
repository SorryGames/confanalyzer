```
@.entries().[$["value"][0][0]["firewall policy"]].({vdom: $["key"], 
policies: $["value"][0][0]["firewall policy"][0].entries().({
id: $["key"],
inspectionmode: $["value"]["inspection-mode"] ? "proxy" : "flow"})
})
```
