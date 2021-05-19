#!/usr/bin/env python3

import uuid, shlex, yaml, os, copy
from jinja2 import Template  
import webbrowser
import sys


TAB_WIDTH = 4
CONFIG_CALLS = [
    'system interface',
    'system admin',
    'system console',
    'system global',
    'firewall address',
    'firewall policy',
    'router static',
    'router ospf',
    'router bgp',
    'dlp rule'
]
NEED_MULTIPLE_QUOTES = [
    'vdom',
    'srcintf',
    'dstintf',
    'srcaddr',
    'dstaddr'
]
NEED_QUOTES = [
    'alias',
    'device',
    'redistribute',
    'redistribute6',
    'associated-interface',
    'server',
    'edit',
    'name',
    'interface',
    'description',
    'accprofile',
    'comments',
    'comment',
    'password'
]
SET_GROUP = [
    "allowaccess",
    "srcintf",
    "dstintf",
    "srcaddr",
    "dstaddr",
    "service"
]


def _standard_form(content):
    # content = 'edit "solidex"'
    content = content.replace("'", "")
    content = content.replace('"', '')
    content = content.replace('\\', '')
    content = content.split()
    # content = [ "edit", "solidex" ]
    return content


def _from_object_to_cli(obj, spaces=0): 
    mode = None
    return_object = []
    for element in obj: 
        if isinstance(obj[element], list):
            if isinstance(obj[element][0], list):
                mode = "vdom"  # [[ {} ]]
            else:
                mode = "config"  # [ {} ]
        elif isinstance(obj[element], dict):
            mode = "edit"  # {}
        else:
            mode = "set"  # element: obj[element] 
        #
        if mode == "vdom":
            if element == "global":
                return_object += [
                    " " * spaces + "config {}".format(element),
                    *_from_object_to_cli(obj[element][0][0], spaces+TAB_WIDTH),
                    " " * spaces + "end"
                ]
            else:
                return_object += [
                    " " * spaces + "config vdom",
                    " " * spaces + "edit {}".format(element),
                    *_from_object_to_cli(obj[element][0][0], spaces+TAB_WIDTH),
                    " " * spaces + "end"
                ]
        #        
        if mode == "config":
            return_object += [
                " " * spaces + "config {}".format(element),
                *_from_object_to_cli(obj[element][0], spaces+TAB_WIDTH),
                " " * spaces + "end"
            ]
        if mode == "edit":
            return_object += [
                " " * spaces + 'edit "{}"'.format(element),
                *_from_object_to_cli(obj[element], spaces+TAB_WIDTH),
                " " * spaces + "next"
            ]
        if mode == "set":
            template = " " * spaces + "set {} {}"
            if element in NEED_QUOTES:
                template = " " * spaces + 'set {} "{}"' 
            if element in NEED_MULTIPLE_QUOTES:
                template = " " * spaces + 'set {}'.format(element)
                for option in obj[element].split():
                    template += (' "{}"'.format(option)).replace("#", " ")
            else:
                template = template.format(element, obj[element])
            return_object += [ template ]
    return return_object



def _from_cli_to_object(content):
    python_content = [ "{" ]
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
        if line[0] == "end":
            python_content += [ "}]," ]
        #
        if line[0] == "edit":
            python_content += [ "'{}': {{".format(" ".join(line[1:])) ]
        if line[0] == "next":
            python_content += [ "}," ]
        #
        if line[0] == "set":
            if init_line.count('"') == 1:
                init_line = init_line.strip() + '"'
            line = shlex.split(init_line)
            if line[1] in SET_GROUP:
                line[2:] = [ i.replace(" ", "#") for i in sorted(line[2:]) ]
            python_content += [ "'{}': '{}', ".format(line[1], " ".join(line[2:])) ]
    python_content += [ "}" ]
    python_content = " ".join(python_content)
    print("".join(content))
    print(python_content)
    print()
    return eval(python_content)


def _wrap_in_block(content, block_of, block_args):
    if block_args is None:
        return content
    #
    lines, references = [], []
    before, after = [], []
    block_map = {
        "config": "end",
        "edit": "next",
        "set": "set",
        "vdom": "close"
    }
    #
    before.append("{} {}\n".format(block_of, block_args))
    after.append("{}\n".format(block_map[block_of]))
    #
    lines += before
    references += [ -1 ] * len(before)
    #
    lines += content[0]
    references += content[1]
    #
    lines += after
    references += [ -1 ] * len(after)
    #
    return (lines, references)


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
        #
        #
        if line[0] in [ "config", "edit" ]:
            stack_b.append(line[0])
        if line[0] in [ "next", "end" ]:
            stack_b.pop()
        #
        content_b.append(curline)         
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



def _get_block(content, block_of, block_args):

    if block_args is None:
        return content
    #
    block_counter = 0
    global_counter = 0
    detected_replacemsg = False
    block_args = block_args.split()  # "system console" -> "[ "system", "console" ]"
    #
    if block_of == "vdom" and block_args == [ "global" ]:
        block_of = "config"
    #
    content_b = []
    block_reference = []
    block_map = {
        "config": "end",
        "edit": "next",
        "set": "set",
        "vdom": "end"
    }
    #
    block_end = block_map[block_of]
    #
    for index in range(len(content[0])):
        line = _standard_form(content[0][index])  # line = [ "config", "system", "console" ]
        #
        if line == []:
            continue
        #
        if line[0] in [ "config", "edit" ]:
            global_counter += 1
        if line[0] in [ "end", "next" ]:
            global_counter -= 1
        #
        # if line[:3] == [ "config", "system", "replacemsg" ]:
        #     detected_replacemsg = True
        # if line[0] == "end":
        #     detected_replacemsg = False
        # if detected_replacemsg:
        #     continue

        #
        if block_counter and line[0] == block_of:
            block_counter += 1
        #
        compose_line = [ block_of ] + block_args
        if line[:len(compose_line)] == compose_line:
            block_counter += 1
        if block_counter and block_of == "vdom" and line[0] == "config":
            block_counter += 1
        #
        if block_counter and global_counter == 1 and block_of == "set":
            content_b.append(content[0][index])
            block_reference.append(content[1][index])
        if block_counter and block_of in [ "config", "edit", "vdom" ]:
            content_b.append(content[0][index])
            block_reference.append(content[1][index])
        #
        if block_counter == 1 and block_of == "vdom":
            if global_counter == 1:  # edit root
                content_b[-1] = "vdom" + content_b[-1][4:]
            if global_counter == 0:  # end
                content_b[-1] = "close" + content_b[-1][3:]
        #
        if line[0] == block_end and block_counter: 
            block_counter -= 1
    #
    return (content_b, block_reference)


def open_carefully(filename, mode="r"):
    try:
        return open(filename, mode)
    except: 
        return None


def _get_from_config(source, **kwargs):
    file = open_carefully(source, "r")
    #
    if file is None:
        return "No such file :("
    #
    answer = [ line.replace('\\', '') for line in file.readlines() ]  # remove "\" char from the configuration
    answer = _correct_vdom_sections(answer)
    answer = _update_vdom_sections(answer)
    answer = (answer, list(range(len(answer))))

    #
    for block_type in [ "vdom", "config", "edit" ]:
        answer = _get_block(content=answer, block_of=block_type, block_args=kwargs.get(block_type))
    #
    if kwargs.get("leaves"):  # there are some leaves to filter
        lines, references = [], []
        for leaf in kwargs.get("leaves"):
            l, r = _get_block(content=answer, block_of="set", block_args=leaf)
            lines += l
            references += r 
        answer = (lines, references)
    #
    if answer[0]:
        if kwargs.get("leaves"):
            answer = _wrap_in_block(content=answer, block_of="edit", block_args=kwargs.get("edit"))
        if kwargs.get("edit"):
            answer = _wrap_in_block(content=answer, block_of="config", block_args=kwargs.get("config"))
        if kwargs.get("config") and kwargs.get("vdom"):
            answer = _wrap_in_block(content=answer, block_of="vdom", block_args=kwargs.get("vdom"))
    #
    return _from_cli_to_object(answer[0])


def _set_to_config_from_yaml(source, yaml_filename, **kwargs):
    yaml_file = open_carefully(yaml_filename, "r")
    #
    rendered_yaml = "\n".join([ Template(line).render(kwargs['jinja2']) for line in yaml_file.readlines() ])
    obj = yaml.load(rendered_yaml, Loader=yaml.FullLoader)
    return obj


def _set_to_config_by_args(source, **kwargs):
    in_file = open_carefully(source, mode="r")
    #
    vdom, config, edit, leaves = [ kwargs.get(block_of) for block_of in [ "vdom", "config", "edit", "leaves" ] ]
    if leaves:
        del kwargs["leaves"]
    #
    requested_object = {}
    modify_object = requested_object
    #
    if vdom:
        if modify_object.get(vdom) is None:
            modify_object[vdom] = [[{}]]
        modify_object = modify_object[vdom][0][0]  # dive into
    #
    if config:
        if modify_object.get(config) is None:
            modify_object[config] = [{}]
        modify_object = modify_object[config][0]  # dive into
    #
    if edit:
        if modify_object.get(edit) is None:
            modify_object[edit] = {}
        modify_object = modify_object[edit]  # dive into
    #
    if leaves:
        for leaf in leaves:
            modify_object[leaf] = leaves[leaf] 
    #
    return requested_object


def _merge_objects(from_obj, to_obj):
    if isinstance(from_obj, list):
        return [ _merge_objects(from_obj[0], to_obj[0]) ]
    if isinstance(from_obj, str):
        return from_obj
    #
    return_object = copy.deepcopy(to_obj)
    for element in from_obj:
        if to_obj.get(element) is None:
            return_object[element] = copy.deepcopy(from_obj[element])
        else:
            return_object[element] = _merge_objects(from_obj[element], to_obj[element])
    #
    return return_object


def _find_in_config(source, **kwargs):
    in_file = open_carefully(source, mode="r")
    #
    if in_file is None:
        return "No such file :("
    #
    source_config = in_file.readlines()
    answer = (source_config, list(range(len(source_config))))  # answer[0] is lines, answer[1] is reference numbers
    #
    for block_type in [ "vdom", "config", "edit" ]:
        answer = _get_block(content=answer, block_of=block_type, block_args=kwargs.get(block_type))
    #
    if kwargs.get('leaves') is not None:  # there are some leaves to filter
        lines, references = [], []
        for leaf in kwargs.get("leaves"):
            l, r = _get_block(content=answer, block_of="set", block_args=leaf)
            lines += l
            references += r 
        answer = (lines, references)
    #
    return answer


def _set_to_config(source, destination, yaml, **kwargs):
    requested_object = None
    #
    if destination is None:
        destination = "{}.conf".format(str(uuid.uuid4().hex))
    #
    if yaml:
        requested_object = _set_to_config_from_yaml(source, yaml, **kwargs)
    else:
        requested_object = _set_to_config_by_args(source, **kwargs)
    #
    if requested_object is None:
        return False
    #
    vdom_mode = False
    keys = list(requested_object.keys())
    if not keys:
        return False
    # 
    if isinstance(requested_object[keys[0]][0], list):
        vdom_mode = True
    #
    existing_object = {}
    if vdom_mode:
        for vdom in requested_object:
            for config in requested_object[vdom][0][0]:
                config_in_vdom = _get_from_config(source, vdom=vdom, config=config)
                if config_in_vdom:
                    if existing_object.get(vdom) is None:
                        existing_object[vdom] = [[{}]]
                    existing_object[vdom][0][0][config] = config_in_vdom[vdom][0][0][config]
    else:
        for config in requested_object:
            config_in = _get_from_config(source, config=config)
            if config_in:
                existing_object[config] = config_in[config]
    #
    existing_object = _merge_objects(requested_object, existing_object)
    #
    #
    in_file = open_carefully(source, mode="r")
    lines = in_file.readlines()
    in_file.close()
    #
    out_file = open_carefully(destination, mode="w")
    out_file.writelines(lines)
    out_file.close()
    source = destination
    #
    #
    #
    if vdom_mode:
        for vdom in existing_object:
            for config in existing_object[vdom][0][0]:
                ref = _find_in_config(destination, vdom=vdom, config=config)[1]
                #
                in_file = open_carefully(destination, mode="r")
                lines = in_file.readlines() 
                in_file.close()
                #
                if ref:
                    mn, mx = ref[0], ref[-1]
                    replace = [ el + "\n" for el in _from_object_to_cli(existing_object[vdom][0][0][config][0], spaces=4) ]
                    lines = lines[:mn+1] + replace + lines[mx:]
                else: 
                    mx = _find_in_config(destination, vdom=vdom)[1][-1]
                    wrapped_obj = { config: [ existing_object[vdom][0][0][config][0] ] }
                    replace = [ el + "\n" for el in _from_object_to_cli(wrapped_obj, spaces=0) ]
                    lines = lines[:mx] + replace + lines[mx:]
                #
                out_file = open_carefully(destination, mode="w")
                out_file.writelines(lines) 
                out_file.close()
    else:
        pass  # add instructions here
    #
    return requested_object


def _delete_from_config(source, destination, **kwargs):
    in_file = open_carefully(source, mode="r")
    if destination is None:
        destination = "{}.conf".format(str(uuid.uuid4().hex))
    #
    if in_file is None:
        return "No such file :("
    #
    source_config = in_file.readlines()
    in_file.close()
    #
    answer = _find_in_config(source, **kwargs)
    #
    # need check if object is not mentioned in other objects
    #
    out_file = open_carefully(destination, mode="w")
    ref_counter = 0
    for line in source_config:
        if ref_counter not in answer[1]:
            out_file.write(line)
        ref_counter += 1
    return destination



def _proccess_request(action, **kwargs):
    if action == "get":
        return _get_from_config(**kwargs)
    if action == "delete":
        return _delete_from_config(**kwargs)
    if action == "find":
        return _find_in_config(**kwargs)
    if action == "set":
        return _set_to_config(**kwargs)


def run_module(src):
    #
    if src.endswith('.conf'):
        dst = src[:-5] + ".json"  # test.conf -> test.json
    else:
        dst = src + ".json"
    #
    json_file = open_carefully(dst, 'w')
    content = str(_proccess_request(action="get", source=src))  # object to string
    content = content.replace("'", '"')  # replace '' to ""
    json_file.write(content)  # write JSON to destination file
    json_file.close()
    #
    webbrowser.open(dst)  # open created file in default browser
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