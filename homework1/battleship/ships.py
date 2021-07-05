from typing import Union

from battleship.exceptions import InvalidCoordinateException
from battleship.utils import Coordinate, Rotation


class Ship:
    """
    this class represents the ship
    """

    def __init__(self, ship_size: int, head_coord: Coordinate, rotation: Rotation):
        self._size = ship_size
        self._head_coord = head_coord
        self._rotation = rotation
        self._coords: frozenset[Coordinate] = frozenset()

        self._update_coords()

        self._damaged_cells: set[Coordinate] = set()

    @property
    def coordinates(self) -> frozenset[Coordinate]:
        """
        :return: precached coordinates of the ship(including damaged)
        :rtype: frozenset
        """
        return self._coords

    @property
    def damaged_cells(self) -> frozenset[Coordinate]:
        """
        :return: damaged cells of the ship
        :rtype: frozenset
        """
        return frozenset(self._damaged_cells)

    @property
    def damaged(self) -> bool:
        """
        check if the ship was damaged
        """
        return len(self._damaged_cells) > 0

    @property
    def is_destroyed(self) -> bool:
        """
        check if the ship was destroyed at all
        """
        return self._coords == self.damaged_cells

    def is_intersect(self, coord: Union[Coordinate, frozenset[Coordinate]]) -> bool:
        """
        check if given coordinates(or coordinate) intersect with this ship
        :param coord: coordinate(s) of cells to check intersection
        :rtype: bool
        """
        if isinstance(coord, Coordinate):
            coord = frozenset((Coordinate,))
        return len(self._coords.intersection(coord)) > 0

    def _update_coords(self):
        """
        updates the cached coordinates of ship
        """
        x, y = self._head_coord.x, self._head_coord.y
        dx, dy = 0, 0
        if self._rotation == Rotation.HORIZONTAL:
            dx = 1
        elif self._rotation == Rotation.VERTICAL:
            dy = 1
        else:
            raise RuntimeError("unknown rotation parameter")
        self._coords = frozenset(Coordinate(x + dx * i, y + dy * i) for i in range(self._size))

    def shot(self, coord: Coordinate):
        """
        make shot to the coord
        can raise InvalidCoordinateException
        :param coord: the coord to shot
        :type coord: Coordinate
        """
        if coord not in self._coords:
            raise InvalidCoordinateException(f"given coordinate is invalid")
        self._damaged_cells.add(coord)
