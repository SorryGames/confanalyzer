# Configuration Analyzer

This project is designed as pip-package.
> Tested on **Python 3.8.5**

## Description

This tool is able to convert configuration of FortiGate to JSON format. The converted configuration is saved as temporary and is opened in browser.
For comfortable analyzing you should consider using a JSON viewer, which is available as an extension in browser.

> Very powerful and useful tool for JSON analyzing: [JSON Discovery](https://github.com/discoveryjs/browser-extension-json-discovery)

## How to run
1. Install as pip-package:
```
pip3 install git+http://git.solidex.minsk.by:3000/Solidex/confanalyzer.git
```

2. Run to convert:
```
python3 -m confanalyzer fg.conf
```

## Jora queries

Sounds sadly, but Jora (query language for **JSON Discovery**) is not documented well enough. So, I provided some use cases with Jora queries:

##### VDOM-disabled

1. Show webfilter profiles are in use: 
```
@.map('firewall policy')[0].values().map("webfilter-profle")
```

2. Show all interfaces:
```
@['system interface']
```

3. Show only `ip` of all interfaces:
```
@['system interface'][0].values().map("ip")
```

##### VDOM-enabled

1. Show antivirus profiles are in use: 
```
@.entries().({vdom: key, webfilter: [...value[0][0]['firewall policy'][0].values()].map("av-profile")})
```

2. Show all interfaces:
```
@["global"][0][0]["system interface"]
```

3. Show `interface`,`vdom`,`allowaccess` for all interfaces: 
```
global[0][0]["system interface"][0].entries().({interface: key, ...value.[allowaccess].({vdom, allowaccess})})
```
