import yaml
import enum
import datetime
from itertools import islice

from calculator import Item, Speed

mine_count = 0
modifier = None


def all_mines():
    return yaml.load(open("constants/mines.yaml"), Loader=yaml.SafeLoader)


mines = all_mines()
elements = sorted({item
                   for entity in mines.values()
                   for item in list(entity.keys())})


class Mine:
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

    def __init__(self, area: int, level: int = 1):
        self.level = level
        self.area = area
        self.elements = mines.get(self.area)
        self.speed = self.speed_by_level[level]

    def produce_by_time(self, minutes: int):
        count = minutes * self.speed
        return [Item(el_name, int(el_value/100.0 * count))
                for el_name, el_value
                in self.elements.items()]

    def produce_for_count(self, item: Item):
        if self.elements.get(item.key) is None:
            return 0
        required_time = item.count / (self.speed * self.item_probability(item.key))
        return datetime.timedelta(minutes=required_time)

    def item_probability(self, item_name):
        if self.elements.get(item_name) is None: return 0
        return self.elements.get(item_name) / 100.0

    def get_items_speed(self):

        return [Speed(Item(el_name), speed_rpm=(self.speed * self.item_probability(el_name)))
                for el_name, el_value in self.elements.items()]


class CHEM(enum.Enum):
    sulfur = 0,
    sodium = 1,
    silicon = 2,
    nitrogen = 3


class ChemMine:
    name = "NoName"

    def __init__(self, resource: CHEM = None, level: int = 1):
        if resource is None:
            assert("Resource is empty")
        elif resource in [CHEM.sodium, CHEM.silicon, CHEM.sulfur]:
            # resources per 10 minutes as described in game UI
            self.speed_by_level = {
                1: 5,
                2: 7,
                3: 15,
                4: 20
            }
        elif resource == CHEM.nitrogen:
            # resources per 10 minutes as described in game UI
            self.speed_by_level = {
                1: 3,
                2: 4,
                3: 9,
                4: 15
            }
        self.name = resource.name
        self.level = level
        self.speed = self.speed_by_level[level]

    def get_items_speed(self):
        return [Speed(Item(self.name),
                      speed_rpm=self.speed/10.)]


def find_best_mines(item: Item,
                    mines_count: int = 1,
                    mines_level: int = 1,
                    time_minutes: (int, str) = 1440,
                    max_area: int = 120):
    if isinstance(time_minutes, str):
        time_minutes = eval(time_minutes)

    d = {area: Mine(area=area, level=mines_level).produce_by_time(time_minutes)
         for area, elements in mines.items()
         if item.key in elements.keys() and area <= max_area
         }
    filtered_by_item = {
        area: a_item.count
        for area, products in d.items()
        for a_item in products
        if a_item.key == item.key
        }
    sorted_by_count = {str(k): v
                       for k, v
                       in sorted(filtered_by_item.items(),
                                 key=lambda item: item[1],
                                 reverse=True)
                       }
    print(sorted_by_count)
    top_mines = dict(islice(sorted_by_count.items(), mines_count))
    # print(top_mines)
    return(f"Best areas for mining: {', '.join(list(top_mines.keys()))}. "
           f"You will collect {sum(top_mines.values())} "
           f"in {datetime.timedelta(minutes=time_minutes)} "
           f"by {mines_count} mines with {mines_level} lvl"
           )


if __name__ == "__main__":

    # print(f"{Mine(10, level=2).produce_by_time(100)=}")
    # print(f"{Mine(10, level=2).produce_for_count(Item('gold', 9)) =}")
    #
    # print(Mine(area=119, level=8).produce_by_time(1000))
    #
    # a = find_best_mines(
    #     item=Item('uranium'),
    #     mines_count=3,
    #     mines_level=9,
    #     time_minutes=60,
    #     max_area=110)
    # print(a)

    chem = ChemMine(resource=CHEM.nitrogen, level=3)
    print(chem.get_items_speed())
    print(chem.name, chem.speed_by_level)

    chemicals_for_dropdown=[res.name for res in CHEM]
    print(chemicals_for_dropdown, type(chemicals_for_dropdown))

