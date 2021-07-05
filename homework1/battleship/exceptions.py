class BattleshipException(Exception):
    pass


class PlayersNotSetException(BattleshipException):
    pass


class InvalidCoordinateException(BattleshipException):
    pass


class CantPlaceShipException(BattleshipException):
    pass
