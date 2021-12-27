MAX_MESSAGE_SIZE = 20000 # Number of bytes we read on each reader.read() call.
# reader.read() will read a specifed number of bytes, or until the end of file is reached.
# The end of file is only reached when the writer is closed, so we read a finite amount of bytes