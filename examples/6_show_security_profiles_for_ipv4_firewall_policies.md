```
@.entries().({vdom: key, 
profiles: {...value[0][0]["firewall policy"][0].values().({
name: $["name"], 

sslssh_profile: $["ssl-ssh-profile"], 
protocol_options: $["profile-protocol-options"], 

webfilter: $["webfilter-profile"], 
dnsfilter: $["dnsfilter-profile"],
spamfilter: $["emailfilter-profile"] ? $["emailfilter-profile"] : $["spamfilter-profile"],

appcontrol: $["application-list"], 
antivirus: $["av-profile"], 
ips: $["ips-sensor"], 

filefilter: $["file-filter-profile"],	
voiceip: $["voip-profile"],
waf: $["waf-profile"],
profilegroup: $["profile-group"],
})}  
})
```