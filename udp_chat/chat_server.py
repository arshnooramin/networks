import socket
import sys
import random
import string

class UDPChatServer:
    """
    simple udp chat server with the following features:
    - simultaneous client connection
    - message broadcast to all connected clients
    - custom commands
    """
    def __init__(self, ip, port, bufsize):
        self.cobj = dict() # client hashmap object - to save client address (key), nickname (val) pair
        self.nickset = set() # hashset of unique nicknames being used
        
        self.ssock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # server socket
        self.ssock.bind((ip, port))
        self.bufsize = bufsize
        
        # listen for keyboard interrupt to end the loop
        try:
            self.runServer()
        except KeyboardInterrupt:
            self.ssock.close()
    
    def runServer(self):
        """
        method to run the server - starts an inifinite loop
        to continously listen for messages and broadcast messages to
        connected clients
        """
        while True:
            try:
                # listen to messages from client
                data, caddr = self.ssock.recvfrom(self.bufsize)
            except ConnectionResetError:
                # if connection lost delete client
                del self.cobj[caddr]
                continue
            
            # if new client assign a new nickname add to the client hashmap
            if caddr not in self.cobj:
                self.cobj[caddr] = self.getNickname()
            
            print(f"{caddr}, {self.cobj[caddr]}: {data}")

            data = data.decode("utf-8")[:-1]

            # if the message is a command handle the command and send response to client
            if data.startswith('/nick') or data.startswith('/list') or data.startswith('/quit'):
                retstr = self.handleCommands(data, caddr) + '\n'
                for ca in self.cobj:
                    if ca != caddr:
                        self.ssock.sendto(retstr.encode("utf-8"), ca)
            
            # otherwise broadcast to connected clients
            else:
                retstr = f"{self.cobj[caddr]}: {data}\n"
                for ca in self.cobj:
                    self.ssock.sendto(retstr.encode("utf-8"), ca)
    
    def handleCommands(self, data, caddr):
        """
        handle commands from the clients
        do the requested tasks and respond to the client
        inform all the other clients of the command status
        return - cstr: response for command sending client, astr: response for all clients
        """
        cstr = '' # str for client who sent command
        astr = '' # str for all clients
        
        if data.startswith('/nick'):
            t = data.split(' ')
            if len(t) > 1:
                newnick = t[1]
                oldnick = self.cobj[caddr]
                self.cobj[caddr] = newnick
                cstr = f"new nickname set {oldnick}->{newnick}"
                astr = f"{oldnick} changed their nickname to {newnick}"
            else:
                cstr = "error - no nickname provided"
        
        if data == '/list':
            cstr = "showing connected clients: "
            astr = f"{self.cobj[caddr]} queried connected client list"
            carr = list()
            for ca in self.cobj:
                nick = self.cobj[ca]
                carr.append(ca[0] + ':' + str(ca[1]) + ':' + nick)
            cstr += ', '.join(carr)
        
        if data == '/quit':
            cstr = "you have been disconnected."
            astr = f"{self.cobj[caddr]} has disconnected."
            del self.cobj[caddr]
        
        cstr += '\n'
        self.ssock.sendto(cstr.encode("utf-8"), caddr)
        
        return astr

    def getNickname(self):
        """
        method to generate random nicknames
        ensure the nicknames are unique
        return - nick: the generated unique nickname
        """
        letters = string.ascii_letters
        nick = ''.join(random.choice(letters) for i in range(5))

        if nick in self.nickset:
            nick = self.getNickname()

        self.nickset.add(nick)
        return nick

if __name__ == "__main__":
    if len(sys.argv) < 2:
        raise ValueError("usage: [python_interpreter] chat_server.py [port_number]")

    try:
        PORT = int(sys.argv[1])
    except:
        raise ValueError("invalid port number")
    
    ucs = UDPChatServer('localhost', PORT, 1024)
