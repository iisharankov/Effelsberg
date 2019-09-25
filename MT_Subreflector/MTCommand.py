#!/usr/bin/env python
import socket
import datetime
import struct

TCP_IP = '***REMOVED***'
TCP_PORT = ***REMOVED***
BUFFER_SIZE = ***REMOVED***


class MTCommand:
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((TCP_IP, TCP_PORT))

    def sendCommand(self,command):
        self.sock.send(command)
    '''
    So he wants this to be rewritten and cleaned up
    it's probably not correct
    now, midnight, seconds is used to make a unique identifier
    start and end flags are explained in the code
    make sure the length of dataLen is correct. 
    make an __init__ and clean up this class
    cmd_il stands for command interlock and the mode is the command for
    the elevation angle, 1, 2, or 2000. Make all three
    Defined in page 6 and 7 in EFB_SPE documentation 
    
    '''
    def encapsulateCommand(self,command):
        now = datetime.datetime.now()
        midnight = now.replace(hour=0, minute=0, second=0, microsecond=0)
        seconds = (now - midnight).seconds
        startflag=0xdfccf1a
        endflag=0xa1fccfd1
        dataLen=len(command)+4*8
        s= struct.pack("QllsQ",startflag,dataLen,seconds,command,endflag)
        return s

    def setMTElevation(self,elevation):
        cmd_il=106
        mode=2000
        reserve=0.0
        s= struct.pack("Iidd",cmd_il,mode,elevation,reserve)
        return s

    def activateMT(self):
        cmd_il=106
        mode=2
        elevation=0.0
        reserve=0.0
        s= struct.pack("Iidd",cmd_il,mode,elevation,reserve)
        return s

    def close(self):
        self.sock.close()
