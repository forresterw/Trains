from typing import List, Tuple
import sys
from Trains.Common.map import City
sys.path.append('../../../')
from Trains.Player.player import PlayerInterface

# For Graph Use in Referee (Longest Path)
Edge = Tuple[City, City]

# Game Types
PlayerScore = Tuple[PlayerInterface, int]
GameRank = List[PlayerScore]
GameRankings = List[GameRank]
Cheaters = List[PlayerInterface]
GameResult = Tuple[GameRankings, Cheaters]

# Tournament Types (Includes some Game Types)
GameAssignment = List[PlayerInterface]
TournamentWinners = List[PlayerInterface]
TournmentResult = Tuple[TournamentWinners, Cheaters]