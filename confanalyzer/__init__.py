import sys
from .conf_to_json import run_module


if len(sys.argv) == 1:
	print("No configuration file is attached...")
	exit()

run_module(sys.argv[1])
