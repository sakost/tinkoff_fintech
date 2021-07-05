import curses
import pickle
from typing import Optional

from battleship.exceptions import PlayersNotSetException
from battleship.grid import Grid
from battleship.player import AbstractPlayer
from battleship.utils import ShotStatus, MoveStatus


class Game:
    """
    The core of the application
    The instance must be only one
    Manages main elements of the application
    """

    def __init__(self, screen, n: int, k: int):
        """
        Initialize game instance
        :param screen is the curses screen to draw on
        :param n is the height of playing field
        :param k is the width of playing field
        """
        self._screen = screen
        self._kn = k, n

        self._grid1 = Grid(*self._kn)
        self._grid2 = Grid(*self._kn)

        self._player1: Optional[AbstractPlayer] = None
        self._player2: Optional[AbstractPlayer] = None

        self._winner: Optional[AbstractPlayer] = None

    @property
    def player1(self) -> AbstractPlayer:
        return self._player1

    @player1.setter
    def player1(self, value: AbstractPlayer):
        if not isinstance(value, AbstractPlayer):
            raise TypeError('value must be an instance of subclass of `AbstractPlayer`')
        self._player1 = value

    @property
    def player2(self) -> AbstractPlayer:
        return self._player2

    @player2.setter
    def player2(self, value: AbstractPlayer):
        if not isinstance(value, AbstractPlayer):
            raise TypeError('value must be an instance of subclass of `AbstractPlayer`')
        self._player2 = value

    @property
    def winner(self) -> Optional[AbstractPlayer]:
        return self._winner

    def restart(self):
        self._winner = None
        self._grid1 = Grid(*self._kn)
        self._grid2 = Grid(*self._kn)

    def loop(self, index: int = 0) -> None:
        if self._player1 is None and self._player2 is None:
            raise PlayersNotSetException("players must not be None")

        # players place ships to their grids
        self.player1.place_ships(self._grid1)
        self.player2.place_ships(self._grid2)

        # to prettify code
        player_list = [self.player1, self.player2]
        player_index = index

        grid_list = [self._grid1, self._grid2]

        while True:
            # if winner is determined exit game loop
            if self.winner:
                break

            # just another clear
            self._screen.clear()

            # some variables for better code reading
            cur_player_index = player_index % 2
            next_player_index = (cur_player_index + 1) % 2
            cur_grid = grid_list[cur_player_index]
            opponent_grid = grid_list[next_player_index]
            cur_player = player_list[cur_player_index]

            # if some player lost exit the loop
            while not self._lost(opponent_grid):
                # "my" field
                field_not_op = cur_grid.make_field(for_opponent=False)
                # opponent field
                field_op = opponent_grid.make_field(for_opponent=True)

                # let player to choose the move
                move, coord = cur_player.make_move(field_op, field_not_op, cur_grid)

                # if player want to exit the game...
                if move == MoveStatus.EXIT_GAME:
                    return
                # ...or save the game
                elif move == MoveStatus.SAVE_GAME:
                    self.save(player_index)

                # do shot to opponent grid
                status = opponent_grid.shot(coord)
                # if it misses, change the player
                if status == ShotStatus.MISS:
                    break
            else:
                # if someone loses, determine winner and exit to main menu
                self._winner = cur_player
                break
            # swap players
            player_index += 1

    def save(self, index: int) -> None:
        """
        Saves the state of the game to the file
        Filename is prompted from the user through console
        :param index: is the index of playing player
        :type index: int
        """
        try:
            # prompting filename
            path = self._get_filename('Enter a filename to save(with *.pkl extension):')
            with open(path, 'wb') as file:
                # dump all data
                pickle.dump([self._grid1, self._grid2, index], file)
        except:
            # in case of error just print some message
            self._screen.clear()
            self._screen.addstr(0, 0, 'Couldn\'t save the game.\nPress any key to continue...')
            self._screen.getch()

    def load(self) -> int:
        """
        Loads the state of the game from the given through user input filename
        :return: the index of player to move
        :rtype: int
        """
        # get filename
        path = self._get_filename('Enter a filename with a save of the game(with *.pkl extension):')
        with open(path, 'rb') as file:
            # loads the state
            self._grid1, self._grid2, index = pickle.load(file)
            # reset winner
            self._winner = None
        return index

    def _get_filename(self, prompt: str) -> str:
        """

        :param prompt: prompt to print before user input
        :type prompt: str
        :return: the string which user typed
        :rtype: str
        """
        # clear the screen and print the prompt
        self._screen.clear()
        self._screen.addstr(0, 0, prompt.strip() + '\n')
        # to make sure all is okay
        self._screen.refresh()
        # enable the echo of typing characters
        curses.echo(True)
        try:
            # get the string from user through curses method
            return self._screen.getstr()
        finally:
            # disable the echo of typing characters
            curses.noecho()

    @staticmethod
    def _lost(grid: Grid) -> bool:
        """
        :param grid: the player grid(a.k.a. field)
        :type grid: Grid
        :return: whether the player lost the game
        :rtype: bool
        """
        for ship in grid.ships:
            if not ship.is_destroyed:
                return False
        return True

    @staticmethod
    def check_terminal_size(screen_size: tuple[int, int], string: str) -> bool:
        """
        check if the text fits into the size of terminal
        :param screen_size: the size of the terminal screen
        :type screen_size: tuple
        :param string: string to display after this method
        :type string: str
        :return: whether the text fits into the size of terminal
        :rtype: bool
        """
        screen_height, screen_width = screen_size

        lines = string.splitlines()
        if len(lines) > screen_height:
            return False
        if len(max(lines, key=len)) > screen_width:
            return False
        return True

    @staticmethod
    def change_terminal_size_message(screen, text: str):
        """
        prints the message of requiring size increase while `check_terminal_size` returns False
        :param screen: screen to check
        :type screen:
        :param text: text to display later
        :type text: str
        """
        first = True
        while not Game.check_terminal_size(screen.getmaxyx(), text):
            if first:
                screen.clear()
                screen.addstr(0, 0, 'Please make your terminal screen larger.')
                first = False
            screen.refresh()
