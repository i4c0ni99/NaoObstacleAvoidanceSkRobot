#!PySketch/sketch-executor.py
import time


###############################################################################
##
## Copyright (C) Daniele Di Ottavio (aka Tetsuo)
## Contact: tetsuo.tek (at) gmail (dot) com
##
## This program is free software; you can redistribute it and/or
## modify it under the terms of the GNU General Public License
## as published by the Free Software Foundation; either version 3
## of the License, or (at your option) any later version.
##
## This program is distributed in the hope that it will be useful,
## but WITHOUT ANY WARRANTY; without even the implied warranty of
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
## GNU General Public License for more details.
##
## You should have received a copy of the GNU General Public License
## along with this program; if not, write to the Free Software
## Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.
##
###############################################################################

# Could be PySketch_py2 or PySketch_py3
# linked as ./PySketch, for example: ln -s ./PySketch_py3 ./PySketch

from PySketch.elapsedtime import ElapsedTime
from PySketch.abstractflow import FlowChannel
from PySketch.flowsync import FlowSync
from PySketch.flowproto import FlowChanID, Variant_T, Flow_T
from PySketch.flowsat import FlowSat

import sys
import time
import pybullet as p
from qibullet import SimulationManager

sat = None
sonarChannels = {}
actuatorChannels = {}
robot = None
simulation_manager = None
client = None
joint_parameters = list()
import struct
import argparse

args = None
my_body = None

parser = argparse.ArgumentParser(description="Nao subscriber")
parser.add_argument('sketchfile', help='Sketch program file')
parser.add_argument('--user', help='Flow-network username', default='guest')
parser.add_argument('--password', help='Flow-network password', default='password')
parser.add_argument('--publisher-user', help='Flow-network publisher', default='guest')

# IT DOES NOT REQUIRE TO IMPORT pynaqi library
# data will come from SkRobot flow connection

###############################################################################
# SKETCH

def setup():
    global my_body
    global args
    global sat
    global robot
    global joint_parameters
    global simulation_manager
    global client

    args = parser.parse_args()

    sat = FlowSat()
    sat._userName = args.user
    sat._passwd = args.password

    remoteUser = args.publisher_user

    simulation_manager = SimulationManager()

    
    # Auto stepping set to False, the user has to manually step the simulation
    
    client = simulation_manager.launchSimulation(gui=True, auto_step=False)

     
    robot = simulation_manager.spawnNao(client, spawn_ground_plane=True)

   
    
    

     
    sat.setNewChanCallBack(onChannelAdded)
    sat.setDelChanCallBack(onChannelRemoved)
    sat.setGrabDataCallBack(onDataGrabbed)

    # EXIT if connection is not VALID
    sat.setTickTimer(0.01)
   


    actuators = ['HeadYaw', 'HeadPitch',
                 'LShoulderPitch', 'LShoulderRoll', 'LElbowYaw', 'LElbowRoll',
                 'LHipYawPitch', 'LHipRoll', 'LHipPitch', 'LKneePitch', 'LAnklePitch', 'LAnkleRoll',
                 'RHipYawPitch', 'RHipRoll', 'RHipPitch', 'RKneePitch', 'RAnklePitch', 'RAnkleRoll',
                 'RShoulderPitch', 'RShoulderRoll', 'RElbowYaw', 'RElbowRoll']
    """
        sensors = ["LeftSonar", "RightSonar"]
    
        for sensor in sensors:
            longName = "{}.{}".format(remoteUser, sensor)
            sonarChannels[longName] = None
            print("Prepared sensor-channel to open: {}".format(longName))
    """
    for name in robot.joint_dict.keys():
            if "Finger" not in name and "Thumb" not in name:
                joint_parameters.append(name)
    for actuator in actuators:
        longName = "{}.{}".format(remoteUser, actuator)
        actuatorChannels[longName] = None
        print("Prepared actuator-channel to open: {}".format(longName))

    # EXIT if connection is not VALID

    return sat.connect()


def loop():

    sat.tick()
    # EXIT if connection is not VALID
    return sat.isConnected()

###############################################################################
# CALLBACKs

def onChannelAdded(ch):
    global sonarChannels
    global actuatorChannels

    """
    if ch.name in sonarChannels:
        sonarChannels[ch.name] = ch
        print("{} Channel ready".format(ch.name))
        sat.subscribeChannel(ch.chanID)
    """
    if ch.name in actuatorChannels:
        actuatorChannels[ch.name] = ch
        print("{} Channel ready".format(ch.name))
        sat.subscribeChannel(ch.chanID)




def onChannelRemoved(ch):
    global sat
    global sonarChannels
    global actuatorChannels

    if ch.name in actuatorChannels:
        actuatorChannels[ch.name] = None




def onDataGrabbed(chanID, data):
    global sonarChannels
    global actuatorChannels

    ch = sat.channelByID(chanID)
  
    if ch.name in actuatorChannels:
        if actuatorChannels[ch.name] is None:
           # print("Channel NOT ready: {}".format(ch.name))
            return
        
        # GRAB data FROM Nao - CASTING data-bytearray TO float32
        val, = struct.unpack('<f',data)
        joint_name = ch.name.split(".")[1]
        
       

       

        
        
            
        for joint_parameter in joint_parameters:
            
            if joint_parameter == joint_name:
                
                print(joint_parameter,val,1.0)
                robot.setAngles(joint_parameter,val,1.0)

        # Step the simulation
        simulation_manager.stepSimulation(client)
            
###############################################################################
