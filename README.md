## Estimating age to most recent common ancestor: Setting a period with a sampling proportion of Zero

Typically when estimating the node age of divergence of virus sequences, there is a period for which no sequence data is available. This is the period before the oldest sequence available. For this region, the correct sampling proportion is 0. To set this, some changes need to be made to the BEAST XML file. 

These changes, detailed at https://github.com/laduplessis/skylinetools/wiki/TreeSlicer%3A-Example-1 can be applied using the script alter_beast2_xml_sampling.sh with the arguments -i <input_xml_file> -a <age_of oldest sequence> -o <output_xml>. This script calls a python script to make the changes detailed below to the xml file.

Within the 
`<distribution id="BDSKY_Serial.t:adenovirus_polymerase_muscle"… tag, the following tags are added to reverse the time array on the samplingProportion prior.
<samplingRateChangeTimes spec="parameter.RealParameter" value="0.0 <oldest sequence age>.0000001" />
<reverseTimeArrays spec="parameter.BooleanParameter" value="false false true false false false" />`

The samplingProportion is the 3rd array for the reverseTimeArrays value.

Then the two values are set within the sampling proportion prior. The first sets that no sampling (0) has occurred within the first period (root to just before oldest sequence) and the sampling proportion established in beauti is maintained for the last region of the tree, in the example below this is 0.01.

`<parameter id="samplingProportion" name="stateNode" lower="0.0" upper="1.0">0 0.01</parameter>`

Finally, because 0 maybe undefined in many distributions, sampling across the region where the proportion is 0 may cause problems. To fix this, tell beast to sample only one point in this region by creating a slice of the distribution with a function and sampling this slice only. The script will insert a function into the xml file within the <beast> element. The function will be named `samplingProportionSlice_<data_id>` and one will be created for each alignment. In the example below this function was created for the alignment of the polymerase of adenovirus sequences aligned by Muscle.

`<function spec="beast.core.util.Slice" id="samplingProportionSlice_adenovirus_polymerase_muscle" arg="@samplingProportion_BDSKY_Serial.t:adenovirus_polymerase_muscle" index="1" count="1" />`

Then call this function when sampling the samplingProportion distribution. This is done by altering the prior tag within the `<distribution id=”prior”…` tag of the Beast2 XML document, and setting x to point to the slicing function.

`<prior id="samplingProportionPrior_BDSKY_Serial.t:adenovirus_polymerase_muscle" name="distribution" x="@samplingProportionSlice_adenovirus_polymerase_muscle">`

This script will set this for all the alignments within a Beast2 XML file, although it is not yet tested on files containing several alignments.

Note: if you reload this xml file in Beauti, some of these changes will be altered. Particularly the samplingProportion prior and the function are merged:


`<distribution id="BDSKY_Serial.t:adenovirus_polymerase_muscle" spec="beast.evolution.speciation.BirthDeathSkylineModel" 	becomeUninfectiousRate="@becomeUninfectiousRate_BDSKY_Serial.t:adenovirus_polymerase_muscle" 	origin="@origin_BDSKY_Serial.t:adenovirus_polymerase_muscle" reproductiveNumber="@reproductiveNumber_BDSKY_Serial.t:adenovirus_polymerase_muscle" 	samplingProportion="@samplingProportion_BDSKY_Serial.t:adenovirus_polymerase_muscle" tree="@Tree.t:adenovirus_polymerase_muscle">`
                
`<parameter id="RealParameter.1" spec="parameter.RealParameter" dimension="2" name="samplingRateChangeTimes">0.0 <oldest sequence age>.0000001"</parameter>`

`<reverseTimeArrays id="BooleanParameter.0" spec="parameter.BooleanParameter" dimension="6">false false true false false false</reverseTimeArrays></distribution>`



`<prior id="samplingProportionPrior_BDSKY_Serial.t:adenovirus_polymerase_muscle" name="distribution">
	<x id="samplingProportionSlice" spec="util.Slice" 	
		arg="@samplingProportion_BDSKY_Serial.t:adenovirus_polymerase_muscle" index="1"/>
 	<Beta id="Beta.1" name="distr">
       		<parameter id="RealParameter.22" spec="parameter.RealParameter" estimate="false" 			name="alpha">1.0</parameter>
		<parameter id="RealParameter.23" spec="parameter.RealParameter" estimate="false" 			name="beta">9999999.0</parameter>
        </Beta>
</prior>`

And the function element itself disappears!
