import yaml
import datetime
import enum
from typing import  NewType, Sequence
from math import ceil


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
    recipes_by_op = {}
    for recipe_key, recipe_data in resources.items():
        for key, value in recipe_data.items():
            operation = key.title()
            if operation not in [building.name for building in BUILDING] :
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


class Building:
    def speed(self):
        pass


class Item:
    def __init__(self, name, count=1):
        self.name = name
        self.count = count

    def __repr__(self):
        if self.count > int(self.count):
            count = int(self.count) + 1
        else:
            count = int(self.count)
        return f"{self.name} x {count}"

    def __mul__(self, number: int):
        return Item(self.name, self.count * number)


ItemVector = NewType("ItemVector", Sequence[Item])


def sum_list_of_items(items: ItemVector) -> ItemVector:
    count_by_items = dict()
    for item in items:
        if count_by_items.get(item.name) is None:
            count_by_items[item.name] = item.count
        else:
            count_by_items[item.name] += item.count
    return [Item(name, count) for name, count in count_by_items.items()]

class Speed:
    def __init__(self, quantity: int = None,
                 time: (datetime.timedelta, int) = None,
                 speed_rpm: int = None):
        defined_vars = [i for i in [quantity, time, speed_rpm] if i is not None]
        if defined_vars.__len__() <2:
            raise BaseException(
                f"Need at least 2 parameters to initilize Speed(). "
                f"We got {[quantity, time, speed_rpm]=}")
        self._quantity = quantity
        if isinstance(time, int):
            self._time = datetime.timedelta(minutes=time)
        else:
            self._time = time
        self._speed = speed_rpm

    @property
    def quantity(self):
        if self._quantity: return self._quantity
        return ceil(self._speed * ((self._time.seconds // 60) % 60))
    
    @property
    def time(self):
        if self._time: return self._time
        return datetime.timedelta(minutes=int(self._quantity / self._speed))

    @property
    def speed(self):
        if self._speed: return self._speed
        return int(self._quantity / ((self._time.seconds // 60) % 60))

    def __repr__(self):
        return f"{self.quantity} for {self.time} with {self.speed} RPM"

    def __mul__(self, mul: float):
        return Speed(quantity=self.quantity, speed_rpm=int(self.speed * mul))

class Recipe:
    def __init__(self, key, building=None):
        context = resources.get(key)
        self.exists = context
        self.key = key
        self.name = key
        if self.exists:
            self.name = context.get("name") or key

            buildings = [ i for i in list(context.keys()) if i not in ["name"]]
            # print(f"{buildings=}")
            if len(buildings) > 1:
                raise BaseException(f"Define building for Recipe instance. "
                                    f"There is more than 1 building found: "
                                    f"{buildings}")
            if len(buildings) == 1: building = buildings[0]
            recipe = context.get(building)
            self.producer = building
            self.count_x1 = recipe["out"]
            self.ingredients_x1 = [Item(ingr_name, ingr_count) for ingr_name, ingr_count in recipe.get("in").items()]
            self.time_x1 = recipe['time_sec']

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

    def produce(self, count, recursive=False):
        ingredients = self.ingredients(count)
        time = self.time(count)
        total_ingredients = list()
        total_time = time

        r = (f"Creating {Item(self.name, count)} requires "
             f"{ingredients}"
             f" and {time} (hh:mm:ss) by ")
        if recursive:
            for res in ingredients:
                sub_recipe = Recipe(res.name)

                if not sub_recipe.exists:
                    total_ingredients.append(res)
                    continue
                if sub_recipe.is_simple():
                    sub_product = sub_recipe.produce(res.count, recursive=recursive)
                    # print(f"Add simple item {sub_product.get('out')}")
                    total_ingredients.extend(sub_product.get('out'))
                    # print(f"from {self.name} {total_ingredients=}")
                    continue

                sub_product = sub_recipe.produce(res.count, recursive=recursive)
                total_ingredients.extend(sub_product.get('out'))
                r = f"{r} \n " \
                    f"|| || || \n" \
                    f" v  v  v \n {sub_recipe.produce(res.count, recursive=recursive)}"
                total_time += sub_recipe.time(res.count)
        r = f"{r} \t Total time required: {total_time}"
        # print(r)
        if not total_ingredients:
            # print(f"++ from {self.name} {total_ingredients=}")
            total_ingredients = ingredients

        result = {"in": Item(self.name, count),
                  "out": sum_list_of_items(total_ingredients),
                  "time": total_time,
                  "produce_speed": None,
                  "consume_speed": None
                  }
        # print(f"RETURN {self.name}  {result}")
        return result


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

# Resource()
# smelting = Building("smelting", total_count=8)
class CraftBooster:
    pass


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
    print(Recipe("hydrogen").produce(2))

    print(Speed(quantity=1200, time=10))

    print(Speed(speed_rpm=120, time=10))
    print(Speed(speed_rpm=120, quantity=1200))
    print(Speed(speed_rpm=120, quantity=1200) * 1.5)

    print(recipes_by_operation())
