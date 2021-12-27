from inspect import isclass
import sys, os
from importlib.util import spec_from_file_location, module_from_spec

sys.path.append('../../')
from Trains.Player.player import AbstractPlayer
from Trains.Player.strategy import AbstractPlayerStrategy


class DynamicPlayer(AbstractPlayer):
    """
    A player that implements a dynamically loaded strategy.
    Sources:
        https://stackoverflow.com/questions/67631/how-to-import-a-module-given-the-full-path?rq=1
        https://stackoverflow.com/questions/1796180/how-can-i-get-a-list-of-all-classes-within-current-module-in-python
    """
    def __init__(self, name: str, age: int, path: str):
        """
        Dynamically loads a strategy from a given file path to create a player
        Uses the AbstractPlayer class constructor.
            Parameters:
                name (str): player name
                age (int): player age
                path (str): file path of strategy to load
        """
        # Get absolute file path
        abs_path = os.path.abspath(path)
        # Get file name from absolute path
        file_name = os.path.basename(abs_path)
        # Format file name (remove .py)
        if file_name[-3::] == ".py":
            file_name = file_name[0:-3]
        # Get module from file path
        spec = spec_from_file_location(file_name, abs_path)
        module = module_from_spec(spec)
        spec.loader.exec_module(module)

        super().__init__(name, age)
        # Initializes player with strategy from file path
        self.strategy = self.get_strategy(module)

    def get_strategy(self, module):
        """
        Creates an instance of a strategy object from a given module
            Parameters:
                module: Module to dynamically load strategy from
            Returns:
                An instance of a strategy object found in the given module
        """
        strategy_class_instance = None
        # Iterate through names of the given module's elements (includes imported classes)
        # TODO: Do we need to verify python file for Strategy?
        seen_implementations = []
        for class_name in dir(module):
            if isclass(getattr(module, class_name)) and issubclass(getattr(module, class_name), AbstractPlayerStrategy) \
                and class_name != AbstractPlayerStrategy.__name__:
                check_class = getattr(module, class_name)
                check_class_instance = check_class.__new__(check_class)
                # Set it only if we have not seen a previous concrete implementation
                # or the class subclasses that concrete implementation.
                if strategy_class_instance is None or issubclass(check_class_instance.__class__, strategy_class_instance.__class__):
                    strategy_class_instance = check_class_instance
                    seen_implementations.append(check_class_instance)
        return strategy_class_instance
