import socketserver
import threading
import logging
import socket
import struct
import time
import json
import re

dict = {}


def add_variable(variable_name, value):
    """
    :param variable_name: str - name of the variable user wants to add to JSON
    :param value: str - value of variable in a string. Read below.
    :return: str- Message to return to user. Function also adds value to global
                  json dictionary

    Above we grabbed both sides of the equal sign (variable_name and value),
    but we don't know what the type is of the value. Of course it's a string,
    as that's what input returns, but maybe they input "7" and meant the int 7,
    or "7.0" as a float, or "[2, 3]" as a list. if we type("[2, 3]") we get a
    string, not a list. This can be solved weakly with many if statements.
    Instead, we use the below line to set up variable_name and value into a
    string that has the *exact* format needed to parse it into a temporary JSON.
    Basically, we use a temp JSON to serialize the value, and the serialization
    will calculate the correct type for the value (int, str, float, bool, list),
    then we index the tempjson for the one value it has, and this time instead
    of getting '"7"' (a string with a 7 in it), we get '7' (the int 7). Now we
    have the true value and the variable_name, and we can use this to put the
    real value into the final JSON object.
    """

    # Rplaces single quotes with double quotes from the value var.
    value = value.replace("'", '"')
    # I'm amazed ('"', "'")  does not violate PEP-8...

    # Sets up the variable_name and value (both strings)  into a larger string
    # of the correct format to parse into a json.loads
    data = '{' + '"' + variable_name + '":' + value + '}'

    # Now load this correct data string into a tempjson
    # Todo: add a try-except on loads for bad values like one quote not two used
    tempjson = json.loads(data)  # this will serialize the value

    # Now call the value of the variable_name in the JSON jsondict
    true_value = tempjson[variable_name]
    print(f'Value of {variable_name} is "{true_value}" and the type of the '
          f'value is {type(true_value)}')

    # Now add to the real dictionary the true_value and variable_name!
    dict[variable_name] = true_value
    msg = f"Variable {variable_name} set to {true_value}"
    return msg
    # And like that, we found the true type() of the contents of a string


def return_variable(requested_var):
    if requested_var in dict:
        print(requested_var)
        # TODO Bug: this next line fails for returning lists, unhashable
        msg = 'The set value for {} is ' \
              '{}'.format(requested_var, {dict[requested_var]})
        return msg
    else:
        msg = f"{requested_var} was not found/was never set"
        return msg


# Communication class
class MyUDPHandler(socketserver.BaseRequestHandler):
    """
    The request handler class the server.
    """

    def setup(self):
        pass
        # print("Incoming message")

    def handle(self):
        # self.request is the UDP connected to the client

        # takes message, decodes to string and - all whitespace (by rejoining)
        telnet_msg = ''.join(self.request[0].decode('utf-8').lower().split())

        cur_thread = threading.current_thread()
        print(f"{self.client_address[0]} wrote this on "
              f"thread {cur_thread.name}")

        if telnet_msg.startswith('variable:'):
            telnet_msg = telnet_msg.replace('variable:', '')

            try:
                # telnet_msg is in form "variable=value" or "variable", so
                # check there is one or no "=" signs
                assert telnet_msg.count("=") <= 1

            except AssertionError:
                msg = "More than one equals sign in message. Don't assert."

            else:
                # If 1 =  sign, then we know something is being set
                if telnet_msg.count("=") == 1:
                    # Replace = with : to parse into temp JSON
                    variable_name, value = telnet_msg.split('=', 1)
                    msg = add_variable(variable_name, value)
                   
                # if no "=" sign, then user wants value of variable_name given
                else:
                    assert telnet_msg.count("=") == 0  # Should never fail
                    msg = return_variable(telnet_msg)

        # Called if user wants to see full JSON object
        elif telnet_msg == 'returnvariables':
            msg = json.dumps(dict)
            print(msg)
        
        # Checks if the telnet_msg is in the multicast strings
        elif telnet_msg in multicastdata:

            # Finds the location of the variable in the multicast message
            loc = multicastdata.find(telnet_msg)
            multicast_var = (multicastdata[loc:loc+50])

            # Format to remove everything after comma, and remove a quote
            multicast_var = multicast_var.replace('"', '').split(",", 1)[0]
            msg = multicast_var

        # Invalid input by user
        else:
            msg = f"{telnet_msg} is not a valid input or not recognized"

        # Message to return to client
        print(f"Sending message: {msg}")
        returnsocket = self.request[1]
        returnsocket.sendto(msg.encode(), self.client_address)

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

        mcast_group = '***REMOVED***'
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
