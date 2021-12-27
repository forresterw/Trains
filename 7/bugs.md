# Bugs found in Clean-up

-   The referee game state unit test `test_verify_legal_connection_invalid_not_enough_colored_cards` is misrepresented. It is actually passing due to insufficient number of rails instead of what the test name suggests (colored_cards).

    -   [Bad Unit Test](https://github.ccs.neu.edu/CS4500-F21/lassen/blob/eae0d98d19ce93f1710118546b83db66fb705de6/Trains/Other/Unit_Tests/game_state_tests.py#L115)
    -   [Added Unit Test](https://github.ccs.neu.edu/CS4500-F21/lassen/blob/e22ceba46676a08e5048888cc87f38f8a5d4c9c1/Trains/Other/Unit_Tests/referee_game_state_tests.py#L113)

-   Referee previously did not update its game state when getting an updated state to send to the player. Unit test previously did not catch this, but does now.

    -   [Bad Unit Test](https://github.ccs.neu.edu/CS4500-F21/lassen/blob/d2e1d05abf9cf95438caf1a65c8bf5548767a5e8/Trains/Other/Unit_Tests/referee_test.py#L261)
    -   [New Unit Test](https://github.ccs.neu.edu/CS4500-F21/lassen/blob/6f23881dcd7ffdbcb3d6583a3f6b8ded52e05866/Trains/Other/Unit_Tests/referee_test.py#L316)

-   RefereeGameState was not correctly detecting unchanged state over a single round.

    -   Missing Unit Test | [Old Functionality](https://github.ccs.neu.edu/CS4500-F21/lassen/blob/e22ceba46676a08e5048888cc87f38f8a5d4c9c1/Trains/Admin/referee_game_state.py#L81)
    -   [New Functionality](https://github.ccs.neu.edu/CS4500-F21/lassen/blob/1195fd930d2543ccd7a8fa935c0f1f74ec02886a/Trains/Admin/referee_game_state.py#L71) | [New Unit Test](https://github.ccs.neu.edu/CS4500-F21/lassen/blob/1195fd930d2543ccd7a8fa935c0f1f74ec02886a/Trains/Other/Unit_Tests/referee_game_state_tests.py#L210)

-   Referee would not end the game if there was only player remaining (in the case of kicking other players).

    -   [New Unit Test](https://github.ccs.neu.edu/CS4500-F21/lassen/blob/1195fd930d2543ccd7a8fa935c0f1f74ec02886a/Trains/Other/Unit_Tests/referee_test.py#L499)

-   RefereeGameState equality referred to a deck field that did not exist

    -   Missing Unit Test | [Old Functionality](https://github.ccs.neu.edu/CS4500-F21/lassen/blob/e22ceba46676a08e5048888cc87f38f8a5d4c9c1/Trains/Admin/referee_game_state.py#L50)
    -   [New Unit Test](https://github.ccs.neu.edu/CS4500-F21/lassen/blob/1195fd930d2543ccd7a8fa935c0f1f74ec02886a/Trains/Other/Unit_Tests/referee_game_state_tests.py#L226) | [New Functionality](https://github.ccs.neu.edu/CS4500-F21/lassen/blob/1195fd930d2543ccd7a8fa935c0f1f74ec02886a/Trains/Admin/referee_game_state.py#L50)

-   Missing integration test on referee's main game loop.

    -   [New Integration Test](https://github.ccs.neu.edu/CS4500-F21/lassen/blob/1195fd930d2543ccd7a8fa935c0f1f74ec02886a/Trains/Other/Unit_Tests/referee_test.py#L488)

-   No integration testing when a player is banned.

    -   [New Integration Test](https://github.ccs.neu.edu/CS4500-F21/lassen/blob/1195fd930d2543ccd7a8fa935c0f1f74ec02886a/Trains/Other/Unit_Tests/referee_test.py#L499)

-   PlayerGameState does not allow more than 45 rails (not guaranteed if rules change) or more than 50 cards of each color in the players hand upon construction.

    -   [Deleted Rails Unit Test](https://github.ccs.neu.edu/CS4500-F21/lassen/blob/d2e1d05abf9cf95438caf1a65c8bf5548767a5e8/Trains/Other/Unit_Tests/player_game_state_tests.py#L65)
    -   [Deleted Cards Unit Test](https://github.ccs.neu.edu/CS4500-F21/lassen/blob/d2e1d05abf9cf95438caf1a65c8bf5548767a5e8/Trains/Other/Unit_Tests/player_game_state_tests.py#L56)

-   Missing a unit test for getting the number of colored cards in the player game state.

    -   [New Unit Test - Cards in hand](https://github.ccs.neu.edu/CS4500-F21/lassen/blob/1195fd930d2543ccd7a8fa935c0f1f74ec02886a/Trains/Other/Unit_Tests/player_game_state_tests.py#L72)
    -   [New Unit Test - No cards](https://github.ccs.neu.edu/CS4500-F21/lassen/blob/1195fd930d2543ccd7a8fa935c0f1f74ec02886a/Trains/Other/Unit_Tests/player_game_state_tests.py#L75)

-   Initial player hands were not always initialized with all colors in the case of not having any cards of a certain color

    -   [New Functionality](https://github.ccs.neu.edu/CS4500-F21/lassen/blob/1195fd930d2543ccd7a8fa935c0f1f74ec02886a/Trains/Admin/referee.py#L174-L176)
