
# Proxy Server in Python

This is a simple proxy server written in Python that can handle HTTP requests. It can be used to intercept, modify, or forward HTTP traffic between a client and a server.

## Features

- Supports caching of web pages locally in file system for faster access
- Supports logging of requests and responses
- Supports domain blocking to filter out unwanted websites
- Supports concurrency to handle multiple connections simultaneously

## Implementation

The proxy server is implemented as a single Python script (`proxy.py`) that uses the `socket` module to create and manage TCP connections. The main logic of the proxy server is as follows:

The proxy server creates a listening socket on the specified port and waits for incoming connections. 
When there is a connection, the proxy server creates a new thread to handle the client request. There are a specified number of threads which are joined/freed as the connections are closed. 
The proxy server parses the HTTP request and extracts the method, URL, protocol, headers, and body of the request. 
The proxy server then checks if the URL matches a domain (via regular expressions) in the list of blocked domains (which is a text file, by default `blocked.txt`). If a match is found, it sends back a blocked domain (by default `blocked.html`) response to the client and closes the connection.
If a match is not found the proxy server checks if the URL (hashed) is in the cache (`cache.txt`). If there is a cache hit, it reads the cached response from the file and sends it back to the client. 
If there is a cache miss, the proxy server adds the URL (hashed) to the cache along with the web resources from that request and sends the web resources to the client.

## Testing

The proxy server was tested using a web browsers (Firefox), where the browser was configured to use the local running proxy server. The following scenarios were tested:

- Normal browsing: The proxy server was able to handle GET and POST requests for various websites such as Google, Wikipedia, YouTube, etc. and display them correctly in the web browser. This was tested simply by navigating to different websites using the configured browser with the proxy server running locally.
- Caching: The proxy server was able to cache responses for GET requests for static web pages and serve them from the cache when requested again. This was tested by navigating to a website for the first time and revisiting the website to make sure that the proxy server will send cached resources. The cached resources were also inspected to ensure that the server was properly caching the resources.
- Domain blocking: The proxy server was able to block requests for websites that were in the blocked list (`blocked.txt`) and send back the `blocked.html` response to the client. This was tested by navigating to URLs that would match the domains in the blocked domain list and ensuring that the `blocked.html` page was displayed in the browser in the place of the actual webpage.
- Concurrency: The proxy server was able to handle multiple connection requests simultaneously from different clients using threading.

## Reflection

In this project, I learned how to implement a basic proxy server in Python that can perform various functions such as caching, domain blocking, and concurrency. This was a good exercise to understand how web proxies work and how they utilize caching and concurrency to improve throughput and performance.
