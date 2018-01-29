from enum import IntEnum

__all__ =[
    'ArrangeMode', 'DuplicateAction'
]
class ArrangeMode(IntEnum):
    COPY = 1
    MOVE = 2
    NA = 0xFF

    def __str__(self):
        return self.name

    @classmethod
    def from_str(cls, str):
        str = str.lower()
        if str == 'copy':
            return cls.COPY
        elif str == 'move':
            return cls.MOVE
        else:
            return cls.NA

class DuplicateAction(IntEnum):
    SKIP = 1
    DROP = 2
    MOVE = 3
    NA = 0xFF

    def __str__(self):
        return self.name

    @classmethod
    def from_str(cls, str):
        str = str.lower()
        if str == 'skip':
            return cls.SKIP
        elif str == 'drop':
            return cls.DROP
        elif str == 'move':
            return cls.MOVE
        else:
            return cls.NA

