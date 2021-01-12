import yaml
import datetime
import enum
from itertools import islice
from typing import NewType, Sequence

from calculator import Item

mine_count = 0
modifier = None


def all_mines():
    mines = yaml.load(open("mines.yaml"), Loader=yaml.SafeLoader)
    # print(mines)
    return mines


mines = all_mines()
elements = sorted({item
                   for entity in mines.values()
                   for item in list(entity.keys())})

speed_by_level = {
    # PBM - Pieces By Minute
    1: 3,
    2: 4,
    3: 5,
    4: 6,
    5: 8,
    6: 12,
    7: 15,
    8: 17,
    9: 20
    }


class Mine:
    def __init__(self, area: int, level: int = 1):
        self.level = level
        self.area = area
        self.elements = mines.get(self.area)

        self.speed = speed_by_level[level]

    def produce_by_time(self, minutes: int):
        count = minutes * self.speed
        return [Item(el_name, int(el_value/100.0 * count))
                for el_name, el_value
                in self.elements.items()]

    def produce_for_count(self, item: Item):
        if self.elements.get(item.name) is None:
            return 0
        item_probability = self.elements.get(item.name) / 100.0
        required_time = item.count / (self.speed * item_probability)
        return datetime.timedelta(minutes=required_time)


def find_best_mines(item: Item,
                    mines_count: int = 1,
                    mines_level: int = 1,
                    time_minutes: int = 1000):
    d = { area: Mine(area=area, level=mines_level).produce_by_time(time_minutes)
            for area, elements in mines.items()
            if item.name in elements.keys()
        }
    filtered_by_item = {
        area: a_item.count
         for area, products in d.items()
         for a_item in products
         if a_item.name == item.name
        }
    sorted_by_count = {str(k): v
           for k, v
           in sorted(filtered_by_item.items(), key=lambda item: item[1], reverse=True)
           }
    # print(sorted_by_count)
    top_mines = dict(islice(sorted_by_count.items(), mines_count))
    # print(top_mines)
    return(f"Best areas for mining: {', '.join(list(top_mines.keys()))}. "
          f"You will collect {sum(top_mines.values())} "
          f"in {datetime.timedelta(minutes=time_minutes)} "
          f"by {mines_count} mines with {mines_level} lvl"
        )


if __name__ == "__main__":
    print(Mine(10, level=2).produce_by_time(100))
    print(Mine(10, level=2).produce_for_count(Item("gold", 9)))

    print(Mine(area=119, level=8).produce_by_time(1000))

    a = find_best_mines(
        item=Item('uranium'),
        mines_count=3,
        mines_level=9,
        time_minutes=60)
    print(a)