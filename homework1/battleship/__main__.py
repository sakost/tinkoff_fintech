from curses import wrapper, error as curses_error

import click

from battleship.game import Game
from battleship.player import ConsolePlayer, RandomPlayer


def get_player_name() -> str:
    """
    gets the player name from standard input and checks if its size is less than or equal to 15
    :return: player name
    :rtype: str
    """
    text = f'Please enter a name for player: '
    while len(name := input(text).strip()) > 15:
        text = 'Please enter a name with 15 or less characters: '
    if not name:
        name = 'Player'
    return name


def get_preview(game: Game) -> str:
    """
    :return: the string representation of main menu preview of the game
    :rtype: str
    """
    header_str = '#' * 49 + '\n' \
                            '#\t\tWELCOME TO BATTLESHIP\t\t#\n' + \
                 '#' * 49 + '\n'

    player_names_str = f'Player 1 name: {game.player1.name}\n' \
                       f'Player 2 name: {game.player2.name}\n'

    instruction_str = '\nPress p to play the game.' \
                      '\nPress q to quit the game.' \
                      '\nPress l to load the game state from file.\n'

    winner_str = f'{game.winner.name} is the winner of this game! Congrats!\n' if game.winner else ''

    return header_str + player_names_str + winner_str + instruction_str


def play(screen, n: int, k: int, player_name: str) -> None:
    """
    main game loop
    """
    # Clear screen
    screen.clear()
    # Initialize the game
    game = Game(screen, n, k)

    game.player1 = ConsolePlayer(player_name, screen)
    game.player2 = RandomPlayer()

    while True:
        preview = get_preview(game)

        game.change_terminal_size_message(screen, preview)

        screen.clear()
        screen.addstr(0, 0, preview)
        screen.refresh()

        c = screen.getch()
        if c == ord('q'):
            # quit the game
            break
        elif c == ord('p'):
            # play game
            game.restart()
            game.loop()
        elif c == ord('l'):
            # load game from file
            try:
                game.load()
            except curses_error:
                screen.clear()
                screen.addstr(0, 0, 'Couldn\'t load the game.\nPress any key to continue...')
                screen.getch()
                continue
            # run game
            game.loop()


def check_grid_side(ctx, param, value: int) -> int:
    """
    check the size of the grid
    :type value: int
    """
    if value < 5:
        raise ValueError("all sides of grid must be at least 5")
    return value


@click.command()
@click.argument('n', default=10, type=int, callback=check_grid_side)
@click.argument('k', default=10, type=int, callback=check_grid_side)
def main(n: int, k: int) -> None:
    player1_name = get_player_name()

    wrapper(play, n, k, player1_name)


if __name__ == '__main__':
    main()
