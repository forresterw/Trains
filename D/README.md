# D - GUI #
Takes in a well-formed and valid JSON object from STDIN that contains the specification for a small graph.  The program then renders the points from the input as small black dots an orange canvas of the specified size, and draws red lines from every point to every other, distinct point.  The popup window with the drawing of the graph is displayed for 3 seconds and then shuts down.

--- 

## Usage ##
Run 'make' in the D directory.

### Example: ###

The contents of the well-formed, valid JSON object:
```console
{\"nodes\": [[20,15],[100,120],[50,10],[90,180]],\"size\": 200}
```
The "nodes" field is a JSON array of points that are represented by a JSON array of two integers between 0 and the size specified in the "size" field.

Using the 'xgui' program to render the graph of a well-formed, valid JSON object:
```console
$ echo {\"nodes\": [[20,15],[100,120],[50,10],[90,180]],\"size\": 200} | ./xgui
```
In this example, the command takes the JSON object as input through STDIN, draws the specified graph to the orange canvas that is displayed in a pop up window for 3 seconds.

Nothing is printed to STDOUT

---

## Structure and File Descriptions ##
### Makefile ###
Gives 'xgui' executable permissions.

### xgui ###
Entry point for the program that contains the python implementation of functionality described above.

Utilizes the 'sys' module, 'json' module, and the classes 'Tk' and 'Canvas' from the 'tkinter' module, which are all a part of the Python Standard Library.  

---