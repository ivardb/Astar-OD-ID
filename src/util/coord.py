class Coord:
    __slots__ = ("x", "y")

    def __init__(self, x: int, y: int):
        self.x = x
        self.y = y

    def move(self, dx, dy):
        return Coord(self.x + dx, self.y + dy)

    def __hash__(self) -> int:
        return self.x << 16 | self.y
        #return tuple.__hash__((self.x, self.y))

    def __eq__(self, other):
        return (self.x, self.y) == (other.x, other.y)

    def __iter__(self):
        yield self.x
        yield self.y