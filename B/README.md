# B - The Very Basics #
Uses piped-in terminal commands as STDIN input and prints a command-line-specified number of lines to STDOUT.

--- 

## Usage ##
Run 'make' in the B directory.

### Example: ###
```console
$ ls -l / | ./xhead -6
total 7472  
drwxr-xr-x  1 PC 197610       0 Aug 23 17:47 bin/  
drwxr-xr-x  1 PC 197610       0 Aug 23 17:48 cmd/  
drwxr-xr-x  1 PC 197610       0 Aug 23 17:47 dev/  
drwxr-xr-x  1 PC 197610       0 Aug 23 17:48 etc/  
-rwxr-xr-x  1 PC 197610  137232 Aug 17 09:40 git-bash.exe*  
```
In the example above, the command pipes the output of 'ls -l /' into xhead with the argument '-6' to indicate how many lines should be printed.  
The result will is the first 6 lines of the root of the file system being printed to STDOUT

---

## Special Character Cases ##
There are special characters in a Bash shell that, when added to the command-line arugment, appear as malformed arguments for xhead, but still produce the expected output.
### Example: ###
```console
$ ls -l / | ./xhead -\6
total 7472  
drwxr-xr-x  1 PC 197610       0 Aug 23 17:47 bin/  
drwxr-xr-x  1 PC 197610       0 Aug 23 17:48 cmd/  
drwxr-xr-x  1 PC 197610       0 Aug 23 17:47 dev/  
drwxr-xr-x  1 PC 197610       0 Aug 23 17:48 etc/  
-rwxr-xr-x  1 PC 197610  137232 Aug 17 09:40 git-bash.exe*  
```
This is an example of the Bash escape character '\\' being present in the command-line argument '-\6' and functioning properly even though '\6' it is not a natural number.  This is a special case, because the escape character preserves the value of the character that follows, and '6' is a valid input.

This is also true for single quotes
```console
$ ls -l / | ./xhead -'6'
```
and double quotes
```console
$ ls -l / | ./xhead -"6"
```
because they both preserve the literal value of the characters inside the quotes.

Documentation Source:  
https://www.gnu.org/software/bash/manual/html_node/Quoting.html

---

## Structure and File Descriptions ## 
### Makefile ###
Gives xhead and xtest executable permissions.

### xhead ###
Entry point for the program that contains the python implementation of functionality described above.

Utilizes the 'sys' module from the Python Standard Library. 
### xtest ###
Contains tests for the following cases:
- Correct four file test equal arg
- Correct four file test larger arg
- Correct four file test smaller arg
- Malformed 0 arg
- Missing arg
- Malformed string arg
- Malformed negative num arg
- Malformed decimal num arg
- Malformed number no arg dash
- Malformed string no arg dash
- Malformed too many args  

Utilizes the 'subprocess' module from the Python Standard Library.  

---