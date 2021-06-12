# -*- coding: utf-8 -*-
"""
Created on Thu Dec 17 11:45:51 2020

@author: Bhaskar Yechuri
"""

from NatNetClient import NatNetClient

from scipy.spatial.transform import Rotation as R

from datetime import datetime

#latest_rotation = [0,0,0]
#latest_position = [0,0,0]
position_list = []
velocity_list = []
vel_window_size = 3 #CAN CHANGE TO SUIT NEEDS
keep_going = False

def rotationToPhase(rot_tuple):
    rot_vector = [rot_tuple[0],rot_tuple[1], rot_tuple[2], rot_tuple[3]]
    r = R.from_quat(rot_vector).as_euler('zyx', degrees=True)%360 #convert from quaternion to degrees, and move everything to 0->360 range
    return r

# This is a callback function that gets connected to the NatNet client and called once per mocap frame.
def receiveNewFrame( frameNumber, markerSetCount, unlabeledMarkersCount, rigidBodyCount, skeletonCount,
                    labeledMarkerCount, timecode, timecodeSub, timestamp, isRecording, trackedModelsChanged ):
	#print( "Received frame", frameNumber )
	pass

# This is a callback function that gets connected to the NatNet client. It is called once per rigid body per frame
def receiveRigidBodyFrame( id, position, rotation ):
    #print( "Received frame for rigid body", id )
    #print(rotation)
	#global latest_rotation
	#latest_rotation=rotationToPhase(rotation)
	#global latest_position
	#latest_position=position
	global position_list
	now = datetime.utcnow()
	position_list.append([now,position])
	print("Positions: ",now, position)
	if(len(position_list)>vel_window_size):
		vel_from_postiion(vel_window_size)
	
	#print(latest_rotation)

def vel_from_postiion(window_size):
	
	global position_list
	global velocity_list
	sum_x = 0
	sum_y = 0
	sum_z = 0
	time_before = position_list[len(position_list)-1-(window_size-1)][0]
	time_after = position_list[len(position_list)-1][0]
	for i in range(0, window_size-1):
		sum_x += position_list[len(position_list)-1-i][1][0] - position_list[len(position_list)-1-(i+1)][1][0]
		sum_y += position_list[len(position_list)-1-i][1][1] - position_list[len(position_list)-1-(i+1)][1][1]
		sum_z += position_list[len(position_list)-1-i][1][2] - position_list[len(position_list)-1-(i+1)][1][2]
		
	#print("Sums: ", sum_x, sum_y, sum_z)
	vel_x = (sum_x/(window_size-1))/(time_after-time_before).total_seconds()
	vel_y = (sum_y/(window_size-1))/(time_after-time_before).total_seconds()
	vel_z = (sum_z/(window_size-1))/(time_after-time_before).total_seconds()
	
	print("Velocities: ",time_after, (vel_x, vel_y, vel_z))
	velocity_list.append([time_after, (vel_x, vel_y, vel_z)])
	
	pass	

# This will create a new NatNet client
streamingClient = NatNetClient()

# Configure the streaming client to call our rigid body handler on the emulator to send data out.
streamingClient.newFrameListener = receiveNewFrame
streamingClient.rigidBodyListener = receiveRigidBodyFrame

# Start up the streaming client now that the callbacks are set up.
# This will run perpetually, and operate on a separate thread.
streamingClient.run()


import sys
import numpy as np

import psychopy.visual
import psychopy.event
import psychopy.core

win = psychopy.visual.Window(
    size=[400, 400],
    units="pix",
    fullscr=False
)

#grating = psychopy.visual.GratingStim(
#    win=win,
#    size=[200, 200],
#    mask="circle",
#    units="pix",
#    sf=5.0 / 200.0
#)

clock = psychopy.core.Clock()

keep_going = True

#TEMP LINE
#grating.phase = np.interp(latest_rotation[0], [0, 360], [0,1])


while keep_going:

    #grating.phase = np.interp(latest_rotation[0], [0, 360], [0,1])

    #grating.draw()

    win.flip()

    keys = psychopy.event.getKeys()

    if len(keys) > 0:
        keep_going = False

win.close()

print("DONE")
sys.exit()