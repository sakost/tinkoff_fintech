from copy import deepcopy
from math import sqrt
from types import MappingProxyType

from battleship.exceptions import CantPlaceShipException
from battleship.ships import Ship
from battleship.utils import Size, ShotStatus, Coordinate


class Grid:
    SHIP_CHARACTER = '#'  # can be visible only at user own field
    DAMAGED_SHIP_CHARACTER = '@'
    DESTROYED_SHIP_CHARACTER = 'x'
    EMPTY_CELL_CHARACTER = '.'
    HERE_CHARACTER = 'H'  # player cursor to check cells

    def __init__(self, k: int, n: int):
        """
        :param k: the k from the statement
        :param n: the n from the statement
        """
        self._grid_size = Size(n, k)
        self._ship_counts = self._compute_ship_count(self._grid_size)

        self._ships: list[Ship] = []

    @staticmethod
    def _compute_ship_count(grid_size: Size) -> dict[int, int]:
        """
        for size of the grid calculate the count of ships of every type
        total occupied area of ships is nearly equal to 20%
        :return the dictionary of such pairs: ships_type: ships_count
        :rtype dict
        """
        counts = {}

        occupied_field_area = grid_size.height * grid_size.width // 5  # 20% of field

        # magic

        # this is a solution of equation
        # |1/6 * t**3 + 1/2 * t**2 + t/3 - occupied_field_area|, where meaning of t if explained below
        # and occupied_field_area is an area occupied by ships

        # ships of length of t is 1, of (t-1) is 2 ..., of 2 is (t-1) and of 1 is t

        # and the above equation is the count of area occupied depending on t
        x = (3 * occupied_field_area + 1 / 3 * sqrt(81 * occupied_field_area ** 2 - 1 / 3)) ** (1 / 3)
        ship_coefficient = int(
            x + 1 / (3 * x) - 1
        )

        # to avoid the overflow of ship size in case of size of grid is 100x5 or so
        ship_coefficient = min(ship_coefficient, grid_size.width // 2, grid_size.height // 2)

        for ship_size in range(1, ship_coefficient + 1):
            counts[ship_size] = ship_coefficient - ship_size + 1

        return counts

    @property
    def ship_counts(self) -> MappingProxyType[int, int]:
        # helps to avoid changing
        return MappingProxyType(self._ship_counts)

    @property
    def size(self):
        return self._grid_size

    def __len__(self) -> int:
        """
        :returns the total size of ships
        """
        return sum(self._ship_counts.values())

    def place_ship(self, ship: Ship):
        """
        places the ship into the grid
        :param ship: ship to place
        :return: whether the method could place the ship or not
        :rtype: bool
        """
        if not self.can_place_ship(ship):
            raise CantPlaceShipException()
        self._ships.append(ship)

    def can_place_ship(self, ship: Ship) -> bool:
        """
        checks opportunity to place the ship
        """
        for inner_ship in self._ships:
            # if sets intersection not empty
            if inner_ship.coordinates & ship.coordinates:
                return False
        return True

    def make_field(self, for_opponent: bool = False) -> list[list[str]]:
        """
        map the grid into the list of list of chars(a.k.a. field)
        :param for_opponent: whether this for opponent or not
        :type for_opponent: bool
        :return: the field of this grid
        :rtype: list
        """
        field = [[self.EMPTY_CELL_CHARACTER for _ in range(self.size.height)] for _ in range(self.size.width)]

        if not for_opponent:
            for ship in self._ships:
                for coord in ship.coordinates:
                    if ship.is_destroyed:
                        char = self.DESTROYED_SHIP_CHARACTER
                    elif ship.damaged and coord in ship.damaged_cells:
                        char = self.DAMAGED_SHIP_CHARACTER
                    else:
                        char = self.SHIP_CHARACTER
                    field[coord.y][coord.x] = char
        else:
            for ship in self._ships:
                # skip ship if it is intact
                if not ship.damaged and not ship.is_destroyed:
                    continue
                if ship.is_destroyed:
                    for coord in ship.coordinates:
                        field[coord.y][coord.x] = self.DESTROYED_SHIP_CHARACTER
                elif ship.damaged:
                    for coord in ship.damaged_cells:
                        field[coord.y][coord.x] = self.DAMAGED_SHIP_CHARACTER

        return field

    @staticmethod
    def concat_field(field: list[list[str]]) -> str:
        """
        concatenate the field returned by `make_field`
        :return: the resulting text
        :rtype: str
        """
        return '\n'.join(''.join(row) for row in field)

    def shot(self, coord: Coordinate) -> ShotStatus:
        """
        make a given shot to this grid
        :return: the status of shot
        :rtype: ShotStatus
        """
        for ship in self._ships:
            if coord in ship.coordinates:
                ship.shot(coord)
                if ship.is_destroyed:
                    return ShotStatus.SINK
                return ShotStatus.HIT
        return ShotStatus.MISS

    @property
    def ships(self) -> list[Ship]:
        # deepcopy to avoid changing from outside
        return deepcopy(self._ships)
