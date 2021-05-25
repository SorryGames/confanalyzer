import sys
from .conf_to_json import main


if len(sys.argv) == 1:
	print("No configuration file is attached...")
	exit()

main()
