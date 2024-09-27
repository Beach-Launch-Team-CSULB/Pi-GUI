import can  # /////////////////////////////////////////////////////////////////////////
import bitstring
from bitarray.util import ba2int
from bitarray import bitarray

bus = can.interface.Bus(channel="can1",bustype='socketcan')
msg = can.Message(arbitration_id=123, data=[1], is_extended_id=True)
bus.send(msg)

bus_type = 'socketcan'
channel0 = 'can0'
bus_receive = can.interface.Bus(channel=channel0, bustype=bus_type)



# noinspection PyTypeChecker
while True:
    msg = can.Message(arbitration_id=23159336, data=[1], is_extended_id=True)
    bus.send(msg)
    msg_in = bus_receive.recv(timeout=None)
    msg_id = msg_in.arbitration_id
    msg_bin = bitstring.BitArray(int=msg_id, length=29).bin
    IDA_bin = msg_bin[-11:]
    IDA = ba2int(bitarray(IDA_bin))
    print(msg_id)
    if IDA == 552:
        HP1_bin = msg_bin[3:10]
        HP2_bin = msg_bin[11:18]
        print(ba2int(bitarray(HP1_bin)))
        print(ba2int(bitarray(HP2_bin)))

    #print(bitstring.BitArray(int=IDA, length=11).bin)
