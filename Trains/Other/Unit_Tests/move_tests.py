import unittest, sys
sys.path.append('../../../')
from Trains.Common.map import Connection, City, Color
from Trains.Player.moves import MoveType, NoAvailableMove, DrawCardMove, AcquireConnectionMove


class TestPlayerMove(unittest.TestCase):
    def test_move_enum(self):
        self.assertEqual(MoveType.NO_MOVE.value, 0)
        self.assertEqual(MoveType.DRAW_CARDS.value, 1)
        self.assertEqual(MoveType.ACQUIRE_CONNECTION.value, 2)

    def test_move_types(self):
        boston = City("Boston", 70, 20)
        new_york = City("New York", 60, 30)
        conn1 = Connection(frozenset({boston, new_york}), Color.BLUE, 5)
        no_move = NoAvailableMove()
        draw_move = DrawCardMove()
        acquire_move = AcquireConnectionMove(conn1)

        self.assertEqual(no_move.move_type, MoveType.NO_MOVE)
        self.assertEqual(str(no_move), "No possible move")

        self.assertEqual(draw_move.move_type, MoveType.DRAW_CARDS)
        self.assertEqual(str(draw_move), "Draw 2 cards")

        self.assertEqual(acquire_move.move_type, MoveType.ACQUIRE_CONNECTION)
        self.assertEqual(acquire_move.connection, conn1)
        self.assertIn(str(acquire_move), ["Attempt to acquire Connection(cities=frozenset({City(name='Boston', x=70, y=20), City(name='New York', x=60, y=30)}), color=<Color.BLUE: 2>, length=5)", "Attempt to acquire Connection(cities=frozenset({City(name='New York', x=60, y=30), City(name='Boston', x=70, y=20)}), color=<Color.BLUE: 2>, length=5)"])

        # Invalid input
        with self.assertRaises(ValueError):
            AcquireConnectionMove(boston)


if __name__ == '__main__':
    unittest.main()