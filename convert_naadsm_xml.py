#!/usr/bin/env python
import sys, getopt, io

def print_usage():
    s = """
    python convert_naadsm_xml.py -i <input_filename> -o <output_filename>
    
    converts a UTF-16 encoded NAADSM xml file in <input_filename>
    to a UTF-8 encoded file in <output_filename> .  
    If -o <output_filename> is not specified, output is written to a
    file named converted_xml.xml .
    python convert_naadsm_xml.py -h prints this usage statement ."""
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

with io.open(input_file,'r',encoding='utf16') as source_file:
    contents = source_file.read()

source_file.close()

with io.open(output_file,'w',encoding='utf8') as dest_file:
    dest_file.write(contents.replace('UTF-16','UTF-8'))

dest_file.close()

#
#with open(input_file, 'r') as source_file:
#  with open(output_file, 'w') as dest_file:
#    contents = source_file.read()
#    dest_file.write(contents.decode('utf-16').replace('UTF-16','UTF-8').encode('utf-8'))


    
