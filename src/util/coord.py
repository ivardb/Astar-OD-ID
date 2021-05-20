class Coord:
    __slots__ = ("x", "y")

    def __init__(self, x: int, y: int):
        """
        Create a coordinate.
        :param x: The x position
        :param y: The y position
        """
        self.x = x
        self.y = y

    def move(self, dx, dy):
        """
        Create a new coordinate moved in the given direction.
        :param dx: The x direction to move
        :param dy: The y direction to move
        :return: A new moved coordinate
        """
        return Coord(self.x + dx, self.y + dy)

    def __hash__(self) -> int:
        return tuple.__hash__((self.x, self.y))

    def __eq__(self, other):
        return (self.x, self.y) == (other.x, other.y)

    def __iter__(self):
        yield self.x
        yield self.y