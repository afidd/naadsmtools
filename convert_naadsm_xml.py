#!/usr/bin/env python2.7
import sys, getopt

def print_usage():
    s = """python convert_naadsm_xml.py -i <input_filename> -o <output_filename> converts UTF-16 encoded NAADSM xml file in <input_filename> to UTF-8 encoded file in <output_filename>
    If -o <output_filename> is not specified, output is written to file named converted_xml.xml
    python convert_naadsm_xml.py -h prints this usage statement"""
    print(s)

options, arguments = getopt.getopt(sys.argv[1:], "i:o:h")
input_file = None
output_file = "converted_xml.xml"
for option, value in options:
    if option == "-i":
        input_file = value
    if option == "-o":
        output_file = value
    if option == "-h":
        print_usage()
        exit()

with open(input_file, 'r') as source_file:
  with open(output_file, 'w') as dest_file:
    contents = source_file.read()
    dest_file.write(contents.decode('utf-16').replace('UTF-16','UTF-8').encode('utf-8'))


    
