Pair: saguaro

Commit: [`e34200`](https://github.ccs.neu.edu/CS4500-F21/saguaro/tree/e34200ceb102af87f28ba015e0874b054221c07e) 

Score: 48/100

Grader: Chukwurah Somtoo


20/20: accurate self eval

28/80

1. 8/20 pts for `remote-proxy-player` implementation satisfying the player interface

2. 8/20 pts for unit tests of `remote-proxy-player`:

   - Does it come with unit tests for all methods
     (start, setup, pick, play, more, win, end)?

3. 4/20 pts for separating the `server` function (at least) into the following two pieces of functionality:
   - signing up enough players in at most two rounds of waiting, with a different requirement for a min number of players
   - signing up a single player: which requires three steps: connect, check name, create remote-proxy player
   - First function lacks a purpose statement and it looks like its the wrong function. The second function dosent have the required steps.

4. 8/20 pts for implementing `remote-proxy-manager-referee` to the manager and referee interfaces.
