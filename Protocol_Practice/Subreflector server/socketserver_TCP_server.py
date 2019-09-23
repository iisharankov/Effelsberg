import socketserver
import threading
import socket
import struct
import time
import json
import re


dict = {}

class MyUDPHandler(socketserver.BaseRequestHandler):
    """
    The request handler class the server.
    """

    def setup(self):
        pass
        # print("Incoming message")

    def handle(self):
        # self.request is the UDP connected to the client
        # print(self.request)

        # takes message, decodes to string and - all whitespace (by rejoining)
        self.telnet_msg = ''.join(self.request[0].decode('utf-8').
                                  lower().split())

        socket = self.request[1]
        cur_thread = threading.current_thread()
        print("{} wrote this on thread {}".format(self.client_address[0],
                                                  cur_thread.name))
        print(self.telnet_msg)
        if self.telnet_msg.startswith('variable:'):
            self.telnet_msg = self.telnet_msg.replace('variable:', '')

            try:
                # self.telnet_msg is in form "variable=value" or "variable", so
                # check there is one or no "=" signs
                assert self.telnet_msg.count("=") <= 1
            except AssertionError:
                msg = "More than one equals sign in message"

            else:
                # If 1 =  sign, then we know something is being set
                if self.telnet_msg.count("=") == 1:
                    
                    # Replace = with : to parse into temp JSON
                    # self.telnet_msg = self.telnet_msg.replace('=', ':')
                    varName, value = self.telnet_msg.split('=', 1)

                    """
                    This is a clever trick. Above we grabbed both sides of the 
                    equal sign (varName and value). But we don't know what the 
                    type is of the value. Of course it's a string, as that's 
                    what input returns, but maybe they input "7" and meant the 
                    int 7, or "7.0" as a float, or "[2, 3]" as a list. if we 
                    type("[2, 3]") we get a string, not a list. This can be 
                    solved weakly with many if statements. Instead, we 
                    use the below line to set up varName and value into a
                    string that has the *exact* format needed to parse it into a
                    temporary JSON. Basically, we use a temp JSON to serialize
                    the value, and the serialization will calculate the correct
                    type for the value (int, str, float, bool, list), then we 
                    index the tempjson for the one value it has, and this time
                    instead of getting '"7"' (a string with a 7 in it), we get 
                    '7' (the int 7). Now we have the true value and the 
                    varName, and we can use this to put the real value into
                    the final JSON object!
                    """

                    # This line replaces single quotes with double quotes from
                    # the value variable. This means either input will work
                    value = value.replace("'", '"')
                    # I'm amazed ('"', "'")  does not violate PEP-8...

                    # The ugly line that sets up the varName and value (both
                    # strings) into a larger string of the correct format
                    data = '{' + '"' + varName + '":' + value + '}'
                    # I'm also curious how this violates PEP-8 too...

                    # Now load this correct data string into a tempjson
                    # Todo: add a try-except on loads for bad values
                    tempjson = json.loads(data)  # this will serialize the value
                    
                    # Now call the value of the varName in the JSON dict
                    true_value = tempjson[varName]
                    print(f'Value of {varName} is "{true_value}" and the type '
                          f'of the value is {type(true_value)}')
                    
                    # Now add to the real dictionary the true_value and varName!
                    dict[varName] = true_value
                    msg = f"Variable {varName} set to {true_value}"
                    # And like that, we found the true type() of the
                    # contents of a string

                # if no "=" sign, then user is asking for value of varName given
                else:
                    assert self.telnet_msg.count("=") == 0
                    varName = self.telnet_msg
                    if varName in dict:
                        print(varName)
                        # TODO Bug: this next line fails for returning lists, 
                        # unhashable
                        msg = 'The set value for {} is ' \
                              '{}'.format(varName, {dict[varName]})
                    else:
                        msg = f"{varName} was not found/was never set"

        # Called if user wants to see full JSON object
        elif self.telnet_msg == 'returnvariables':
            msg = json.dumps(dict)
            print(msg)
        
        # Checks if the telnet_msg is in the multicast strings
        elif self.telnet_msg in multicastdata:  # == 'mjuld':

            # Finds the location of the variable in the multicast message
            loc = multicastdata.find(self.telnet_msg)
            multicast_var = (multicastdata[loc:loc+50])

            # Format to remove everything after comma, and remove a quote
            multicast_var = multicast_var.replace('"', '').split(",", 1)[0]
            msg = multicast_var

        # Invalid input by user
        else:
            msg = f"{self.telnet_msg} is not a valid input or not recognized"

        # Message to return to client
        socket.sendto(msg.encode(), self.client_address)

    def finish(self):
        pass
        # print("End of message.")


class ThreadingUDPServer(socketserver.ThreadingMixIn, socketserver.UDPServer):
    pass


if __name__ == "__main__":
    destination_address = ('***REMOVED***', ***REMOVED***)
    # destination_address = ('localhost', 9999)

    # Create the server, binding to localhost on port 9999
    # server = socketserver.UDPServer(destination_address, MyUDPHandler)
    server = ThreadingUDPServer(destination_address, MyUDPHandler)
    with server:
        ip, port = server.server_address

        # Start a thread with the server -- that thread will then start one
        # more thread for each request
        server_thread = threading.Thread(target=server.serve_forever)

        mcast_group = ***REMOVED***
        server_address = ('', 1602)  # sdh json
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.bind(server_address)
        group = socket.inet_aton(mcast_group)
        mreq = struct.pack('4sL', group, socket.INADDR_ANY)
        sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)
        multicastdata_bytes, address = sock.recvfrom(300000)
        multicastdata = str(multicastdata_bytes)

        # Exit the server thread when the main thread terminates
        server_thread.daemon = True
        server_thread.start()
        print("Server loop running in thread:", server_thread.name)

        # Activate the server; this will keep running until you
        # interrupt the program with Ctrl-C
        server.serve_forever()

'''
Part two will be harder. Go into sdh.py (/opt/operatorguis/VMEDisplay/sdh.py)
where just under the GUI section line you have a line (third one) that says 
'mjuld', this is julian date format or something of the sort. He only cared
for this one (proof of concept) but try with all three time vars. Somehow he 
wanted to "connect to the existing JSON" in sdh.py which is on port 1602 and 
read those values from it into your
server via "multicast cousnn" (box illegible), this then can be set as a 
common vairable that can also become a JSON through "multicast server". I
Don't understand why multicsting is needed as a middle step here between having
the common variables and putting them in the JSON, but maybe I can read up on 
what multicasting ACTUALLY is and how it would pertin to this situation. obvs
it's about sending to multiple clients at once, but why did he want it here?           
'''


# Old method
# try:
#     pass
#     # if value in ['true', 'false']:
#     #     value = bool(value)
#     # elif value in ['none', 'null']:
#     #     value = None
#     # elif re.search('[a-z]', value):
#     #     value = str(value)
#     # elif bool(re.match('^[0-9]+$', value)):
#     #     value = int(value)
#     # elif bool(re.match("^\d+?\.\d+?$", value)):
#     #     value = float(value)
#     # else:
#     #     flag = True
# except Exception as err:
#     print(err, " \n User gave type not found in conversion")
# finally:
