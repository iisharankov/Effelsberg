import socketserver
import threading
import logging
import socket
import struct
import json

dict_ = {}  # Temporary, will get to this fix later

def main():
    destination_address = (LOCAL_ADDRESS, UDPTELNET_PORT)

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

        # Activate the server; this will keep running until you
        # interrupt the program with Ctrl-C
        server.serve_forever()


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

        command = CommandModule(telnet_msg)
        msg = command.return_message()

        # Message to return to client
        print(f"Sending message: {msg}")
        returnsocket = self.request[1]
        returnsocket.sendto(msg.encode(), self.client_address)

    def finish(self):
        pass
        # print("End of message.")


class CommandModule:
    """
    Instantiating this class takes a string and parses it to return the correct
    response to the user
    """

    def __init__(self, command_message):
        """
        :param command_message: str - message to parse
        """
        self.command = command_message
        self.msg = ''
        self.multicastdata = sdh_multicast()
        self.probe_command()

    def probe_command(self):
        # Checks what is in the string, and calls the correct method
        if self.command.startswith('variable:'):
            self.new_variable()

        elif self.command.startswith('returnvariables'):
            self.return_variables_in_json()

        elif self.command in self.multicastdata:
            self.multicast_variable()

        else:
            string = f"{self.command} is not a valid input or not recognized"
            self.set_message(string)

    def new_variable(self):
        self.command = self.command.replace('variable:', '')

        try:
            # telnet_msg is in form "variable=value" or "variable", so
            # check there is one or no "=" signs
            assert self.command.count("=") <= 1

        except AssertionError:
            string = "More than one equals sign in message. Don't assert."
            self.set_message(string)

        else:
            # If 1 =  sign, then we know something is being set
            if self.command.count("=") == 1:
                # Replace = with : to parse into temp JSON
                variable_name, value = self.command.split('=', 1)
                string = add_variable(variable_name, value)
                self.set_message(string)

            # if no "=" sign, then user wants value of variable_name given
            else:
                assert self.command.count("=") == 0  # Should never fail
                self.return_variable()

    def return_variable(self):
        if self.command in dict_:

            string = f'The set value for {self.command} ' \
                     f'is {dict_[self.command]}'
            self.set_message(string)

        else:
            string = f"{self.command} was not found/was never set"
            self.set_message(string)

    def return_variables_in_json(self):
        string = json.dumps(dict_)
        self.set_message(string)

    def multicast_variable(self):
        # Finds the location of the variable in the multicast message
        loc = self.multicastdata.find(self.command)
        # takes a bit more on the right side than needed. This is trimmed next
        multicast_var = (self.multicastdata[loc:loc + 50])

        # Format to remove everything after comma, and remove a quote
        multicast_var = multicast_var.replace('"', '').split(",", 1)[0]
        self.set_message(multicast_var)

    def set_message(self, string):
        self.msg = string

    def return_message(self):
        return self.msg


class ThreadingUDPServer(socketserver.ThreadingMixIn, socketserver.UDPServer):
    pass


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
    # I'm amazed ('"', "'")  does not violate PEP-8 somehow...

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
    dict_[variable_name] = true_value
    msg = f"Variable {variable_name} set to {true_value}"
    return msg
    # And like that, we found the true type() of the contents of a string


def sdh_multicast():
    # Currently this opens a multicast port just to get the multicastdata
    # and then closes to save the resource. Can change to always open if needed
    server_address = ('', SDH_PORT_READING)  # sdh json
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind(server_address)
    group = socket.inet_aton(MULTICAST_GROUP)
    mreq = struct.pack('4sL', group, socket.INADDR_ANY)
    sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)
    multicastdata_bytes, address = sock.recvfrom(300000)
    sock.close()
    return str(multicastdata_bytes)


if __name__ == "__main__":

    # Constants
    UDPTELNET_PORT = ***REMOVED***
    SDH_PORT_READING = 1602
    LOCAL_ADDRESS = '***REMOVED***'
    MULTICAST_GROUP = ***REMOVED***

    main()
