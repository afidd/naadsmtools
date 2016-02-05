# naadsmtools
A set of scripts and code to assist with the analysis of simulation results from the North American Animal Disease Simulation Model.

## NAADSM

The
[North American Animal Disease Simulation Model](http://www.naadsm.org/)
simulates spread of diseases among agricultural units on a landscape.
It has two parts, a backend called NAADSM/SC (where SC stands for
supercomputer) that is run from the command line, and a frontend,
which is a Windows graphical user interface (GUI).  The tools
developed here have been targeted to work with NAADSM release 3.2.19,
although we suspect that these should also work with more recent
NAADSM 4.x releases.  There are three ways to get data from a NAADSM
run.

 1. Copy columns from the graphical interface. There are a few outputs the graphical interface will show.
 2. Query the database of results that is internal to NAADSM.
 3. Run NAADSM/SC and print results to a file.

## These tools interpret NAADSM/SC all-units-states output

NAADSM/SC can be configured to produce different types of output data, by specifying the 
relevant <output></output> tags in a NAADSM parameter scenario XML file.  The following 
entry in a scenario file will print the disease state of every unit (farm) for every day in 
a simulation:
<output>
  <variable-name>all-units-states</variable-name>
  <frequency>daily</frequency>
</output>
It is this particular output data that these scripts are intended to analyze.  The first 
step is to process the NAADSM all-units-states data to identify the daily changes of 
state, and to record those events in a file
formatted with [Hierarchical Data Format](https://www.hdfgroup.org/HDF5/), (HDF5).
Subsequent scripts read that event data to create survival analysis plots and
movies which augment analysis done within the NAADSM graphical user interface.
These scripts also serve as examples, in Python and R, for how to read
the HDF5 files with event data.  The HDF5-formatted event file serves to as an 
intermediate data format that we can write results to from other simulation programs 
which specifically simulate individual transitions among states at arbitrary times 
(as opposed to updates of state at a set of discrete times).  
By defining a common data format for two different 
modeling paradigms, we can build downstream tools capable of interpreting either set
of results.

## List of tools

### convert_naadsm_xml.py

NAADSM/SC uses as input XML files specifying model parameters and unit properties, rather than the composite scenario files used by the NAADSM GUI.  The NAADSM GUI can export the units and parameters XML files associated with a NAADSM scenario.  Under some circumstances, however, the resulting XML files will be encoded in UTF-16, while the NAADSM/SC program expects UTF-8 encoded XML files.  

The NAADSM frontend GUI enables users to develop scenarios

On some occasions, 

![Flow diagram for tools](/naadsmtools.png?raw=true "How tools interrelate")
