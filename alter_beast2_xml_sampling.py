#!/usr/bin/python3

import sys
import xml.etree.ElementTree as ET
from xml.dom import minidom
import datetime


def prettify(elem):
    """Return a pretty-printed XML string for the Element.
    """
    rough_string = ET.tostring(elem, 'utf-8')
    reparsed = minidom.parseString(rough_string)
    return reparsed.toprettyxml(indent="  ")



if len(sys.argv) != 4:
	
	print("Incorrect paramters XML file passed to python script alter_beast2_xml_sampling.py")
	print("Please pass 3 paramters 1) input_xml, 2) age of oldest sequence and 3) output_xml")
	exit(1)



#User has passed an argument
xml_script=sys.argv[1]
oldest_sequence=sys.argv[2]
output_xml=sys.argv[3]
print(xml_script)
xml_tree=ET.parse(xml_script)

xml_root=xml_tree.getroot()
id_names=[]

#get a list of the ids of data elements

for data in xml_root.iter('data'):
	id_names.append(data.get("id"))


#for each data element insert the slicing function

for data_id in id_names:
	
	#Find the oldest sequence
	trait_id="dateTrait.t:"+str(data_id)
	for trait_element in xml_root.iter('trait'):
		if trait_element.get("id")==trait_id:
			trait_value=trait_element.get("value")
			
			#Value is a comma delimited string like:
			#MT894381=2016,MW380865=2019,JF510462=1975,KJ469653=1977,MH777395=2016,MH777398=2015,MN923205=2019,MH777397=2016,MH777396=2017,MN539540=2016,KR135164=2014,MN551586=2015,MT792736=2018
			
			#so split the string by comma
			sequence_date_pairs=trait_value.split(",")
			
			present_time=datetime.datetime.now()
			present_year=present_time.strftime("%Y")
			oldest_date=present_year
			youngest_sequence=0
			for sequence_date_pair in sequence_date_pairs:
				components=sequence_date_pair.split("=")
				sequence_year=components[1]
				if int(sequence_year) < int(oldest_date):
					oldest_date=sequence_year
				if int(sequence_year) > int(youngest_sequence):
					youngest_sequence=sequence_year
			if int(oldest_date)<(int(youngest_sequence)-int(oldest_sequence)):
				print("ERROR: There is an older sequence in the file than the time specified. "+str(int(youngest_sequence)-int(oldest_date))+" years ("+str(oldest_date)+") vs. "+str(oldest_sequence))
				print("Change the time to before the oldest sequence")
				exit(1)
			print("Oldest sequence found is from: "+str(oldest_date)+", "+str(int(youngest_sequence)-int(oldest_date))+" years before the youngest sequence.")
			
	#insert the slicing function on the sampling proportion
	
	function_element=ET.Element("function")
	
	#<function spec="beast.core.util.Slice" id="samplingProportionSlice" arg="@samplingProportion" index="1" count="1"/>"
	
	function_found=False
	function_id="samplingProportionSlice_"+str(data_id)
	
	#check to see if the function exists
	check_for_function=xml_root.find("function")
	for function_element in xml_root.iter('function'):
		if function_element.get("id")==function_id:
			function_found=True
	
	if not function_found:
		function_element.set("spec","beast.core.util.Slice")
		function_element.set("id","samplingProportionSlice_"+str(data_id))
		function_element.set("arg","@samplingProportion_BDSKY_Serial.t:"+str(data_id))
		function_element.set("index","1")
		function_element.set("count","1")
		xml_root.append(function_element)

	# Now insert the following elements within the <distribution id="BDSKY_Serial.t:data_id"
	#This is a child of xml > run > distribution id="posterior" > distribution id="prior"
	distribution_id="BDSKY_Serial.t:"+str(data_id)
	print("Looking for distrubtion elements with id: "+str(distribution_id))
	for distribution_element in xml_root.iter('distribution'):
		
		if distribution_element.get("id") == distribution_id:
			#<samplingRateChangeTimes spec="RealParameter" value="0 oldest_sequence.0000001"/>
			
			check_for_sampleRateChangeTimes=distribution_element.find("samplingRateChangeTimes")
			
			if check_for_sampleRateChangeTimes is not None:
				distribution_element.remove(check_for_sampleRateChangeTimes)
			
			samplingRateChangeTimes_element=ET.Element("samplingRateChangeTimes")
			samplingRateChangeTimes_element.set("spec","parameter.RealParameter")
			samplingRateChangeTimes_element.set("value","0.0 "+str(oldest_sequence)+".0000001")
			distribution_element.append(samplingRateChangeTimes_element)
			print("Inserting samplingRateChangeTimes element in element "+str(distribution_id))
			#<reverseTimeArrays spec="BooleanParameter" value="false false true false false false"/>
			reverseTimeArrays_element=ET.Element("reverseTimeArrays")
			reverseTimeArrays_element.set("spec","parameter.BooleanParameter")
			reverseTimeArrays_element.set("value","false false true false false false")
			distribution_element.append(reverseTimeArrays_element)
			print("Inserting reverseTimeArrays element in element "+str(distribution_id))
		
	#Change the samplingProportion parameter to include the first 0.0
		
	#<parameter id="samplingProportion_BDSKY_Serial.t:adenovirus_polymerase_muscle" 
	sampling_proportion_id="samplingProportion_BDSKY_Serial.t:"+str(data_id)
	for parameter_element in xml_root.iter('parameter'):
		if parameter_element.get("id") == sampling_proportion_id:
			current_sampling_proportion=parameter_element.text
			parameter_element.text="0.0 "+str(current_sampling_proportion)
			print("Changing parameter "+str(sampling_proportion_id)+" text from "+str(current_sampling_proportion)+" to: "+parameter_element.text)
	
	
	#Now change the samplingProportion prior to point to the function
	#<prior id="samplingProportionPrior" name="distribution" x="@samplingProportionSlice">
	sampling_prior_id="samplingProportionPrior_BDSKY_Serial.t:"+str(data_id)
	for prior_element in xml_root.iter('prior'):
		if prior_element.get("id") == sampling_prior_id:
			#found the sampling proportion prior
			prior_element.set("x","@samplingProportionSlice_"+str(data_id))
			
			#remove any x child tags
			for x_element in prior_element.iter('x'):
				prior_element.remove(x_element)

#For debugging
#print(prettify(xml_root))


#Write the xml file 
xml_tree.write(output_xml)

