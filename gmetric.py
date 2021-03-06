 
#!/usr/bin/env python

# To change this license header, choose License Headers in Project Properties.
# To change this template file, choose Tools | Templates
# and open the template in the editor.

__author__="mcanuto"
__date__ ="$Feb 13, 2014 6:03:13 PM$"


from xdrlib import Packer, Unpacker
import socket

slope_str2int = {'zero':0,
                 'positive':1,
                 'negative':2,
                 'both':3,
                 'unspecified':4}

# could be autogenerated from previous but whatever
slope_int2str = {0: 'zero',
                 1: 'positive',
                 2: 'negative',
                 3: 'both',
                 4: 'unspecified'}


class Gmetric:
    """
    Class to send gmetric/gmond 2.X packets

    Thread safe
    """

    type = ('', 'string', 'uint16', 'int16', 'uint32', 'int32', 'float',
            'double', 'timestamp')
    protocol = ('udp', 'multicast')

    def __init__(self, host, port, protocol):
        if protocol not in self.protocol:
            raise ValueError("Protocol must be one of: " + str(self.protocol))

        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        if protocol == 'multicast':
            self.socket.setsockopt(socket.IPPROTO_IP,
                                   socket.IP_MULTICAST_TTL, 20)
        self.hostport = (host, int(port))
        #self.socket.connect(self.hostport)

    def send(self, NAME, VAL, TYPE='', UNITS='', SLOPE='both',
             TMAX=60, DMAX=0, GROUP="", SPOOF=""):
        if SLOPE not in slope_str2int:
            raise ValueError("Slope must be one of: " + str(self.slope.keys()))
        if TYPE not in self.type:
            raise ValueError("Type must be one of: " + str(self.type))
        if len(NAME) == 0:
            raise ValueError("Name must be non-empty")

        ( meta_msg, data_msg )  = gmetric_write(NAME, VAL, TYPE, UNITS, SLOPE, TMAX, DMAX, GROUP, SPOOF)
        #print data_msg

        self.socket.sendto(meta_msg, self.hostport)
        self.socket.sendto(data_msg, self.hostport)

def gmetric_write(NAME, VAL, TYPE, UNITS, SLOPE, TMAX, DMAX, GROUP, SPOOF):
    """
    Arguments are in all upper-case to match XML
    """
    packer = Packer()
    HOSTNAME="test"
    if SPOOF == "":
        SPOOFENABLED=0
    else :
        SPOOFENABLED=1
    # Meta data about a metric
    packer.pack_int(128)
    if SPOOFENABLED == 1:
        packer.pack_string(SPOOF)
    else:
        packer.pack_string(HOSTNAME)
    packer.pack_string(NAME)
    packer.pack_int(SPOOFENABLED)
    packer.pack_string(TYPE)
    packer.pack_string(NAME)
    packer.pack_string(UNITS)
    packer.pack_int(slope_str2int[SLOPE]) # map slope string to int
    packer.pack_uint(int(TMAX))
    packer.pack_uint(int(DMAX))
    # Magic number. Indicates number of entries to follow. Put in 1 for GROUP
    if GROUP == "":
        packer.pack_int(0)
    else:
        packer.pack_int(1)
        packer.pack_string("GROUP")
        packer.pack_string(GROUP)
    
    # Actual data sent in a separate packet
    data = Packer()
    data.pack_int(128+5)
    if SPOOFENABLED == 1:
        data.pack_string(SPOOF)
    else:
        data.pack_string(HOSTNAME)
    data.pack_string(NAME)
    data.pack_int(SPOOFENABLED)
    data.pack_string("%s")
    data.pack_string(str(VAL))

    return ( packer.get_buffer() ,  data.get_buffer() )
  
  
class GmetricConf:
    def __init__(self, host, port, protocol, slope, spoof):
      self.host = host
      self.port = port
      self.protocol = protocol
      self.slope = slope
      self.spoof = spoof
      
      
