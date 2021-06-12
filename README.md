_Author: [Bhaskar Yechuri](bhaskar.yechuri@gmail.com), Engineering Technician & Research Assistant at the [Altshuler Lab](https://altshuler.zoology.ubc.ca/), University of British Columbia - Vancouver (Last Updated: June 2021)_

# Avian VR Closed Loop System

# Summary

This set of python examples builds the basis of a closed-loop virtual reality system for avian test subjects. The system is built upon a [state-space model](https://en.wikipedia.org/wiki/State-space_representation#Linear_systems), where incoming data causes the state variable(s) to be updated at each timepoint. The system's state at each timepoint then goes on to determine the system's output. In the case of this system:
* The input data is the live rigid body data (position & rotation) streamed from [OptiTrack Motive](https://optitrack.com/software/motive/) and received by the python script using the [NatNet SDK](https://optitrack.com/software/natnet-sdk/)
* The script stores and processes incoming data and updates its internal state variables
* The state variable is then used to modify the display parameters of an arbitrary stimulus (grating, dotfield, etc.) on the TV screens using [psychopy](https://www.psychopy.org/), a Psychtoolbox package built for python 

This project can allows experimenters to artificially manipulate/control aspects of the test subject's visual perception such as optic flow, rate of expansion, etc. 

# Usage

To use the system, only two files are needed (in the same directory) - the library file (`NatNetClient`) and the file in which your script is written. This second file is the one that you will need to run in order to start the system.

The following steps must be carried out once the two files are present in the same folder:
1. First, open the `NatNetClient.py` file and modify the `serverIPAddress` and `localIPAddress` values based on the streaming settings chosen in Optitrack Motive. 
    1. If Optitrack Motive and the script are running on the same machine, then both addresses can be set to `127.0.0.1`, which is the loopback IP address.
1. Next, the script file (containing your experiment-specific code to read incoming Motive data, process it, and output commands to TV screens) can be run via the command line
    1. This repository contains examplar scripts I've written (such as `testscript.py`, `vel_calc.py` and `roe_calc.py` which calculate/store instantaneous position, velocity, and rate of expansion respectively) which can be run instead of writing new scripts from scratch. 
    1. These scripts show users how to calculate those state variables, but don't actually act upon that information. Instead, what the system does in response to these state variables is left to the experimenter to implement, since this will depend on the experiment being run and this implementation is quite straightforward to those familiar with writing code. Modifiable parameters are also defined at the top of the script files to allow for easy modification by future users.
1. Once it is running, the script will print directly to the command line window, which shows the user that the program is running

# Notes & Limitations

The system built thus far is still in development, but contains the engine & mathematics upon which additional features and behaviour can be built. Moving forward, the following factors need to be considered:
* The time lag of the system has not been quantified, so that will be necessary to ensure that it is usable for avian test subjects. If the system is not fast enough, modifications to the code might be needed to optimize it further
* While the system has passed the eye test during development, the absolute accuracy of the various components also needs to be tested and documented to ensure that the state variables being calculated are indeed correct. For example, moving a rigid body by a pre-set distance, or at a known velocity could help study the absolute accuracy of the system (which includes the combination of Optitrack live data and the python code)
* Finally, prior to performing any experiment, the system will need to be calibrated because the code uses the (0,0,0) point defined in Optitrack as the reference point, and has assigned arbitrary units to the Optitrack position data being received. This should not be too difficult to solve, since the methods mentioned in the previous bullet point could help with the calculation of scaling factors which could be applied to solve this problem
