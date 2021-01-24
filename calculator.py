import yaml
import datetime
import enum
import uuid
from typing import  NewType, Sequence
from math import ceil

import locale
locale.setlocale(locale.LC_ALL, '')


def all_resources():
    """
    :return: dict
    """
    resources = yaml.load(open("resources.yaml"), Loader=yaml.SafeLoader)
    for item_key, item_data in resources.items():
        item_data['name'] = item_data.get('name') or item_key.replace("_", " ").title()
    sorted_dict = {key: resources[key] for key in sorted(resources.keys())}
    return sorted_dict


resources = all_resources()


def recipes_by_operation() -> dict:
    global resources
    resources = all_resources()
    recipes_by_op = {}
    for recipe_key, recipe_data in resources.items():
        for key, value in recipe_data.items():
            operation = key.title()
            if operation not in [building.name for building in BUILDING]:
                continue
            if recipes_by_op.get(operation) is None:
                recipes_by_op[operation] = dict()
            recipes_by_op[operation][recipe_key] = recipe_data["name"]
    return recipes_by_op


class BUILDING(enum.Enum):
    Smelting = 0
    Chemistry = 1
    Crafting = 2
    Planting = 3
    Jewelling = 4


class Building:
    def speed(self):
        pass


class Item:
    def __init__(self, key, count=1):
        self.exists = bool(resources.get(key))
        self.key = key
        self.name = resources.get(key).get("name") if self.exists else key.replace("_", " ").title()
        self.count = count
        self.uuid = str(uuid.uuid4())

    def is_simple(self):
        """
        Doesn't require ingredients
        :return: bool
        """
        return not self.exists

    def __repr__(self):
        if self.count > int(self.count):
            count = int(self.count) + 1
        else:
            count = int(self.count)
        return f"{self.name} x {count:n}"

    def __mul__(self, number: int):
        return Item(self.key, self.count * number)

    def rpm(self, time_sec):
        return Speed(item=self,
                     time_sec=time_sec)


class Speed:
    def __init__(self,
                 item: Item,
                 time_sec: (datetime.timedelta, int) = None,
                 speed_rpm: float = None):
        defined_vars = [i for i in [item.count, time_sec, speed_rpm] if i is not None]
        if defined_vars.__len__() < 2:
            # raise BaseException(
            print(
                f"Need at least 2 parameters to initialize Speed(). "
                f"We got {[item.count, time_sec, speed_rpm]=}")
        self.item = item
        self._quantity = item.count
        if isinstance(time_sec, float): time_sec = int(time_sec)
        if isinstance(time_sec, int):
            self._time = datetime.timedelta(seconds=time_sec)
        elif isinstance(time_sec, datetime.timedelta):
            self._time = time_sec
            assert self._time.total_seconds() > 0
        else:
            self._time = time_sec
        self._speed = speed_rpm

    @property
    def quantity(self):
        if self._quantity is not None: return self._quantity
        return ceil(self._speed * (self._time.total_seconds() // 60))

    @property
    def time(self):
        if self._time is not None: return self._time
        return datetime.timedelta(minutes=int(self._quantity / self._speed))

    @property
    def speed(self):
        if self._speed is not None: return self._speed
        speed = self._quantity / (self._time.total_seconds() / 60)
        return round(speed, 3)

    def set(self, name, value):
        self.__setattr__(name, value)
        return self

    def __add__(self, other):
        return Speed(item=self.item, speed_rpm=self.speed + other.speed)

    def __repr__(self):
        return f"{self.item.name} x {self.speed:.3f} RPM"

    def __mul__(self, mul: float):
        return Speed(item=self.item, speed_rpm=round(self.speed * mul, 3))


ItemVector = NewType("ItemVector", Sequence[Item])
SpeedVector = NewType("SpeedVector", Sequence[Speed])


def sum_items_by_count(items: ItemVector) -> ItemVector:
    count_by_items = dict()
    for item in items:
        if count_by_items.get(item.key) is None:
            count_by_items[item.key] = item.count
        else:
            count_by_items[item.key] += item.count
    return [Item(key, count) for key, count in count_by_items.items()]


def sum_items_by_rpm(speeds: SpeedVector) -> SpeedVector:
    rpm_by_items = dict()
    for speed_obj in speeds:
        if rpm_by_items.get(speed_obj.item.key) is None:
            rpm_by_items[speed_obj.item.key] = speed_obj.speed
        else:
            rpm_by_items[speed_obj.item.key] += speed_obj.speed
    # print(f"{rpm_by_items=}")
    return [Speed(Item(key), speed_rpm=rpm) for key, rpm in rpm_by_items.items()]



class Recipe:
    def __init__(self, key, count=1000):
        context = resources.get(key)
        self.exists = context
        self.key = key
        self.name = key
        if not self.exists:
            print(f"Can't create Recipe {key=}. It doesn't exist")
            pass
            # raise BaseException(f"Can't create Recipe {key=}. It doesn't exist")
        else:
            self.name = context.get("name") or key.replace("_", " ").title()

        buildings = [i for i in list(context.keys())
                     if i in [building.name.lower() for building in BUILDING]]
        # print(f"{buildings=}")
        if len(buildings) > 1:
            raise BaseException(f"Define building for Recipe instance. "
                                f"There is more than 1 building found: "
                                f"{buildings}")
        if len(buildings) == 1: building = buildings[0]
        recipe = context.get(building)
        self.producer = building
        self.count_x1 = recipe["out"]
        self.ingredients_x1 = [Item(ingr_key, ingr_count) for ingr_key, ingr_count in recipe.get("in").items()]
        self.time_x1 = recipe['time_sec']
        self.uuid = str(uuid.uuid4())
        self.count = count

    def ingredients(self, count=1):
        times = ceil(count / self.count_x1)
        return [item * times for item in self.ingredients_x1]

    def time(self, count=1):
        times = ceil(count / self.count_x1)
        return datetime.timedelta(seconds=(self.time_x1 * times))

    def is_simple(self):
        """
        doesn't require complex resource
        :return:
        """
        is_simple = True
        if not self.exists: return True
        for res in self.ingredients(1):
            sub_item = Recipe(res.name)
            if sub_item.exists:
                return False
        return is_simple

    @property
    def produce(self):
        ingredients = self.ingredients(self.count)
        time = self.time(self.count)
        total_ingredients = list()
        total_time = time

        r = (f"Creating {Item(self.name, self.count)} requires "
             f"{ingredients}"
             f" and {time} (hh:mm:ss) by ")

        r = f"{r} \t Total time required: {total_time}"
        # print(r)
        if not total_ingredients:
            # print(f"++ from {self.name} {total_ingredients=}")
            total_ingredients = ingredients

        result = {"product": Item(self.key, self.count),
                  "consume": sum_items_by_count(total_ingredients),
                  "operation": self.producer,
                  "time": total_time,
                  "uuid": self.uuid
                  }
        # print(f"RETURN {self.name}  {result}")
        return result


class RecipeSpeed:
    def __init__(self, recipe: Recipe, boosters: dict = None):
        # print(f"{boosters=}")
        self.product = recipe.produce
        self.boosters = None
        if boosters:
            self.boosters = boosters.get(self.product['operation'])
        # print(f"{self.boosters=}")

    @property
    def all(self):
        # Define speed of production
        # Define speed of each consumable
        # Multiply both values to booster multiplier
        multiplier = sum(list(self.boosters.values())) if self.boosters else 1
        speed_production = Speed(self.product['product'], self.product['time']) * multiplier
        speed_consumings = [ingr.rpm(time_sec=self.product['time'].total_seconds()) * (-1 * multiplier)
                        for ingr in self.product['consume']]
        print(f" {speed_consumings=}  {speed_production=}")

        print(f"{multiplier=}")
        speed_consumings.append(speed_production)
        return speed_consumings


def calc(resource_name, count, producers_count=1, speed_modifiers=None):
    item = resources.get(resource_name)
    if item is None:
        raise BaseException(f"Can't create item {item} in {sorted(resources.keys())}")
    for operation_name, resource_data in item.items():
        if operation_name in ["name"]: continue
        # print(f"{operation_name} {resource_data}")
        time = datetime.timedelta(seconds=resource_data.get('time_sec') * count / producers_count)
        input_resources = []
        for input_resource_name, input_resource_count in resource_data['in'].items():
            input_resources.append(f"{input_resource_name} x {input_resource_count * count}")
        print(f"Creating {resource_name} x {count} requires "
              f"{input_resources} "
              f"and {time} (hh:mm:ss) by {operation_name} x {producers_count}")


if __name__ == "__main__":
    # calc("copper_bar", 23300-4996, producers_count=1)
    # calc("gold_bar", 1500, producers_count=4)
    # calc("steel_plate", 50, producers_count=1)
    # calc("steel_bar", 20)

    print("*"*120)
    # print(Recipe("copper_bar").produce(count=25000))
    # print(Recipe("steel_plate").produce(50))
    # print(Recipe("gold_bar").produce(1500, recursive=True))
    # print(Recipe("titanium_bar").produce(210-81, recursive=True))

    # print(Recipe("gunpowder").produce(50, recursive=True))
    # print(Recipe("hydrogen").produce(2))
    #
    # print(Speed(quantity=1200, time=10))
    #
    # print(Item('clean_water', count=10).rpm(time_sec=60))
    # print(Item('clean_water', count=10).rpm(time_sec=60) * 0.5)
    # print(Item('clean_water', count=10).rpm(time_sec=60) * 6)
    # print(Item('clean_water', count=100).rpm(time_sec=1))
    # print(Item('clean_water', count=-100).rpm(time_sec=1))
    # print(Item('clean_water', count=-100).rpm(time_sec=1) * 0.5)

    # print(Speed(speed_rpm=120, quantity=1200))
    # print(Speed(speed_rpm=120, quantity=1200) * 1.5)
    #
    # print(recipes_by_operation())

    boosters = {
        "crafting": {
            "bot": 1.2,
            "tech_lab": 2,
            },
        "smelting": {
            "bot": 1.2,
            "tech_lab": 2,
            "pumpkin": 2
            }
        }
    copper_bar = RecipeSpeed(recipe=Recipe("copper_bar"), boosters=boosters).all
    wires = RecipeSpeed(recipe=Recipe("wire"), boosters=boosters).all

    steel_plate = RecipeSpeed(Recipe('steel_plate'),
                              boosters={
                                  "smelting": {
                                      "count": 2,
                                      "bot": 1.2,
                                      }
                                  }).all
    steel_bar = RecipeSpeed(Recipe('steel_bar'),
                              boosters={
                                  "smelting": {
                                      "count": 5,
                                      "bot": 1.2,
                                      }
                                  }).all
    iron_bar = RecipeSpeed(Recipe('iron_bar'),
                              boosters={
                                  "smelting": {
                                      "count": 1,
                                      "bot": 1.2,
                                      }
                                  }).all
    all = []
    all.extend(steel_plate)
    all.extend(steel_bar)
    all.extend(iron_bar)
    print(all)
    print(sum_items_by_rpm(all))
    # print(RecipeSpeed(Recipe("steel_plate", count=720)).all)

