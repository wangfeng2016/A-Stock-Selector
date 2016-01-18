import argparse
import time
import os
import os.path

parser = argparse.ArgumentParser(
	formatter_class=argparse.RawDescriptionHelpFormatter,
	description=('''\
	The script is used to start !
	-----------------------------------------------
	The following parameters are MANDATORY: 

	1.
	2.
	3.
	-----------------------------------------------
	'''))

parser.add_argument('-d', '--debug', dest="debug", action='store_true', default=False, help="parameter to enter the debug mode")
parser.add_argument('-f', '--file', nargs='?', type=str, dest="xmlFile", required=True, help="xml file to be parsed")
#parser.add_argument('-bc', '--bench_conf', nargs='?', type=str, dest="bench_conf_file", required=True, help="ECU-Test bench configuration file name")
#parser.add_argument('-prj', '--project', nargs='?', type=str, dest="projectFile", required=True, help="ECU-Test test project file name")
#parser.add_argument('-ws', '--workspace', nargs='?', type=str, dest="workSpace", required=True, help="ECU-Test workspace")

args = parser.parse_args()
workspace =args.workSpace
#workspace = os.environ.get('WORKSPACE')
#build_tag = os.environ.get('BUILD_TAG')

if args.debug:
	print args
	print args.xmlFile
