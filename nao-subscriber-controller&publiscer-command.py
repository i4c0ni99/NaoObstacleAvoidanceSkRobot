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
sensors={}
sat = None
robot = None
import struct
import argparse
command = None
perceptChan=None
sonarChannels={}
commandChan = None
prevCommand= " "
args = None
my_body = None
threshold_distance= 0.7

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
    global args
    global sat
    global sonarChannels
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
        
        sat.addStreamingChannel(Flow_T.FT_BLOB, Variant_T.T_STRING, "Command", " ")
        
        """  sensors = {"LeftSonar":0, "RightSonar":0}
    
            
        for sensor in sensors:
            longName = "{}.{}".format(remoteUser, sensor)
            sonarChannels[longName] = None
            print("Prepared sensor-channel to open: {}".format(longName)) """
            
            
        

        # EXIT if connection is not VALID

    return ok

def loop():
    global prevCommand


    if commandChan and command and prevCommand:
            #print(f"{command},{prevCommand}")
            if  command != prevCommand :
                print(command)
                prevCommand = command
                sat.publishString(commandChan.chanID, command)
    sat.tick()



    # EXIT if connection is not VALID
    return sat.isConnected()

###############################################################################
# CALLBACKs

def onChannelAdded(ch):
    global perceptChan
    global commandChan
    
    if ch.name == "guest.PerceptRatio":
        perceptChan = ch
        print("{} Channel ready".format(ch.name))
        sat.subscribeChannel(ch.chanID)

    if ch.name == "guest.Command":
        commandChan = ch
        print("{} Channel ready".format(ch.name))

    """  if ch.name in sonarChannels:
        sonarChannels[ch.name] = ch
        print("{} Channel ready".format(ch.name))
        sat.subscribeChannel(ch.chanID) """
        


def onChannelRemoved(ch):
    global perceptChan
    global commandChan
    

    if ch.name == "guest.PerceptRatio":
       perceptChan = None

    if ch.name == "guest.Command":
       commandChan = None
    
    """ if ch.name in sonarChannels:
        sonarChannels[ch.name] = None   
 """
def onStartChanPub(ch):
    
    if ch.name == "guest.Command" :
        print("SkRobot requested to START publishing on {}".format(ch.name))
    



def onStopChanPub(ch):
    
    if ch.name == "guest.Command" :
        print("SkRobot requested to STOP publishing on {}".format(ch.name))



def constrollerSendCommand(left_ema,right_ema):
    global command

    if left_ema is None or right_ema is None:
                return

    if left_ema < threshold_distance or right_ema < threshold_distance:
        if left_ema < threshold_distance and right_ema < threshold_distance:
            # Se entrambi i sensori rilevano un ostacolo, fermarsi e girare
            command = "Ruota"
        elif left_ema < threshold_distance:
            # Se l'ostacolo è a sinistra, gira a destra
            command = "Destra"
            #self.motion_proxy.moveTo(0, 0, -0.5)  # Ruota di -0.5 radianti (circa -28.5 gradi)
        elif right_ema < threshold_distance:
            command = "Sinistra"
            # Se l'ostacolo è a destra, gira a sinistra
            #self.motion_proxy.moveTo(0, 0, 0.5)  # Ruota di 0.5 radianti (circa 28.5 gradi)
    else:
        # Se non ci sono ostacoli vicini, vai avanti
        command = "Avanti"
        #self.motion_proxy.moveTo(0.5, 0, 0)  # Avanza di 0.5 metri


def onDataGrabbed(chanID, data):
    global sonarChannels
    global actuatorChannels
    global sensors
    

    ch = sat.channelByID(chanID)
    val = None
    if ch.name == "guest.PerceptRatio":
       
        
        # GRAB data FROM Nao - CASTING data-bytearray TO float32
        val, = struct.unpack(f"{len(data)}s",data)
        decoded_string = val.decode('utf-8')


        
        left_ema = float(decoded_string.split(',')[0])
        right_ema= float(decoded_string.split(',')[1])
        if left_ema != None and right_ema != None:
                #print(f"EMA distanza sinistra: {left_ema:.2f} m, EMA distanza destra: {right_ema:.2f} m")
                constrollerSendCommand(left_ema, right_ema)
        #time.sleep(0.025)
        
    



  
            
###############################################################################
