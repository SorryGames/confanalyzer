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