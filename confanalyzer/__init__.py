import os
import sys
import jinja2 
import yaml
import json
import argparse
import webbrowser
import tempfile

from .convert_configuration_to_object import convert_configuration_to_object
from .check_object_for_anomaly import check_object_for_anomaly


class MyDumper(yaml.Dumper):
    def increase_indent(self, flow=False, indentless=False):
        return super(MyDumper, self).increase_indent(flow, False)


def open_carefully(filename, mode="r"):
    try:
        return open(filename, mode)
    except: 
        return None


def init_parser():
    pr = argparse.ArgumentParser(
                        description="Use to convert FortiGate configuration "\
                        "to JSON object with anomaly detection. ")
    pr.add_argument("-f", "--file",
                        help="Specify a path to configuration file",
                        required=True,
                        type=str)
    pr.add_argument("-a", "--anomaly-report", 
                        help="Specify to report about anomalies.", 
                        action="store_true")
    return pr.parse_args()


def work(filepath, anomaly_check):
    #
    #
    # open the configuration file
    file = open_carefully(filepath, "r")
    filename = os.path.basename(filepath).split(".")[0]
    config_string = file.readlines()
    #
    #
    # 1) convert config_string to object
    # 2) look for anomalies in config_object
    config_object = convert_configuration_to_object(config_string=config_string)
    if anomaly_check:
        anomaly_report = check_object_for_anomaly(config_object=config_object)
    #
    # config_object => object of configuration 
    # anomaly_report => object of anomaly list
    #
    #
    #
    dst = tempfile.NamedTemporaryFile(delete=False, prefix=filename+"___")
    dst_path = "{}.json".format(dst.name)
    #
    json_file = open_carefully(dst_path, 'w')
    config_json = str(config_object).replace("'", '"')
    #
    json_file.write(config_json)
    json_file.close()
    #
    webbrowser.open(dst_path)  # open created file in default browser
    #
    if anomaly_check:
        webbrowser.open(_generate_anomaly_report(filename=filename+".conf", data=anomaly_report))  # open created file in default browser
    return 0

def _generate_anomaly_report(filename, data):
    #
    # read template
    print(os.path.join(os.path.dirname(__file__),"confanalyzer/template.html.jinja2"))
    with open(os.path.join(os.path.dirname(__file__),"template.html.jinja2")) as file_:
        template = jinja2.Template(file_.read())
    #
    #
    # anomalies = yaml.dump(data["anomalies"])
    formatted_data = []
    for test in data:
        formatted_data += [{
            "name": test["name"],
            "description": test["description"],
            "anomalies": [ yaml.dump(el, Dumper=MyDumper, default_flow_style=False) for el in test["anomalies"] ],
        }]
    # print(formatted_data)
    # exit()
    # print(template.render(report=data))
    #
    dst = tempfile.NamedTemporaryFile(delete=False)
    dst_path = "{}.html".format(dst.name)
    #
    report_file = open_carefully(dst_path, 'wb')
    output = template.render(
        filename=filename,
        data=formatted_data
    )
    report_file.write(output.encode("utf-8"))
    report_file.close()
    return dst_path 



# if __name__ == "__main__":
args = init_parser()
work(filepath=args.file, anomaly_check=args.anomaly_report)