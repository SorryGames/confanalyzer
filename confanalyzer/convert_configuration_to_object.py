#!/usr/bin/env python3

import uuid, shlex, os
import sys
import re


SET_GROUP = [
    "allowaccess",
    "srcintf",
    "dstintf",
    "srcaddr",
    "dstaddr",
    "service"
]

IGNORE_BLOCKS = [
    ".*config system replacemsg.*",
    ".*application name.*",
    ".*ips decoder.*",
    ".*ips rule.*"
]


def _pre_standard_form(content): 
    content = content.replace("'", "")
    content = content.replace('"', '')
    content = content.replace('\\', '')
    return content


def _standard_form(content):
    # content = 'edit "solidex"'
    content = _pre_standard_form(content)
    content = content.split()
    # content = [ "edit", "solidex" ]
    return content


def _from_cli_to_object(content):
    python_content = [ "{" ]
    b_stack = []  # [ [CONFIG, x], [CONFIG, y] ], where x,y -- counter for EDIT blocks within CONFIG
    # 
    for init_line in content:
        line = _standard_form(init_line)
        if line == []:
            continue
        #
        if line[0] == "vdom":
            python_content += [ "'{}': [[{{".format(" ".join(line[1:])) ]
        if line[0] == "close":
            python_content += [ "}]]," ]
        #
        if line[0] == "config":
            python_content += [ "'{}': [{{".format(" ".join(line[1:])) ]
            b_stack.append([line[0], 0])
        if line[0] == "end":
            python_content += [ "}]," ]
            b_stack.pop()
        #
        if line[0] == "edit":
            python_content += [ "'[{}]___{}': {{".format(b_stack[-1][-1], " ".join(line[1:])) ]
            b_stack[-1][-1] += 1
        if line[0] == "next":
            python_content += [ "}," ]
        #
        if line[0] == "set":
            #
            try:
                b_value = [ _pre_standard_form(part) for part in shlex.split(init_line) ]
                # >>> a = "set srcaddr localaddr remoteaddr 'another addr'"
                # >>> shlex.split(a)
                # [ 'set', 'srcaddr', 'localaddr', 'remoteaddr', 'another addr' ]
                # 'srcaddr': [ 'localaddr', 'remoteaddr', 'another addr' ]
                #
            except: 
                b_value = [ line[0], line[1], "cannot parse this" ]

            if len(b_value) == 3:
                python_content += [ "'{}': '{}', ".format(b_value[1], b_value[2]) ]
            else:
                python_content += [ "'{}': {}, ".format(b_value[1], b_value[2:]) ]
    python_content += [ "}" ]
    python_content = " ".join(python_content)
    return eval(python_content)


def _update_vdom_sections(content):
    pass
    #
    # is using to update vdom bounds
    # FOR EXAMPLE:
    # 
    # config vdom  <====| 
    # edit root   <=====| vdom root
    # next      <=======|      
    # end       <=======| close
    #
    stack_b = []
    content_b = []
    #
    for curline in content:
        line = _standard_form(curline)  # line = [ "config", "system", "console" ]
        #
        if line == []:
            continue
        #
        #
        # config system replacemsg ... <=== ignore block
        # end
        ignore_status = [ bool(re.search(ignoreit, curline)) for ignoreit in IGNORE_BLOCKS ]
        
        if True in ignore_status:
            print("IGNORED: {}".format(curline.strip()))
            stack_b.append("ignore")
            continue
        #
        #
        # config global
        # end
        if line == [ "config", "global" ]:
            stack_b.append("config_global")
            content_b.append("vdom {}\n".format(line[1]))
            continue
        if line == [ "end" ] and stack_b[-1] == "config_global":
            content_b.append("close\n")
            stack_b.pop()
            continue
        #
        #
        # config vdom
        # end
        if line == [ "config", "vdom" ]:
            stack_b.append("config_vdom")
            continue
        if line == [ "end" ] and stack_b[-1] == "config_vdom":
            stack_b.pop()
            continue
        #
        #
        # edit name_of_vdom
        # next
        if line[0] == "edit" and stack_b[-1] == "config_vdom":      # the first EDIT after CONFIGVDOM
            stack_b.append("edit_vdom")                       # stack_b: [CONFIGVDOM, EDITVDOM]
            content_b.append("vdom {}\n".format(line[1]))    # line = [ "edit", "root" ] ==> "vdom root\n"
            continue
        if line == [ "next" ] and stack_b[-1] == "edit_vdom":
            content_b.append("close\n")
            stack_b.pop()
            continue
        #
        #
        if "ignore" not in stack_b:
            content_b.append(curline)       
        #
        #
        if line[0] in [ "config", "edit" ]:
            stack_b.append(line[0])
        if line[0] in [ "next", "end" ]:
            stack_b.pop()
        #
    #
    return content_b


def _correct_vdom_sections(content):
    #
    # is using to recreate configuration, where END section could close EDIT sections
    # FOR EXAMPLE:
    # 
    # config vdom
    # edit root
    # ---                <=== This function will insert in this empty space NEXT section
    # end
    #
    stack_b = []
    content_b = []
    #
    for curline in content:
        line = _standard_form(curline)  # line = [ "config", "system", "console" ]
        #
        if line == []:
            continue
        #
        if line[0] in [ "config", "edit" ]:
            stack_b.append(line[0])            # insert to block stack: [CONFIG, EDIT] <== CONFIG
        #
        if line[0] == "next":
            deleted = stack_b.pop() 
            if deleted != "edit":          # if the current section is EDIT
                print("ERROR: CONFIG section is going to be closed by NEXT section; line[{}]".format(index+1))
                exit(0)
        #
        if line[0] == "end":                       # if the current section is CONFIG
            while stack_b.pop() != "config":   # END section should be closing all blocks until the first CONFIG is encountered 
                content_b.append("next\n")     # if EDIT section is closed by END section, then NEXT is missing
        #
        #
        content_b.append(curline)         
    #
    return content_b


def _normalize_object(config_object):
    normalized_config_object = []
    if "root" in config_object:
        normalized_config_object = config_object
    else: 
        normalized_config_object = {"root": [[ config_object ]]}
    #
    return normalized_config_object


# argument: string (configuration data)
# return: object
def convert_configuration_to_object(config_string):
    #
    config_object = config_string
    #
    try:
        config_object = [ line.replace('\\', '') for line in config_string ]  # remove "\" char from the configuration
        config_object = _correct_vdom_sections(config_object)
        config_object = _update_vdom_sections(config_object)
        config_object = _from_cli_to_object(config_object)
        config_object = _normalize_object(config_object)
    except: 
        config_object = ["Converting is failed..."]
    #
    return config_object



if __name__ == '__main__':
    pass