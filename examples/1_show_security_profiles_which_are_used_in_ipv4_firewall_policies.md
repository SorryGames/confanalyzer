```
@.entries().[$["value"][0][0]["firewall policy"]].({vdom: $["key"], 
  webfilter: [...$["value"][0][0]["firewall policy"][0].values().[$["webfilter-profile"]].([$["webfilter-profile"]])],
  dnsfilter: [...$["value"][0][0]["firewall policy"][0].values().[$["dnsfilter-profile"]].([$["dnsfilter-profile"]])],
  antivirus: [...$["value"][0][0]["firewall policy"][0].values().[$["av-profile"]].([$["av-profile"]])],
  ips: [...$["value"][0][0]["firewall policy"][0].values().[$["ips-sensor"]].([$["ips-sensor"]])],
  spamfilter: [...$["value"][0][0]["firewall policy"][0].values().[$["emailfilter-profile"]].([$["emailfilter-profile"]]), 
  				...$["value"][0][0]["firewall policy"][0].values().[$["spamfilter-profile"]].([$["spamfilter-profile"]])],
  filefilter: [...$["value"][0][0]["firewall policy"][0].values().[$["file-filter-profile"]].([$["file-filter-profile"]])],
  appcontrol: [...$["value"][0][0]["firewall policy"][0].values().[$["application-list"]].([$["application-list"]])],
  voiceip: [...$["value"][0][0]["firewall policy"][0].values().[$["voip-profile"]].([$["voip-profile"]])],
  waf: [...$["value"][0][0]["firewall policy"][0].values().[$["waf-profile"]].([$["waf-profile"]])],
  profilegroup: [...$["value"][0][0]["firewall policy"][0].values().[$["profile-group"]].([$["profile-group"]])]
})
```