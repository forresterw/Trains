# E - TCP #
Allows a single TCP client connection that consumes a series of [well-formed](https://www.json.org/json-en.html) and valid JSON from the client.  The word "valid" meaning there are no JSON oddities in the fields or values, and that Strings are non-empty, composed of lowercase alphabetical characters [a-z], and do not exceed 10 characters.  The inputted JSON are [reversed](https://github.ccs.neu.edu/CS4500-F21/boise/blob/master/C/README.md) using [C/xjson](https://github.ccs.neu.edu/CS4500-F21/boise/blob/master/C/xjson) before being delivered to the output side of the TCP connection.  The server shuts down once the connection is closed. Additionally, the program has a 3 second timeout, so it will signal an error and shut down if no client connects within that time.  

The program accepts a single, optional command-line argument to specify the port on which the server accepts connections, and has a default port of 45678 if not port is specified.  A specified port number must fall within the range [2048, 65535].

--- 

## Usage ##
Run 'make' in the E directory.

### Example: ###

The contents of a single well-formed JSON from the Tests/1-in.json file:
```console
$ cat Tests/1-in.json
{"name": "bill", "age": 26, "vals": [null, true, false, 54.8, -34], "sub_object": {"other": "value", "and": 45, "also": true}}
```
Using the xtcp program to establish a connection, recieve the contents of the 1-in.json file, reverse it and deliver the reversed version:  

First establish the server by running xtcp:  
This example was run with a command-line argument that specifies the port, 8888, for xtcp to accept connections on
```console
$ ./xtcp 8888
```
This example was run locally, so the ip address 127.0.0.1 is used.
```console
$ cat Tests/1-in.json | nc 127.0.0.1 8888
{"name": "llib", "age": -26, "vals": [34, -54.8, true, false, null], "sub_object": {"other": "eulav", "and": -45, "also": false}}
```
The command takes in the well-formed JSON 1-in.json from the client through netcat, reverses all fields, delivers the result back to the client and shuts down.

The reversed JSON that the client receives is printed to STDOUT via netcat.

---

## Structure and File Descriptions ##
### Makefile ###
Gives xtcp executable permissions.

### xtcp ###
Entry point for the program that reuses [C/xjson](https://github.ccs.neu.edu/CS4500-F21/boise/blob/master/C/xjson) via the subprocess module to provide the python implementation of the functionality described above.

Utilizes the sys, json, and asyncio modules, which are all in the Python Standard Library

### Tests/ ###
This directory contains JSON files that are used in xtest to compare the expected output JSON and the actual output JSON received from xtcp. 

The in files are well-formed JSON that contain field values to exhaustively test the program's functionality.

---