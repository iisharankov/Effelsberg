import socketserver
import threading
import time
import json
import re


dict = {}

class MyUDPHandler(socketserver.BaseRequestHandler):
    """
    The request handler class the server.
    """

    def setup(self):
        print("Incoming message")

    def handle(self):
        # self.request is the UDP connected to the client
        print(self.request)

        # takes message, decodes to string and removes all whitespace
        self.data = ''.join(self.request[0].decode('utf-8').lower().split())

        socket = self.request[1]
        cur_thread = threading.current_thread()

        print("{} wrote this on thread {}".format(self.client_address[0],
                                                  cur_thread.name))


        # just send back the same data, but upper-cased
        time.sleep(.1)


        if self.data.startswith('variable:'):
            self.data = self.data.replace('variable:', '')

            try:
                # self.data is in form "variable=value", so check there is 1 "="
                assert self.data.count("=") <= 1
            except AssertionError:
                msg = "More than one equals sign in message"

            else:
                # If 1 =  sign, then we know something is being set
                if self.data.count("=") == 1:
                    
                    # Replace = with : to parse into temp JSON
                    self.data = self.data.replace('=', ':')
                    varName, value = self.data.split(':', 1)

                    """
                    This is a clever trick. Above we grabbed both sides of the 
                    equal sign, one side being the varName, the other side
                    being a value. Problem is we don't know what the type is 
                    of the value. Of course it's a string as that's what the 
                    user input, but maybe they input "7" and meant the int 7, or
                    "7.0" as a float, or "[2, 3]" as a list. if we 
                    type("[2, 3]") we get a string, not a list. This can be 
                    solved weakly with many if statements. Instead, we 
                    use the below messy line to set up varName and value into a
                    string that has the *exact* format needed to parse it into a
                    temporary JSON. Basically, we use a temp JSON to serialize
                    the value, and the serialization will calculate the correct
                    type for the value (int, str, float, bool, list), then we 
                    index the tempjson for the one value it has, and this time
                    insted of getting '"7"' (a string with a 7 in it), we get 
                    '7' (the int 7). Now we have the true value and the 
                    varName, and we can use this to put the real value into
                    the final JSON object!
                    """
                    
                    # The ugly line that sets up the varName and value (both 
                    # strings) into a larger string of the correct format
                    data = "{" + '"' + varName + '":' + value + "}"
                    print(f"the varName is {varName} and the value is {value}")
                    
                    # Now load this correct data string into a tempjson
                    tempjson = json.loads(data)  # this will serialize the value
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
                    
                    # Now call the value of the varName in the JSON dict
                    trueValue = tempjson[varName]
                    print(trueValue, type(trueValue))
                    
                    # Now add to the real dictionary the trueValue and varName!
                    dict[varName] = trueValue
                    msg = f"Variable {varName} set to {trueValue}"
                    # And like that, we found the true type() of the
                    # contents of a string

                # if no = sign, then user is asking for value of varName given
                else:
                    assert self.data.count("=") == 0
                    varName = self.data
                    if varName in dict:
                        print(varName)
                        msg = 'The set value for {} is ' \
                              '{}'.format(varName, {dict[varName]})
                    else:
                        msg = f"{varName} was not found/was never set"

        # Called if user wants to see full JSON object
        elif self.data == 'returnvariables':
            msg = json.dumps(dict)
            print(msg)

        # Invalid input by user
        else:
            msg = f"{self.data} is not a valid input"

        # Message to return to client
        socket.sendto(msg.encode(), self.client_address)

    def finish(self):
        print("End of message.")


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
        # Exit the server thread when the main thread terminates
        server_thread.daemon = True
        server_thread.start()
        print("Server loop running in thread:", server_thread.name)

        #
    # Activate the server; this will keep running until you
    # interrupt the program with Ctrl-C
        server.serve_forever()



'''
Ivan
Wake up

First you should make a JSON string that holds several variables that could
be accessed by telnet. For example
effelsberg:setavx 4
effelsberg:Boolian = True
effelsberg: x = "string"
etc.

Just proof of concept that you can get commands to change variables stored
in the server, and then output that JSON (non-mutable) for usage outside the
server.

Part two will be harder. Go into sdh.py (/opt/operatorguis/VMEDisplay/sdh.py)
where just under the GUI section line you have a line (third one) that says 
'mjuld', this is julian date format or something of the sort. He only cared
for this one (proof of concept) but try with all three time vars. Somehow he 
wanted to "connect to the existing JSON" in sdh.py which is on port 
1601 or 1602 or 1604, you get the idea, and read those values from it into your
server via "multicast cousnn" (box illegible), this then can be set as a 
common vairable that can also become a JSON through "multicast server". I
Don't understand why multicsting is needed as a middle step here between having
the common variables and putting them in the JSON, but maybe I can read up on 
what multicasting ACTUALLY is and how it would pertin to this situation. obvs
it's about sending to multiple clients at once, but why did he want it here?

Biggest issue in all this is understanding what he meant as to how to connect 
and read the "existing JSON" which is in sdh.py into my server. But that's your
problem, future Ivan. 


        # obsprefix = ''
        # if 'EFFELSBERG:' in self.data:
        #     obsprefix = 'EFFELSBERG:'
        # 
        # # This triggers the instrumentServer
        # if 'INSTRUMENTSERVER:ACTIVERX?' in self.data:
        #     activeRx = 'NORX'
        #     self.reply = obsprefix + f'INSTRUMENTSERVER:ACTIVERX {activeRx} ' \
        #                         f'{time.strftime("%FT%T%z", time.gmtime())}'
        
        
        
'''