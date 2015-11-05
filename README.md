# naadsmtools
A set of scripts and code to help with analysis of the North American Animal Disease Simulation Model.

## What is NAADSM?
The [North American Animal Disease Simulation Model](http://www.naadsm.org/)
simulates spread of diseases among agricultural units on a landscape.
It has two parts, a backend called NAADSM/SC (where SC stands for supercomputer),
and a frontend, which is a Windows graphical user interface.
There are three ways to get data from a NAADSM run.

 1. Copy columns from the graphical interface. There are a few outputs the graphical interface will show.
 2. Query the database of results that is internal to NAADSM.
 3. Run NAADSM/SC and print results to a file.

## These scripts interpret NAADSM/SC output
NAADSM/SC will print the state of disease at farms, and other output,
to the screen. These scripts interpret that that output as changes to
the state of the simulation and record the events in an file
formatted with [Hierarchical Data Format](https://www.hdfgroup.org/HDF5/), (HDF5).
Subsequent scripts read that event data to create survival analysis plots and
movies which augment analysis done by the NAADSM graphical user interface.
These scripts also serve as examples, in Python and R, for how to read
the HDF5 files with event data.
