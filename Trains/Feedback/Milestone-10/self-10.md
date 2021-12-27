## Self-Evaluation Form for Milestone 10

Indicate below each bullet which file/unit takes care of each task.

The `remote proxy patterns` and `server-client` implementation calls for several
different design-implementation tasks. Point to each of the following:

1. the implementation of the `remote-proxy-player`

    With one sentence explain how it satisfies the player interface.

    **Through a TCP communication protocol, the RemotePlayerProxy is able to convert inputs provided in Player API
    method calls to JSON messages, as well as convert the output JSON received from the player/client to proprietary
    data structures that can be returned as normal.**

2. the unit tests for the `remote-proxy-player`

    Unfortunately, we were not able to get network communication with the player and thus could not write unit tests.

3. the [`server`](https://github.ccs.neu.edu/CS4500-F21/saguaro/blob/e34200ceb102af87f28ba015e0874b054221c07e/Trains/Remote/server.py) and especially the following two pieces of factored-out
   functionality:

    - [signing up enough players in at most two rounds of waiting](https://github.ccs.neu.edu/CS4500-F21/saguaro/blob/e34200ceb102af87f28ba015e0874b054221c07e/Trains/Remote/server.py#L110)
    - [signing up a single player](https://github.ccs.neu.edu/CS4500-F21/saguaro/blob/e34200ceb102af87f28ba015e0874b054221c07e/Trains/Remote/server.py#L163) (connect, check name, create proxy)

4. the [`remote-proxy-manager-referee`](https://github.ccs.neu.edu/CS4500-F21/saguaro/blob/e34200ceb102af87f28ba015e0874b054221c07e/Trains/Remote/server_proxy.py)

    With one sentence, explain how it deals with all calls from the manager and referee on the server side.

    **The ServerProxy (which is effectively a remote-proxy-manager-referee as mentioned above) takes JSON method calls received from the server, converts its arguments
    to proprietary data structures, and calls the given player method with these arguments. It then takes the object returned by this method call (if there is one), converts
    it to JSON, and sends it back to the actual server/manager/referee to be converted to the correct data server side.**

The ideal feedback for each of these three points is a GitHub
perma-link to the range of lines in a specific file or a collection of
files.

A lesser alternative is to specify paths to files and, if files are
longer than a laptop screen, positions within files are appropriate
responses.

You may wish to add a sentence that explains how you think the
specified code snippets answer the request.

If you did _not_ realize these pieces of functionality, say so.

