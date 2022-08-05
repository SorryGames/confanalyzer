```
@.entries().({
vdom: key, 
profiles_ipv4: {...value[0][0]["firewall policy"][0].values().({group: $["profile-group"], name: $["name"]}) }, 
profiles_ipv6: {...value[0][0]["firewall policy6"][0].values().({group: $["profile-group"], name: $["name"]}) }, 
profilegroup: {...value[0][0]["firewall profile-group"][0]}  
})
```