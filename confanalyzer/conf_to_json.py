#!/usr/bin/env python3

import uuid, shlex, os
import webbrowser
import tempfile
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
    ".*config system replacemsg.*"
]


def open_carefully(filename, mode="r"):
    try:
        return open(filename, mode)
    except: 
        return None


def _standard_form(content):
    # content = 'edit "solidex"'
    content = content.replace("'", "")
    content = content.replace('"', '')
    content = content.replace('\\', '')
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
                b_value = shlex.split(init_line)  
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


def _get_from_config(source, **kwargs):
    file = open_carefully(source, "r")
    #
    if file is None:
        return "No such file :("
    #
    answer = [ line.replace('\\', '') for line in file.readlines() ]  # remove "\" char from the configuration
    answer = _correct_vdom_sections(answer)
    answer = _update_vdom_sections(answer)
    #
    return _from_cli_to_object(answer)


def _proccess_request(action, **kwargs):
    if action == "get":
        return _get_from_config(**kwargs)


def run_module(src):
    #
    dst = tempfile.NamedTemporaryFile(delete=False)
    dst_path = dst.name + ".json"
    #
    #
    #
    json_file = open_carefully(dst_path, 'w')
    content = str(_proccess_request(action="get", source=src))  # object to string
    content = content.replace("'", '"')  # replace '' to ""
    json_file.write(content)  # write JSON to destination file
    json_file.close()
    #
    webbrowser.open(dst_path)  # open created file in default browser
    return 0


def main():
    #
    if len(sys.argv) == 1:
        print("No args with configuration file are attached...")
        exit()
    #
    run_module(sys.argv[1])


if __name__ == '__main__':
    main()