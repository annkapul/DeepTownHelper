import pickle
import codecs

from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
import calculator
import mine_calculator
from typing import Dict, Union, Any, OrderedDict

cookies_expire_time = 2592000

templates = Jinja2Templates(directory="templates")


class _Cookie:
    @staticmethod
    def dump(value):
        return codecs.encode(pickle.dumps(value, 5),
                             encoding='base64').decode()

    @staticmethod
    def load(value):
        return pickle.loads(codecs.decode(value.encode(),
                                          "base64"))


class GlobalModel(BaseModel):
    recipes_for_dropdown: dict
    all_resources: dict
    all_mines: dict


class RecipePageModel(BaseModel):
    all_resources: dict


class MinePageModel(BaseModel):
    elements: list
    last_selected_item: str
    last_mines_count: int
    last_mines_level: int
    last_time_minutes: int
    last_max_area: int


global_data = GlobalModel(
    recipes_for_dropdown=calculator.recipes_by_operation(),
    all_resources=calculator.all_resources(),
    all_mines=mine_calculator.all_mines(),
)


saved_mines_page = MinePageModel(
    elements=mine_calculator.elements,
    last_selected_item='coal',
    last_mines_count=1,
    last_mines_level=1,
    last_time_minutes=1440,
    last_max_area=120
    )


class PlannerModel(BaseModel):
    mines: OrderedDict[int, int]   # # area, lvl
    smelting: Dict[int, Union[Any, None]]  # number, recipe
    crafting: Dict[int, Union[Any, None]]  # number, recipe
    chemistry: Dict[int, Union[Any, None]]  # number, recipe
    jewelling: Dict[int, Union[Any, None]]  # number, Recipe
    planting: Dict[int, Union[Any, None]]  # number, Recipe
    boosters: Dict[str, Any]
    count_of_mines: int


default_planner = PlannerModel(
    count_of_mines=5,
    mines={1: 9,
           2: 7,
           3: 6},
    smelting={
        0: "iron_bar",
        1: "",
        2: "",
        3: "",
        4: "",
        5: "",
        6: "",
        7: ""
        },
    crafting={
        0: "diamond_cutter",
        1: "",
        2: "",
        3: "",
        4: "",
        5: "",
        6: "",
        7: ""
    },
    jewelling={
        0: "polished_diamond",
        1: "",
        2: "",
        3: "",
        4: "",
        5: "",
        6: "",
        7: ""
    },
    planting={
        0: "liana",
        1: "",
        2: "",
        3: "",
        4: "",
        5: "",
        6: "",
        7: ""
    },
    chemistry={
        0: "clean_water",
        1: "",
        2: "",
        3: "",
        4: "",
        5: "",
        6: "",
        7: ""
    },
    boosters={
        "smelting": ["bot"]
    },

    )
