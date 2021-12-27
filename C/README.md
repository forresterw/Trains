# C - JSON #
Takes in [well-formed](https://www.json.org/json-en.html) JSON from STDIN and delivers an equally long JSON to STDOUT with every field reversed.

## Meaning of Reverse ##

| type of JSON value |                  meaning of "reverse"                  |
|:------------------:|:------------------------------------------------------:|
|       String       |             reverse characters in a string             |
|       Number       |               [-](https://bit.ly/3EooCuN)              |
|       object       |            reverse per field as appropriate            |
|        array       | reverse the array and reverse per  slot as appropriate |
|       Boolean      |              [not](https://bit.ly/2XsuK4k)             |
|        null        |           [identity](https://bit.ly/3EoDs4s)           |

--- 

## Usage ##
Run 'make' in the C directory.

### Example: ###

The contents of the well-formed '1-in.json' file:
```console
$ cat Tests/1-in.json
{"name": "bill", "age": 26, "vals": [null, true, false, 54.8, -34], "sub_object": {"other": "value", "and": 45, "also": true}}
```
Using the 'xjson' program to reverse the contents of the '1-in.json' file:
```console
$ cat Tests/1-in.json | ./xjson
{"name": "llib", "age": -26, "vals": [34, -54.8, true, false, null], "sub_object": {"other": "eulav", "and": -45, "also": false}}
```
In this example, the command takes in the well-formed JSON '1-in.json' through STDIN and reverses all fields in accordance with the "Meaning of Reverse" section above.  

The result is the reversed JSON being printed to STDOUT.

---

## Structure and File Descriptions ##
### Makefile ###
Gives 'xjson' and 'xtest' executable permissions.

### xjson ###
Entry point for the program that contains the python implementation of functionality described above.

Utilizes the 'sys' module and 'json' module from the Python Standard Library.  Also uses the 'reverse_json_value' function from our 'Other/json_operations.py' script.

### Other/json_operations.py ###
Utility file that contains the 'reverse_json_value' function, which is our implementation of the 'reverse' operation that is applied to the inputted JSON.  The function returns an equally long, reversed JSON by following the guidelines established in the "Meaning of Reverse" section. 

Utilizes 'Number' from the 'numbers' module in the Python Standard Library.

### xtest ###
Contains tests for 'xjson' that use sample input JSON files, 'x-in.json' to compare the program output to the expected output in 'x-out.json' that is the correctly reversed version of the inputted JSON.  

Also contains unit tests for the 'reverse_json_value' function applied to the following types:
- Integer
- Float
- Negative Integer
- Negative Float
- String
- Boolean True
- Boolean False
- None/null
- Array of Ints
- Array of Strings
- Object
- Nested Object

Utilizes the 'subprocess' module from the Python Standard Library, and the 'reverse_json_value' function from 'Other/json_operations.py'.  

### Tests/ ###
This directory contains three pairs of JSON files that are used in 'xtest' to compare the expected output JSON and the actual output JSON. 

File pairs:
- '1-in.json' and '1-out.json':  
- '2-in.json' and '2-out.json'  
- '3-in.json' and '3-out.json'

The 'in' files are well-formed JSON that contain field values to exhaustively test the program's functionality.  For example, '2-in.json' has an intentionally complex structure with a list of lists where one of the lists contains a list of objects, which also have their own sublists and subobjects.

---