#!/usr/bin/env python
import datetime
import ctypes


now = datetime.datetime.now()
startflag = 0x1DFCCF1A
endflag = 0xA1FCCFD1
cmd_il, mode, elevation, reserve = (106, 2000, 0.0, 0.0)
dataLen = 64

# C type structure identical to one in C code
class pkg(ctypes.Structure):
    _fields_ = [("start_flag", ctypes.c_ulong),
                ("message_length", ctypes.c_long),
                ("command_serial_number", ctypes.c_long),
                ("command", ctypes.c_long),
                ("mode", ctypes.c_short),
                ("elevation", ctypes.c_double),
                ("reserved", ctypes.c_double),
                ("end_flag", ctypes.c_ulong)]


# Tests that the size of the above structure indeed is 64
assert (ctypes.sizeof(pkg())) == 64

# Creates a instance of the structure
struct_instance = pkg(startflag, 64, 12345, cmd_il, mode, elevation, reserve, endflag)

#  Function to change instance to bytes
def Pack(ctype_instance):
    buf = ctypes.string_at(ctypes.byref(ctype_instance), ctypes.sizeof(ctype_instance))
    return buf

# Respective way to change back
def Unpack(ctype, buf):
    cstring = ctypes.create_string_buffer(buf)
    ctype_instance = ctypes.cast(ctypes.pointer(cstring), ctypes.POINTER(ctype)).contents
    return ctype_instance

# This is the bytes string that was sent by the Cpp code
cbytes = b'\x1a\xcf\xfc\x1d\x00\x00\x00\x00@\x00\x00\x00\x00\x00\x00\x0090\x00\x00\x00\x00\x00\x00j\x00\x00\x00\x00\x00\x00\x00\xd0\x07\xff\xff\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xd1\xcf\xfc\xa1\x00\x00\x00\x00'
print(f"Cbytes: \n {cbytes}")

# Below is our packed version of that string, almost identical except two individual bits in the 4th byte
packaged_struct_instance_with_pack = Pack(struct_instance)
print(f"packaged_struct_instance_with_pack: \n {packaged_struct_instance_with_pack}")

# Unpackaging the bytes created by python back into an struct instance
unpacked_instance = Unpack(pkg, packaged_struct_instance_with_pack)
print('\nUnpackaged Python bytes created by Ctypes then packed')
print(f'start_flag: {unpacked_instance.start_flag} \n'
      f'message_length: {unpacked_instance.message_length} \n'
      f'command_serial_number: {unpacked_instance.command_serial_number} \n'
      f'command: {unpacked_instance.command} \n'
      f'mode: {unpacked_instance.mode} \n'
      f'elevation: {unpacked_instance.elevation} \n'
      f'reserved: {unpacked_instance.reserved} \n'
      f'end_flag: {unpacked_instance.end_flag} \n')


# Unpackaging the bytes created by Cpp back into an struct instance
unpacked_cpp_bytes = Unpack(pkg, cbytes)
print('\nUnpackaged C++ bytes as read from the Python server from the file')
print(f'start_flag: {unpacked_cpp_bytes.start_flag} \n'
      f'message_length: {unpacked_cpp_bytes.message_length} \n'
      f'command_serial_number: {unpacked_cpp_bytes.command_serial_number} \n'
      f'command: {unpacked_cpp_bytes.command} \n'
      f'mode: {unpacked_cpp_bytes.mode} \n'
      f'elevation: {unpacked_cpp_bytes.elevation} \n'
      f'reserved: {unpacked_cpp_bytes.reserved} \n'
      f'end_flag: {unpacked_cpp_bytes.end_flag} \n')


print(
    '''
    The two byte strings are almost exactly the same, spare two bits that are
    different. One being \\x00\\x00, the other being \\xff\\xff. Yet this seems
    to maybe be part of a buffer, as no change in the unpacking of the bytes to 
    a instance to a ctype struct is seen. 
    
    Things to note:
        1) We ran the Cpp program, no crash happened, no changes were found on 
        the control room monitor nor on the output status report on port ***REMOVED***.
        This was tested with changing elevation, and activating/deactivating the
        Subreflector (SR). "At least it doesn't crash"
        
        2) We ran the Python MTCommand.py program.  First trial was with sending 
        a struct_instance as shown above, I believe of size was 64 (but maybe 
        it was 100? Don't remember). This crashed the SR again as usual even 
        though it was a new method (ctypes instead of struct) of making the 
        bytes string
    
        3) Coffee break.
        
        4) After Coffee, I discovered that the Cpp sends an empty bytes string. 
        This was noted as mt is a struct, but when sent to a Python server, the 
        Python server received only an empty bytes string. If this is what the 
        (SR) receives as well, then it makes sense as to why it does not crash 
        (empty string sent), and also why it does not run any command or change 
        any status output internally. We tested MTCommand.py again, this time 
        sending an empty byte string (simply sock.send(b'') ). The SR did not 
        crash, nor did it respond. Similar response as with the Cpp program.
        
        5) mt was changed with outStream in the Cpp program, a bytes stream of 
        the data. This was recieved by the Python server as the cbytes string 
        shown above. This was also sent to the SR, this time no change was 
        noted yet again, but also it still did not crash. 
        
        6) No extra tests were done, but a suggested test is sending, in 
        MTCommand.py, the bytes string we obtained from the Cpp. The only 
        physical difference between the strings are two bits, mentioned above.
        These two bits do not interfere with the deconstructing of the message
        to a structure. They do not change or effect any of the parameters in
        the structure, *BUT* we do not know if that is true with the SR. Maybe 
        the decoder in the SR does not work like the ctype Unpack function above.
        So even though two two different strings unpack to the same values here,
        that does not mean they do so in the SR. Testing sending the Cpp bytes 
        string in the MTCommand.py module will tell us the following:
            
            i) if the SR still crashes, this strongly indicates that the error 
            is not in the bytes string, but rather the fact that it's being sent
            by a Python socket in Python vs Cpp socket in Cpp. (or any other 
            similar external issue). Of course, ideally, these messages from the
            two sockets should be the exact same, but it is not safe to rule out
            the possibility that these sockets are not received the same if this 
            test crashes the SR yet again. If a message sent in the Cpp does not
            crash the SR, but the exact same bytes sequence in MTCommand.py does
            crash the SR, then the error must be elsewhere.
            
            ii) If the SR does not crash with the Cpp bytes string sent in 
            MTCommand.py. This suggests several issues. The main one being that
            the two bits difference between the strings may be causing the 
            SR decoder to crash as it is unrecognized, even if ctypes still can
            decode the bytes string fine. If this is the case, the best fix is
            to find out why those two bits are encoded differently, and if that
            is an issue for all types of commands sent to the SR. 3 different 
            python modules all have Cpp struct creating functionality  (struct, 
            array, and ctypes). All three output the same bytes string with the 
            modified two bits. Why is that the case when the Cpp has a different
            string?
            
        7) Also, the Cpp file did not successfully change any output status on 
        the SR,  suggesting that even though the commands from the Cpp file do
        not crash the SR, they do not change anything either. So no matter how
        or why the Python struct issue is fixed, we must find out why the 
        modified Cpp file does not send commands, when it is taken from the real
        version, which obviously works correctly. I recall a small difference in
        the Cpp code that change the length from 64 to 100 bits. Maybe this
        is critical for the SR to read the input? If so, we need to:
        
            i) Test it in the Cpp and get it working, have commands sent, and 
            have the output on port ***REMOVED*** notice the change. 
            
            ii) Capture the output of the corrected Cpp code and make sure the 
            Python MTCommand.py can do the same functionality. 
            
    '''
)