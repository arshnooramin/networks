"""
A basic web (HTTP) proxy server.
Marchiori 2023
"""

import socket
import argparse
import logging
import urllib.parse
import threading
import select
import binascii
import traceback
	
def handle_https(conn, addr, url):
	"handle a https session on the socket <conn> to the given url."
	log = logging.getLogger(__name__)
	try:
		# parse the url
		urlparts = urllib.parse.urlparse('https://' + url)
		log.debug(f"https: connecting to {urlparts.hostname}:{urlparts.port or 443}")

		# connect to the remote server, using the port specified or 443 if not specified.
		remote = socket.socket(socket.AF_INET, socket.SOCK_STREAM)		
		remote.connect((urlparts.hostname, urlparts.port or 443))

		# tell the browser we're ready
		conn.sendall(b"HTTP/1.1 200 OK\r\n\r\n")
		while True:
			# wait for data to be available on either socket
			r,w,x = select.select([conn, remote], [], [conn, remote])
			if remote in x:
				log.error("https: Error on remote socket.")
				break
			if conn in x:
				log.error("https: Error on client socket.")
				break
			
			if remote in r:
				# read from remote
				data = remote.recv(1 << 16)
				if len(data) == 0:
					log.info("https: remote closed connection.")
					break
				# send to client
				conn.sendall(data)
				#log.debug(f"https: {addr} <- {remote.getpeername()}: [{len(data)}]: {binascii.hexlify(data[:32], bytes_per_sep = 4)}")
			if conn in r:
				# read from client
				data = conn.recv(1 << 16)
				if len(data) == 0:
					log.info("https: browser closed connection.")
					break
				# send to remote
				remote.sendall(data)
				#log.debug(f"https: {addr} -> {remote.getpeername()}: [{len(data)}]: {binascii.hexlify(data[:32], bytes_per_sep = 4)}")
	except Exception as x:
		log.error(f"Error handling https session: {x}")
		traceback.print_exc()
	finally:
		try:
			# try to shutdown both sockets
			remote.shutdown(socket.SHUT_RDWR)
			remote.close()			
		except:
			# close may fail if the connection is already closed, ignore
			pass

		try:
			conn.shutdown(socket.SHUT_RDWR)
			conn.close()
		except:
			pass
	log.debug(f"https: session closed")

def do_web_method(method, url, headers, payload):
	"Get a resource from the web and return an iterator over the response."
	log = logging.getLogger(__name__)
	
	# strip leading http:// or https://
	if url.startswith('http://'):
		url = url[7:]
	elif url.startswith('https://'):
		url = url[8:]

	# parse the url, using HTTP
	urlparts = urllib.parse.urlparse('http://' + url)

	# add/overwrite connection:close to the headers, we don't support persistent connections	
	headers['Connection'] = 'close'

	log.debug(f"Sending {method} request to {urlparts.hostname}:{urlparts.port or 80} with {headers}")
	
	s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	try:
		s.connect((urlparts.hostname, urlparts.port or 80))
		
		# construct the HTTP request.
		req = [f"{method} {urlparts.path} HTTP/1.0\r\n"] 
		req += [f"{k}: {v}\r\n" for k,v in headers.items()]
		req += ["\r\n"]		
		req = ''.join(req).encode('utf-8')
		
		# send the request
		s.sendall(req)
		
		# send the payload, if any
		if payload:
			s.sendall(payload)

		# read the response
		while True:
			# read 1k at a time
			data = s.recv(1 << 10)
			#log.debug(f"got: {data}")
			if len(data) == 0:
				# end of response
				break
			yield data
	except Exception as x:
		log.error(f"Error getting resource from web: {x}")
		traceback.print_exc()
	try:
		s.shutdown(socket.SHUT_RDWR)
		s.close()
	except Exception:
		pass
		
def handle_client(s, cachedir):
	"Run the proxy server on the given socket."
	log = logging.getLogger(__name__)
	while True:
		# accept a connection
		conn, addr = s.accept()
		log.info(f"Accepted connection from {addr}.")
		
		# close connection when done?
		close_conn = True

		try:
			# read the request, if we get a partial request it will fail and we'll ignore it
			reqraw = conn.recv(1 << 16)
			req = reqraw.decode('utf-8', errors='ignore')

			log.debug(f"Reading req, got {len(req)} bytes.")
			if len(req) == 0:
				# the browser may try to open parallel connections but then close them
				# without sending any data. So we just ignore them.
				# our side of the socket will be closed by the finally block
				continue


			# headers end with \r\n\r\n. find the end of the headers
			endpos = req.find('\r\n\r\n')

			if endpos == -1:
				# no headers, ignore
				log.debug(f"No headers, ignoring request: {req[:100]}")
				continue

			# html is a list of lines in the request
			payload = reqraw[endpos+4:] # everything after the header in the raw request...
			reqhead = req[0:endpos].split('\r\n')

			log.debug(f"Parsing request: {reqhead[0]}")
			# parse the request
			method, url, version = reqhead[0].split()

			log.debug (f"got method: {method}, url: {url}, version: {version}: headers: {reqhead[1:]}")

			# extract headers and remove empty lines at the end and convert to a dict			
			headers = {k.strip():v.strip() for k,v in [x.split(":", maxsplit = 1) for x in reqhead[1:]]}
					
			# drop request to upgrade to https, if the browser is trying to do that
			if 'Upgrade-Insecure-Requests' in headers:
				del headers['Upgrade-Insecure-Requests']		

			# add or update the x-forwarded-for header
			if 'x-forwarded-for' in headers:
				# add this ip to the list of forwarded ips
				headers['x-forwarded-for'] = f"{headers['x-forwarded-for']}, {addr[0]}"
			else:
				# if there is no x-forwarded-for header, add it
				headers['x-forwarded-for'] = addr[0]

			# check the method
			if method == "GET":
				# TODO check cache
				
				# if no cache, get the resource from the web
				for chunk in do_web_method("GET", url, headers, payload):
					# TODO probably want to cache the response here
					
					# send the result to the client
					conn.send(chunk)
			elif method in ['POST', 'PUT', 'DELETE', 'PATCH', 'OPTIONS']:
				# these cannot be cached, make the same request to the server			
				for chunk in do_web_method(method, url, headers, payload):					
					# send the result to the client
					conn.send(chunk)
			elif method == "CONNECT":
				# start a new thread to handle the https connection
				threading.Thread(
					target=handle_https, 
					args=(conn, addr, url),
					name=f"HTTPS:{addr[0]}:{addr[1]}", daemon=True).start()
				
				# need to leave the	connection open
				close_conn = False
			else:
				# not supported, send our response back
				resp = "HTTP/1.0 501 Not Implemented\r\n\r\n"
				conn.send(resp.encode('utf-8'))
		except Exception as x:
			log.error(f"Error handling request: {x}")
			traceback.print_exc()
		finally:
			if close_conn:
				log.debug("Closing connection.")
				try:
					conn.shutdown(socket.SHUT_RDWR)
					conn.close()
				except OSError:
					# the client may have closed the connection already which may cause an error when we close 
					pass

if __name__ == "__main__":    
	parser = argparse.ArgumentParser(description='objcache server')
	parser.add_argument('--address', '-a', type=str, default='127.0.0.1',
			 help='IP address to listen on (default:127.0.0.1) use 0.0.0.0 for all addresses')
	parser.add_argument('--proxyport', '-p', type=int, default=8585,
			help='TCP port to listen on')
	parser.add_argument('--objaddr', type=str, default="127.0.0.1", 
			help='objcache server address (default: 127.0.0.1)')	
	parser.add_argument('--objport', type=int, default=8181, 		    
			help='objcache server port')
	parser.add_argument('--datadir', type=str, default="./cache", 
			 help='Path to cache directory')	
	parser.add_argument('--threads', '-t', type=int, default=1, 
			help='Number of threads to use')	
	args = parser.parse_args()

	# set up logging
	logging.basicConfig(level=logging.DEBUG, 
		format='%(asctime)s [%(threadName)10s] %(levelname)7s: %(message)s')
	log = logging.getLogger()

	# accept connections on a socket
	s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
	s.bind((args.address, args.proxyport))
	s.listen(200)

	log.info(f"HTTP Proxy listening on TCP port {args.proxyport}.")
	try:
		# this is a sequential server, it can only handle one client at a time.
		handle_client(s, args.datadir)
	except KeyboardInterrupt:
		log.info("<ctrl-c> Shutting down.")
	
	try:
		s.shutdown(socket.SHUT_RDWR)
		s.close()
	except:
		# try to close but ignore errors
		pass

	log.info("Goodbye.")