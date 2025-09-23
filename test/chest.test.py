from debug import test_structure

from vesperia_types import ChestItemEntry

def to_bytes():
    chest_item: ChestItemEntry = ChestItemEntry(17, 1)

    test_structure(chest_item)

if __name__ == "__main__":
    to_bytes()