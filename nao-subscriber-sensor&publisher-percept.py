#!PySketch/sketch-executor.py
import json
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




left_ema= None
right_ema=None
alfa = 0.5
sat = None
sonarChannels = None
perceptChannel = None
percept_ratio= None
percept = []
sensors = None
import struct
import argparse

args = None
my_body = None

parser = argparse.ArgumentParser(description="Nao Publisher Percept")
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
    global sensors
    args = parser.parse_args()

    sat = FlowSat()
    sat._userName = args.user
    sat._passwd = args.password

    remoteUser = args.publisher_user

    sat.setTickTimer(0.05)
    sat.setNewChanCallBack(onChannelAdded)
    sat.setDelChanCallBack(onChannelRemoved)
    sat.setGrabDataCallBack(onDataGrabbed)
    # ONLY TO NOTIFY requestToStart AND requestToStop FOR PUBLISHING ACTIVITY
    sat.setStartChanPubReqCallBack(onStartChanPub)
    sat.setStopChanPubReqCallBack(onStopChanPub)
   
    ok = sat.connect()
    if ok:

        
        sat.addStreamingChannel(Flow_T.FT_BLOB, Variant_T.T_STRING, "PerceptRatio", " ")
        
        sensors = "sonar"
    
            
       
            
        

        # EXIT if connection is not VALID

    return ok


def loop():
        
      
    if perceptChannel and perceptChannel.isPublishingEnabled:
        print("{},{}".format(left_ema,right_ema))
        sat.publishString(perceptChannel.chanID, "{},{}".format(left_ema,right_ema))

    sat.tick()

  
    # EXIT if connection is not VALID
    return sat.isConnected()

###############################################################################
# CALLBACKs

def onChannelAdded(ch):
    global sonarChannels
    global perceptChannel

     
    if ch.name == "guest.PerceptRatio" :
        perceptChannel= ch
        print("{} Channel ready".format(ch.name))
    
    if ch.name == "guest." + sensors:
        sonarChannels = ch
        print("{} Channel ready".format(ch.name))
        sat.subscribeChannel(ch.chanID)
   



def onChannelRemoved(ch):
    global sat
    global sonarChannels
    global perceptChannel
    
    if ch.name == "guest." + sensors:
            sonarChannels = None

    if ch.name == "guest.PerceptRatio" :
         perceptChannel= None   
   

def onStartChanPub(ch):
    
    if ch.name == "guest.PerceptRatio" :
        print("SkRobot requested to START publishing on {}".format(ch.name))
    



def onStopChanPub(ch):
    
    if ch.name == "guest.PerceptRatio" :
        print("SkRobot requested to STOP publishing on {}".format(ch.name))
    


def onDataGrabbed(chanID, data):
    global sonarChannel
    global percept
    global percept_ratio
    global percept 
    global left_ema
    global right_ema

    ch = sat.channelByID(chanID)

    if ch.name == "guest." + sensors:
        if sonarChannels is None:
            print("Channel NOT ready: {}".format(ch.name))
            return

    # GRAB data FROM Nao - CASTING data-bytearray TO float32
        val, = struct.unpack('{}s'.format(len(data)),data)
        
        decoded_string = val.decode('utf-8')


        print(decoded_string)
        left = float(decoded_string.split(',')[0])
        right= float(decoded_string.split(',')[1])
        
        if left !=None  and right != None :
                left_ema = exponential_moving_average(left, left_ema)
                right_ema = exponential_moving_average(right, right_ema) 
    
      
     
    
def exponential_moving_average(data, prev_ema, alpha=0.9):
    if prev_ema is None:
        return data
    return alpha * data + (1 - alpha) * prev_ema
  

   
    

        
            
###############################################################################
