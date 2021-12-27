import sys
sys.path.append('../../../')

import unittest
from Trains.Common.map import City, Connection, Color, Destination, Map


class TestColors(unittest.TestCase):
    def test_enum_equality(self):
        self.assertEqual(Color.RED, Color.RED)
        self.assertNotEqual(Color.RED, Color.BLUE)


class TestCities(unittest.TestCase):
    def test_constructor(self):
        boston = City("Boston", 70, 80)
        new_york = City("New York", 60, 70)

        self.assertEqual(boston.name, "Boston")
        self.assertEqual(boston.x, 70)
        self.assertEqual(boston.y, 80)

        self.assertEqual(new_york.name, "New York")
        self.assertEqual(new_york.x, 60)
        self.assertEqual(new_york.y, 70)

    def test_invalid_constructor_x_too_small(self):
        with self.assertRaises(ValueError):
            City("Boston", -1, 34)
    
    def test_invalid_constructor_y_too_small(self):
        with self.assertRaises(ValueError):
            City("Boston", 44, -3)

    def test_invalid_constructor_both_too_small(self):
        with self.assertRaises(ValueError):
            City("Boston", -3, -3)

    def test_city_as_json(self):
        boston = City("Boston", 70, 80)
        self.assertEqual(boston.get_as_json(), "[\"Boston\", [70, 80]]")


class TestConnections(unittest.TestCase):
    def setUp(self):
        self.boston = City("Boston", 70, 80)
        self.new_york = City("New York", 60, 70)
        self.philadelphia = City("Philadelphia", 60, 70)
        self.connection1 = Connection(frozenset({self.boston, self.new_york}), Color.BLUE, 3)

    def test_constructor(self):
        boston = City("Boston", 70, 80)
        new_york = City("New York", 60, 70)
        test_connection = Connection(frozenset({boston, new_york}), Color.BLUE, 3)

        self.assertEqual(test_connection.cities, {new_york, boston})
        self.assertEqual(test_connection.color, Color.BLUE)
        self.assertEqual(test_connection.length, 3)

    def test_invalid_constructor_invalid_length(self):
        with self.assertRaises(ValueError):
            Connection({self.boston, self.new_york}, Color.RED, 6)

    def test_invalid_constructor_invalid_color(self):
        with self.assertRaises(ValueError):
            Connection({self.boston, self.new_york}, "RED", 3)

    def test_invalid_constructor_too_few_cities(self):
        with self.assertRaises(ValueError):
            Connection({self.boston}, Color.RED, 3)

    def test_invalid_constructor_too_many_cities(self):
        with self.assertRaises(ValueError):
            Connection({self.boston, self.new_york, self.philadelphia}, Color.RED, 3)

    def test_invalid_constructor_repeated_city(self):
        with self.assertRaises(ValueError):
            Connection({self.boston, self.boston}, Color.RED, 3)

    def test_invalid_constructor_invalid_cities_type(self):
        with self.assertRaises(ValueError):
            Connection([self.boston, self.new_york], Color.RED, 3)

    def test_connection_as_json(self):
        self.assertEqual(self.connection1.get_as_json(), "[\"Boston\", \"New York\", \"blue\", 3]")


class TestDestination(unittest.TestCase):
    def test_valid_constructor(self):
        boston = City("Boston", 70, 80)
        new_york = City("New York", 60, 70)
        philadelphia = City("Philadelphia", 60, 70)
        test_destination = Destination(frozenset({boston, new_york}))

        self.assertIn(boston, test_destination)
        self.assertIn(new_york, test_destination)
        self.assertNotIn(philadelphia, test_destination)

    def test_invalid_constructor_noncity(self):
        with self.assertRaises(ValueError):
            Destination(frozenset({2, 3}))

    def test_invalid_constructor_too_few_cities(self):
        boston = City("Boston", 70, 80)
        with self.assertRaises(ValueError):
            Destination(frozenset({boston}))

    def test_invalid_constructor_too_many_cities(self):
        boston = City("Boston", 70, 80)
        new_york = City("New York", 60, 70)
        philadelphia = City("Philadelphia", 60, 70)
        with self.assertRaises(ValueError):
            Destination(frozenset({boston, new_york, philadelphia}))

    def test_invalid_constructor_repeat_city(self):
        boston = City("Boston", 70, 80)
        with self.assertRaises(ValueError):
            Destination(frozenset({boston, boston}))

    def test_invalid_constructor_invalid_cities_type(self):
        boston = City("Boston", 70, 80)
        new_york = City("New York", 60, 70)
        with self.assertRaises(ValueError):
            Destination(frozenset({"city1": boston, "city2": new_york}))

    def test_special_case_constructor_list_cities(self):
        # This is a special case because it's technically a set and game_state needs it
        boston = City("Boston", 70, 80)
        new_york = City("New York", 60, 70)
        test_dest = Destination([boston, new_york])
        self.assertIn(boston, test_dest)
        self.assertIn(new_york, test_dest)


    def test_destination_as_json(self):
        boston = City("Boston", 70, 80)
        new_york = City("New York", 60, 70)
        test_destination = Destination(frozenset({boston, new_york}))

        self.assertEqual(test_destination.get_as_json(), "[\"Boston\", \"New York\"]")


class TestMap(unittest.TestCase):
    def setUp(self):
        self.boston = City("Boston", 70, 80)
        self.new_york = City("New York", 60, 70)
        self.philadelphia = City("Philadelphia", 60, 70)
        self.los_angeles = City("Los Angeles", 0, 10)
        self.austin = City("Austin", 50, 15)
        self.wdc = City("Washington D.C.", 55, 60)
        self.connection1 = Connection(frozenset({self.boston, self.new_york}), Color.BLUE, 3)
        self.connection2 = Connection(frozenset({self.philadelphia, self.new_york}), Color.RED, 3)
        self.connection3 = Connection(frozenset({self.boston, self.philadelphia}), Color.GREEN, 4)
        self.connection4 = Connection(frozenset({self.austin, self.los_angeles}), Color.WHITE, 5)
        self.connection5 = Connection(frozenset({self.wdc, self.philadelphia}), Color.WHITE, 5)

        self.cities = {self.boston, self.new_york, self.philadelphia}
        self.connections = {self.connection1, self.connection2, self.connection3}
        self.test_map = Map(self.cities, self.connections)

    def test_constructor(self):
        boston = City("Boston", 70, 80)
        new_york = City("New York", 60, 70)
        philadelphia = City("Philadelphia", 60, 70)
        connection1 = Connection(frozenset({boston, new_york}), Color.BLUE, 3)
        connection2 = Connection(frozenset({philadelphia, new_york}), Color.RED, 3)
        connection3 = Connection(frozenset({boston, philadelphia}), Color.GREEN, 4)

        cities = {boston, new_york, philadelphia}
        connections = {connection1, connection2, connection3}
        test_map = Map(cities, connections, 500, 500)

        self.assertEqual(test_map.cities, cities)
        self.assertEqual(test_map.connections, connections)
        self.assertEqual(test_map.width, 500)
        self.assertEqual(test_map.height, 500)

    def test_constructor_defaults(self):
        boston = City("Boston", 70, 80)
        new_york = City("New York", 60, 70)
        philadelphia = City("Philadelphia", 60, 70)
        connection1 = Connection(frozenset({boston, new_york}), Color.BLUE, 3)
        connection2 = Connection(frozenset({philadelphia, new_york}), Color.RED, 3)
        connection3 = Connection(frozenset({boston, philadelphia}), Color.GREEN, 4)

        cities = {boston, new_york, philadelphia}
        connections = {connection1, connection2, connection3}
        test_map = Map(cities, connections)

        self.assertEqual(test_map.cities, cities)
        self.assertEqual(test_map.connections, connections)
        self.assertEqual(test_map.width, 800)
        self.assertEqual(test_map.height, 800)

    def test_constructor_extra_city_in_cities(self):
        test_map = Map({self.boston, self.new_york, self.philadelphia}, {self.connection1})
        for city in self.connection1.cities:
            self.assertIn(city, test_map.cities)

    def test_constructor_extra_city_in_connections(self):
        with self.assertRaises(ValueError):
            Map({self.boston, self.new_york}, {self.connection1, self.connection2})

    def test_constructor_extra_city_in_repeated_connections(self):
        with self.assertRaises(ValueError):
            Map({self.boston, self.new_york, self.philadelphia}, [self.connection1, self.connection2, self.connection2])

    def test_invalid_constructor_invalid_cities_type(self):
        with self.assertRaises(ValueError):
            Map([self.boston, self.new_york, self.philadelphia], {self.connection1, self.connection2})

    def test_invalid_constructor_invalid_connections_type(self):
        with self.assertRaises(ValueError):
            Map([self.boston, self.new_york, self.philadelphia], [self.connection1, self.connection2])

    def test_get_copy_of_map(self):
        map_copy = self.test_map.get_copy_of_map()
        self.assertTrue(map_copy == self.test_map)

    def test_get_city_names(self):
        names1 = {"Boston", "New York", "Philadelphia"}
        names2 = {"New York", "Philadelphia", "Boston"}

        self.assertEqual(self.test_map.get_city_names(), names1)
        self.assertEqual(self.test_map.get_city_names(), names2)

    def test_get_cities_from_connections_multiple_connections(self):
        self.assertEqual(self.test_map.get_cities_from_connections({self.connection1, self.connection2}), {self.boston, self.new_york, self.philadelphia})

    def test_get_cities_from_connections(self):
        self.assertEqual(self.test_map.get_cities_from_connections({self.connection1}), {self.boston, self.new_york})

    def test_get_all_cities(self):
        self.assertEqual(self.test_map.get_all_cities(), {self.boston, self.new_york, self.philadelphia})

    def test_get_all_cities_no_cities(self):
        test_map = Map(set(), set(), 500, 500)
        self.assertEqual(test_map.get_all_cities(), set())

    def test_get_all_connections(self):
        self.assertEqual(self.test_map.get_all_connections(), {self.connection1, self.connection2, self.connection3})

    def test_get_all_connections_no_connections(self):
        test_map = Map(self.cities, set(), 500, 500)
        self.assertEqual(test_map.get_all_connections(), set())

    def test_get_all_terminal_cities_from_city_direct(self):
        self.assertEqual(set(self.test_map.get_all_terminal_cities_from_city(self.boston, self.test_map.connections)), {self.new_york, self.philadelphia})

    def test_get_all_terminal_cities_from_city_indirect_all_connected(self):
        cities = {self.boston, self.new_york, self.philadelphia, self.wdc}
        connections = {self.connection1, self.connection2, self.connection3, self.connection5}
        test_map = Map(cities, connections)
        self.assertEqual(set(test_map.get_all_terminal_cities_from_city(self.boston, test_map.connections)), {self.new_york, self.philadelphia, self.wdc})

    def test_get_all_terminal_cities_from_city_indirect_not_all_connected(self):
        cities = {self.boston, self.new_york, self.philadelphia, self.wdc, self.los_angeles, self.austin}
        connections = {self.connection1, self.connection2, self.connection3, self.connection4, self.connection5}
        test_map = Map(cities, connections)
        self.assertEqual(set(test_map.get_all_terminal_cities_from_city(self.boston, test_map.connections)), {self.new_york, self.philadelphia, self.wdc})

    def test_get_feasible_destinations_simple(self):
        dest1 = Destination({self.new_york, self.philadelphia})
        dest2 = Destination({self.new_york, self.boston})
        dest3 = Destination({self.boston, self.philadelphia})

        self.assertEqual(self.test_map.get_feasible_destinations(self.test_map.connections),
                         {dest1, dest2, dest3})

    def test_get_feasible_destinations_disjoint_connections(self):
        dest1 = Destination({self.new_york, self.philadelphia})
        dest2 = Destination({self.new_york, self.boston})
        dest3 = Destination({self.boston, self.philadelphia})
        dest4 = Destination({self.los_angeles, self.austin})
        dest5 = Destination({self.new_york, self.wdc})
        dest6 = Destination({self.boston, self.wdc})
        dest7 = Destination({self.wdc, self.philadelphia})

        self.connections.add(self.connection4)
        self.connections.add(self.connection5)
        self.assertEqual(self.test_map.get_feasible_destinations(self.test_map.connections),
                         {dest1, dest2, dest3, dest4, dest5, dest6, dest7})

    def test_get_map_as_json(self):
        cities = {self.boston, self.new_york}
        connections = {self.connection1}
        test_map = Map(cities, connections)

        self.assertEqual(test_map.get_as_json(), "{\"cities\": [{\"name\": \"Boston\", \"x\": 70, \"y\": 80}, {\"name\": \"New York\", \"x\": 60, \"y\": 70}], \"connections\": [{\"cities\": [{\"name\": \"Boston\", \"x\": 70, \"y\": 80}, {\"name\": \"New York\", \"x\": 60, \"y\": 70}], \"color\": 2, \"length\": 3}], \"height\": 800, \"width\": 800}")


if __name__ == '__main__':
    unittest.main()
