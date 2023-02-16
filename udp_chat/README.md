# UDP Chat Server
This is a Python implementation of a simple chat server using the User Datagram Protocol (UDP) with the following features: Simultaneous client connection, message broadcast to all connected clients, custom commands.

## Design and Implementation
The server maintains a hashmap `cobj` to store the address tuple of each client as the key and a unique nickname generated (the script generates unique nicknames for each client by combining random ASCII letters) and assigned to each client as the value. The server listens for incoming messages and broadcasts the messages to all connected clients.

The script has methods to handle custom commands from the clients: 
* `/nick` for changing the client's nickname
* `/list` for displaying the list of connected clients
* `/quit` for disconnecting the client from the chat server. 

## Usage
The script does not use any external libraries, only built-in Python libraries hence the script can be executed by using the following command:
```
python server.py [port_number]
```
The script does require an argument `port_number` which is the port number that the server will listen on.

## Operation
Given below are a few examples of how to test this script. Before creating a client ensure that the server is running
```
python3 server.py 12000
```
Once the server is started on a certain port (in this case 12000). We can create and spawn simple clients. Clients can be created using Python or any other relevant programming language however for testing we are creating clients using [Netcat](https://netcat.sourceforge.net/).
```
nc -u localhost 12000
```
This can be repeated a number of times to create multiple simultaneous clients. Given below are some of the client-server back and forth messages to show how the server functions.
```
initial message
TEDDC: initial message
/nick client
new nickname set TEDDC->client
hello
client: hello
/list
showing connected clients: 127.0.0.1:55265:xxHPr, 127.0.0.1:55274:Tyvem, 127.0.0.1:55278:client
/quit
you have been disconnected.
```
Similarly, another simultaneous client will see this:
```
initial message
Tyvem: initial message
TEDDC: initial message
TEDDC changed their nickname to client
client: hello
client queried connected client list
client has disconnected.
```
