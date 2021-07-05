import curses
import random
from abc import ABC, abstractmethod
from collections import OrderedDict
from copy import deepcopy
from typing import Optional

# this manner was used due to cycle import problem
import battleship.game
from battleship.grid import Grid
from battleship.ships import Ship
from battleship.utils import Rotation, Coordinate, MoveStatus


class AbstractPlayer(ABC):
    """
    An abstract class for all players
    """

    def __init__(self):
        self._name = None

    @abstractmethod
    def make_move(self,
                  field_op: list[list[str]], field_not_op: list[list[str]],
                  grid: Grid) -> tuple[MoveStatus, Optional[Coordinate]]:
        """
        makes all interaction operations with user and ask him/her to choose the move
        :param field_op: the field of opponent
        :type field_op: list
        :param field_not_op: the field of current player
        :type field_not_op: list
        :param grid: the grid of current player
        :type grid: Grid
        :return: the tuple of MoveStatus and, in case of MoveStatus.MOVEMENT, the Coordinate where to move
        :rtype: tuple
        """
        return NotImplemented

    @property
    def name(self):
        return str(self._name)

    @name.setter
    def name(self, value):
        self._name = value

    # I hope this would work
    @staticmethod
    def place_ships(grid: Grid):
        """
        randomly places all ships to the grid
        :param grid: player grid
        :type grid: Grid
        """
        # from the biggest ship to the smallest ship
        for ship_length, ship_count in reversed(OrderedDict(grid.ship_counts).items()):
            # add ship by its count
            for i in range(ship_count):
                # while not success
                while True:
                    # change some parameters randomly
                    rotation = random.choice([Rotation.HORIZONTAL, Rotation.VERTICAL])
                    max_x = grid.size.width - 1
                    max_y = grid.size.height - 1
                    # consider the chosen rotation and ship length
                    if rotation is Rotation.HORIZONTAL:
                        max_x -= ship_length
                    elif rotation is Rotation.VERTICAL:
                        max_y -= ship_length
                    else:
                        raise RuntimeError(f"unknown rotation")

                    # randomize coordinates
                    x = random.randrange(max_x)
                    y = random.randrange(max_y)

                    ship = Ship(ship_length, Coordinate(x, y), rotation)

                    # check whether it worked
                    if grid.place_ship(ship):
                        # if yope just go to the next ship
                        break


class ConsolePlayer(AbstractPlayer):
    """
    the class to interact with player via console
    """

    def __init__(self, name: str, screen):
        super().__init__()
        self.name = name
        self._screen = screen

    def make_move(self,
                  field_op: list[list[str]], field_not_op: list[list[str]],
                  grid: Grid) -> tuple[MoveStatus, Optional[Coordinate]]:
        # command char
        ch = None

        # coordinates to move
        x, y = 0, 0
        # while not pressed enter or 'q'
        while ch != ord('\n') and ch != ord('q'):
            # deepcopy to prevent the overriding of original player field
            field = deepcopy(field_op)
            field[y][x] = Grid.HERE_CHARACTER

            res_text = f'This move of player {self.name}\n'
            res_text += Grid.concat_field(field_not_op) + '\n\n'
            res_text += Grid.concat_field(field) + '\n'

            res_text += self._help_message()

            # check the size of the terminal and place text on it
            battleship.game.Game.change_terminal_size_message(self._screen, res_text)
            self._screen.clear()
            self._screen.addstr(0, 0, res_text)
            self._screen.refresh()

            # get the command from user
            ch = self._screen.getch()
            if ch == curses.KEY_LEFT:
                x = max(x - 1, 0)
            elif ch == curses.KEY_UP:
                y = max(y - 1, 0)
            elif ch == curses.KEY_DOWN:
                y = min(y + 1, grid.size.height - 1)
            elif ch == curses.KEY_RIGHT:
                x = min(x + 1, grid.size.width - 1)
            # if pressed Enter on hit cell just skip
            elif ch == ord('\n') and field_op[y][x] != Grid.EMPTY_CELL_CHARACTER:
                ch = None
            # command for saving game
            elif ch == ord('s'):
                return MoveStatus.SAVE_GAME, Coordinate(x, y)
        if ch == ord('q'):
            return MoveStatus.EXIT_GAME, None
        return MoveStatus.MOVEMENT, Coordinate(x, y)

    @staticmethod
    def _help_message() -> str:
        """
        help message at the bottom of the terminal screen
        """
        return '\nPress q to quit the game.\nPress s to save the game.\nPress Enter to choose a move.' \
               '\nUse arrows to navigate.'


class RandomPlayer(AbstractPlayer):
    """
    random player
    """

    def __init__(self):
        super().__init__()
        # name may be better but no
        self.name = "randomer"

    def make_move(self, field_op: list[list[str]], field_not_op: list[list[str]], grid: Grid) \
            -> tuple[MoveStatus, Optional[Coordinate]]:
        # fill out all available coordinates into this set
        coords_set: list[Coordinate] = []
        for num_row, row in enumerate(field_op):
            for num_col, col in enumerate(row):
                # append coordinate only if cell is empty
                if col == Grid.EMPTY_CELL_CHARACTER:
                    coords_set.append(Coordinate(num_col, num_row))
        # choice random movement
        return MoveStatus.MOVEMENT, random.choice(coords_set)
