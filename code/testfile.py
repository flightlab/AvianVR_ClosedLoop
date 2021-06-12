# -*- coding: utf-8 -*-
"""
Created on Thu Dec 17 11:45:51 2020

@author: Bhaskar Yechuri
"""

from NatNetClient import NatNetClient

from scipy.spatial.transform import Rotation as R

latest_rotation = [0,0,0]

def rotationToPhase(rot_tuple):
    rot_vector = [rot_tuple[0],rot_tuple[1], rot_tuple[2], rot_tuple[3]]
    r = R.from_quat(rot_vector).as_euler('zyx', degrees=True)%360 #convert from quaternion to degrees, and move everything to 0->360 range
    return r

# This is a callback function that gets connected to the NatNet client and called once per mocap frame.
def receiveNewFrame( frameNumber, markerSetCount, unlabeledMarkersCount, rigidBodyCount, skeletonCount,
                    labeledMarkerCount, timecode, timecodeSub, timestamp, isRecording, trackedModelsChanged ):
    print( "Received frame", frameNumber )

# This is a callback function that gets connected to the NatNet client. It is called once per rigid body per frame
def receiveRigidBodyFrame( id, position, rotation ):
    print( "Received frame for rigid body", id )
    #print(rotation)
    global latest_rotation
    latest_rotation=rotationToPhase(rotation)
    #print(latest_rotation)


# This will create a new NatNet client
streamingClient = NatNetClient()

# Configure the streaming client to call our rigid body handler on the emulator to send data out.
streamingClient.newFrameListener = receiveNewFrame
streamingClient.rigidBodyListener = receiveRigidBodyFrame

# Start up the streaming client now that the callbacks are set up.
# This will run perpetually, and operate on a separate thread.
streamingClient.run()



import numpy as np

import psychopy.visual
import psychopy.event
import psychopy.core

win = psychopy.visual.Window(
    size=[400, 400],
    units="pix",
    fullscr=False
)

grating = psychopy.visual.GratingStim(
    win=win,
    size=[200, 200],
    mask="circle",
    units="pix",
    sf=5.0 / 200.0
)

clock = psychopy.core.Clock()

keep_going = True

while keep_going:

    grating.phase = np.interp(latest_rotation[0], [0, 360], [0,1])
    print

    grating.draw()

    win.flip()

    keys = psychopy.event.getKeys()

    if len(keys) > 0:
        keep_going = False

win.close()