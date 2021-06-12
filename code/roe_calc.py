# -*- coding: utf-8 -*-
"""
Created on Thu Dec 17 11:45:51 2020

@author: Bhaskar Yechuri
"""
import sys
import numpy as np

import psychopy.visual
import psychopy.event
import psychopy.core

from NatNetClient import NatNetClient

from scipy.spatial.transform import Rotation as R

from datetime import datetime

import math

#latest_rotation = [0,0,0]
latest_position = [0,0,0]
position_list = []
velocity_list = []
vel_window_size = 3 #CAN CHANGE TO SUIT NEEDS
keep_going = False
latest_theta = 0
latest_sf = 0
theta_list = []
sf_list = []
target_expansion_rate = 0 #[s^-1]


def rotationToPhase(rot_tuple):
    rot_vector = [rot_tuple[0],rot_tuple[1], rot_tuple[2], rot_tuple[3]]
    r = R.from_quat(rot_vector).as_euler('zyx', degrees=True)%360 #convert from quaternion to degrees, and move everything to 0->360 range
    return r

# This is a callback function that gets connected to the NatNet client and called once per mocap frame.
def receiveNewFrame(frameNumber, markerSetCount, unlabeledMarkersCount, rigidBodyCount, skeletonCount,
                    labeledMarkerCount, timecode, timecodeSub, timestamp, isRecording, trackedModelsChanged ):
	#print( "Received frame", frameNumber )
	pass

# This is a callback function that gets connected to the NatNet client. It is called once per rigid body per frame
def receiveRigidBodyFrame( id, position, rotation ):
    #print( "Received frame for rigid body", id )
    #print(rotation)
	#global latest_rotation
	#latest_rotation=rotationToPhase(rotation)
	global latest_position
	latest_position=position
	#print(latest_position)
	global position_list
	now = datetime.utcnow()
	position_list.append([now,position])
	#print("Positions: ",now, position)
	if(len(position_list)>vel_window_size):
		vel_from_postiion(vel_window_size)
		
	global grating
	if((len(sf_list)>=1) & (len(theta_list)>=1) & (len(position_list)>=1)):
		print("calculating:")
		calc_theta_next()
		calc_sf_next()
		#at this point x, theta, and sf have been calculated for the current timepoint, so let's write the value to the grating
		grating.sf = sf_list[len(sf_list)-1][1] #the value has now been updated, but the grating window won't update until the grating.draw() and win.flip() lines run in the forever loop below
	
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
	
	#print("Velocities: ",time_after, (vel_x, vel_y, vel_z))
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



def calc_theta_next():
	global target_expansion_rate
	global theta_list
	
	print("Entered calc_theta_next")
	theta_next = target_expansion_rate*theta_list[len(theta_list)-1][1]*(datetime.utcnow()-theta_list[len(theta_list)-1][0]).total_seconds() + theta_list[len(theta_list)-1][1]
	theta_list.append([datetime.utcnow(), theta_next])
	
	return
	
def calc_sf_next():
	global theta_list
	global position_list
	global sf_list
	
	print("Entered calc_sf_next")
	
	theta_val = theta_list[len(theta_list)-1][1]
	x_val = position_list[len(position_list)-1][1][0]
	print("theta_val is ", theta_val, " and x_val is ", x_val)

	
	if(abs(x_val) < 1.0/1000000.0) or (abs(math.sin(theta_val)) < 1.0/1000000.0):
		sf_next = 999999 #arbitrarily high sf value
		sf_list.append([datetime.utcnow(), sf_next])
		print("x_val or sin(theta_val) too low, writing an arbitrarily high SF value")
		return
	
	theta_val = (1/math.sin(theta_val))**2
	theta_val = math.sqrt(theta_val-1)
	
	
	sf_next = theta_val/(2*x_val)
	print("sf_next is ", sf_next)
	sf_list.append([datetime.utcnow(), sf_next])
	
	return

win = psychopy.visual.Window(
    size=[400, 400],
    units="pix",
    fullscr=False
)

#TEMP LINE
#grating.phase = np.interp(latest_rotation[0], [0, 360], [0,1])

grating = psychopy.visual.GratingStim(
    win=win,
    size=[800, 200],
    mask="None",
    units="pix",
    sf=5.0 / 200.0
)

#initialize theta and sf lists. position list will already contain many entries
sf_list.append([datetime.utcnow(), 5.0/200.0])
theta = math.asin(1/(2*sf_list[len(sf_list)-1][1]*math.sqrt((latest_position[0])**2 + 0.25/(sf_list[len(sf_list)-1][1] ** 2) )))
theta_list.append([datetime.utcnow(),theta])
print("values written, lengths of the arrays are:")
print(str(len(sf_list)), str(len(theta_list)))
clock = psychopy.core.Clock()

keep_going = True


while keep_going:
	print("lengths of the arrays are:")
	print(str(len(sf_list)), str(len(theta_list)))
	#print("inputting:")
	#print("current position is", latest_position)
	
	
	#print("theta: ", theta)
	#print(str(latest_position[1][0]))
	thickness = np.interp(latest_position[0], [0, 0.5], [0,10.00])
	grating.sf = thickness


	grating.draw()

	win.flip()

	keys = psychopy.event.getKeys()

	if len(keys) > 0:
		keep_going = False

win.close()

print("DONE")
sys.exit()