#!/bin/bash

# A POSIX variable
OPTIND=1         # Reset in case getopts has been used previously in the shell.


#Get current directory
current_dir=$(pwd)

function show_help {
	echo ""
	echo "alter_beast2_xml_sampling.sh -i <input xml> -o <output xml> -a <age of oldest node from youngest node>"
	echo ""
	echo "Applies sampling proportion to period between where sequence data exists and no sampling before oldest sequence"
	echo ""
}


if [ "$#" == 0 ]; then
	#No arguments were supplied
	show_help
	exit 0
fi

#oldest_sequence=$(date +'%Y')
oldest_sequence=0

# Find script path
script_path=$(dirname ${BASH_SOURCE[0]})


while [ "$1" ]; do 
	case "$1" in
		-h|--help) 
			show_help
			exit 0
		;;
		# input XML
		-i|--input)
			shift
			input_xml="$1"
			;;
		# output directory
		-o|--output)
			shift
			output_xml="$1"
			;;
		-a|--age)
			shift
			oldest_sequence="$1"
			;;
	esac
	shift
done

#the id for the partition will be in the xml file in line <data id="....."

# create the slice function
slice_function="<function spec="beast.core.util.Slice" id="samplingProportionSlice" arg="@samplingProportion" index="1" count="1"/>"

# Looks for python script in same path as this file:
python3 ${script_path}/alter_beast2_xml_sampling.py $input_xml $oldest_sequence $output_xml
