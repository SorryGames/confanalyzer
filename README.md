# Configuration Analyzer

This project is designed as pip-package.
> Tested on **Python 3.8.5**

### Description

This tool is able to convert configuration of FortiGate to JSON format. The converted configuration is saved as `<name>.json` and is opened in browser.
For comfortable analyzing you should consider using a JSON viewer, which is available as an extension in browser.

> Very powerful and useful tool for JSON analyzing: [JSON Discovery](https://github.com/discoveryjs/browser-extension-json-discovery)

### How to run
1. Install as pip-package:
> `pip3 install git+http://git.solidex.minsk.by:3000/Solidex/confanalyzer.git`

2. Run to convert:
> `python3 -m confanalyzer fg.conf`

