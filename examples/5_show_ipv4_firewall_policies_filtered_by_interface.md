```
@.entries().[$["value"][0][0]["firewall policy"]].({vdom: $["key"], 
policies: $["value"][0][0]["firewall policy"][0].values().[$["srcintf"] = "dst1"].({
"status": $["status"] ? "disable" : "enable",
...$
})
})
```