import collections

from fastapi import FastAPI, Request, Form, Cookie, File, UploadFile, Response
from fastapi.responses import HTMLResponse, JSONResponse, FileResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import Dict, TypeVar, Union, Any, Optional, OrderedDict

import calculator
import mine_calculator
import dictdiffer
import pickle, codecs
from datetime import timedelta

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")
app.mount("/images", StaticFiles(directory="images"), name="images")
templates = Jinja2Templates(directory="templates")

cookies_expire_time = 2592000

class RecipePageModel(BaseModel):
    recipes_for_dropdown: dict
    all_resources: dict


class MinePageModel(BaseModel):
    elements: list
    mines: dict
    last_selected_item: str
    last_mines_count: int
    last_mines_level: int
    last_time_minutes: int
    last_max_area: int


resource_page = RecipePageModel(
    recipes_for_dropdown=calculator.recipes_by_operation(),
    all_resources=calculator.all_resources(),)


saved_mines_page = MinePageModel(
    elements=mine_calculator.elements,
    mines=mine_calculator.all_mines(),
    last_selected_item='coal',
    last_mines_count=1,
    last_mines_level=1,
    last_time_minutes=1440,
    last_max_area=120
    )


@app.get("/", response_class=HTMLResponse)
async def root(request: Request,
               saved_resource_page: Optional[str] = Cookie(None)
               ):
    if saved_resource_page:
        _saved_resource_page = _Cookie.load(saved_resource_page)
    else:
        _saved_resource_page = dict(
            opened_recipes=dict()
        )
    context = {"request": request,
               **_saved_resource_page,
               **resource_page.dict()
               }
    return templates.TemplateResponse("index.html", context=context)


@app.get("/items", response_class=HTMLResponse)
async def item(request: Request,
               saved_resource_page: Optional[str] = Cookie(None)):

    if saved_resource_page:
        _saved_resource_page = _Cookie.load(saved_resource_page)
    else:
        _saved_resource_page = dict(
            opened_recipes=dict()
        )
    context = {"request": request,
               **resource_page.dict(),
               **_saved_resource_page
               }
    return templates.TemplateResponse("index.html", context=context)


@app.post("/items", response_class=HTMLResponse)
async def calc_items(request: Request):
    form_data = await request.form()

    count = form_data.get("count")
    name = form_data.get("res")

    if isinstance(count, str):
        count = eval(count)

    recipe = calculator.Recipe(name, count)
    result = recipe.produce
    print(f"{result=}")
    opened_recipes = dict()
    opened_recipes[str(recipe)] = result

    saved_resource_page = {
        "last_selected_count": count,
        "last_selected_item": name,
        "opened_recipes": opened_recipes
    }

    context = {"request": request,
               "result": result,
               "total": result.get("out"),
               **resource_page.dict(),
               **saved_resource_page}

    response = templates.TemplateResponse("index.html", context=context)

    response.set_cookie("saved_resource_page",
                        _Cookie.dump(saved_resource_page),
                        max_age=cookies_expire_time)

    return response


@app.post("/add_product", response_class=HTMLResponse)
async def add_product_from_button(
        request: Request,
        saved_resource_page: Optional[str] = Cookie(None)):
    form_data = await request.form()

    count = int(form_data.get("count"))
    key = form_data.get("key").strip()
    uuid = form_data.get("uuid").strip()

    recipe = calculator.Recipe(key, count)
    result = recipe.produce
    _saved_resource_page = _Cookie.load(saved_resource_page)
    _saved_resource_page['opened_recipes'][uuid] = result

    ids_opened_frames = list(_saved_resource_page['opened_recipes'].keys())
    print(f"{ids_opened_frames=}")

    total = [ingr
             for uuid, recipe in _saved_resource_page['opened_recipes'].items()
             for ingr in recipe["consume"]
             if ingr.uuid not in ids_opened_frames]
    total = calculator.sum_items_by_count(total)

    context = {"request": request,
               "result": result,
               "total": total,
               **resource_page.dict(),
               **_saved_resource_page}

    response = templates.TemplateResponse("index.html", context=context)
    response.set_cookie('saved_resource_page',
                        _Cookie.dump(_saved_resource_page),
                        max_age=cookies_expire_time)
    return response


@app.post("/del_product", response_class=HTMLResponse)
async def del_product_from_button(
        request: Request,
        saved_resource_page: Optional[str] = Cookie(None)
):
    form_data = await request.form()

    uuid = form_data.get("uuid").strip()

    _saved_resource_page = _Cookie.load(saved_resource_page)

    if _saved_resource_page['opened_recipes'].get(uuid):
        _saved_resource_page['opened_recipes'].__delitem__(uuid)

    ids_opened_frames = list(_saved_resource_page['opened_recipes'].keys())
    print(f"{ids_opened_frames=}")

    print(f"{_saved_resource_page['opened_recipes']}")
    total = [ingr
             for uuid, recipe in _saved_resource_page['opened_recipes'].items()
             for ingr in recipe["consume"]
             if ingr.uuid not in ids_opened_frames]
    total = calculator.sum_items_by_count(total)

    context = {"request": request,
               "total": total,
               **resource_page.dict(),
               **_saved_resource_page}
    response = templates.TemplateResponse("index.html", context=context)
    response.set_cookie("saved_resource_page",
                        _Cookie.dump(_saved_resource_page),
                        max_age=cookies_expire_time)
    return response


@app.post("/reload_resources", response_class=HTMLResponse)
async def reload_resources(request: Request,
                           saved_resource_page: Optional[str] = Cookie(None)):
    updated_res = calculator.all_resources()
    print(list(dictdiffer.diff(updated_res, resource_page.all_resources)))

    resource_page.all_resources = updated_res
    resource_page.recipes_for_dropdown = \
        calculator.recipes_by_operation()

    context = {"request": request,
               **resource_page.dict(),
               **_Cookie.load(saved_resource_page)
               }

    response = templates.TemplateResponse("index.html", context=context)
    return response


@app.get("/mines", response_class=HTMLResponse)
async def mines(request: Request):
    context = {
        "request": request,
        **saved_mines_page.dict()
        }
    return templates.TemplateResponse("mines.html", context=context)


@app.post("/mines", response_class=HTMLResponse)
async def get_best_mines(request: Request):
    form_data = await request.form()

    item = form_data.get("item")
    mines_count = int(form_data.get("mines_count"))
    mines_level = int(form_data.get("mines_level"))
    time_minutes = form_data.get("time_minutes")
    max_area = int(form_data.get("max_area"))

    saved_mines_page.last_selected_item = item
    saved_mines_page.last_mines_count = mines_count
    saved_mines_page.last_mines_level = mines_level
    saved_mines_page.last_time_minutes = time_minutes
    saved_mines_page.last_max_area = max_area

    print(f"{item=} {calculator.Item(item)}")

    result = mine_calculator.find_best_mines(
            item=calculator.Item(item),
            mines_count=mines_count,
            mines_level=mines_level,
            time_minutes=time_minutes,
            max_area=max_area
            )
    context = {
        "request": request,
        "result": result,
        **saved_mines_page.dict(),
        }
    return templates.TemplateResponse("mines.html", context=context)


class PlannerModel(BaseModel):
    recipes_for_dropdown: dict
    mines: OrderedDict[int, int]   # # area, lvl
    smelting: Dict[int, Union[Any, None]]  # number, recipe
    crafting: Dict[int, Union[Any, None]]  # number, recipe
    chemistry: Dict[int, Union[Any, None]]  # number, recipe
    jewelling: Dict[int, Union[Any, None]]  # number, Recipe
    planting: Dict[int, Union[Any, None]]  # number, Recipe
    boosters: Dict[str, Any]
    count_of_mines: int


default_planner = PlannerModel(
    recipes_for_dropdown=calculator.recipes_by_operation(),
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


def plain_to_dict(plain_dict, base_dict):
    nested_dict = base_dict
    nested_dict["mines"] = collections.OrderedDict()
    for key, value in plain_dict.items():
        # print(f"{key=}, {value=}")
        if key in ["count_of_mines"]:
            nested_dict[key] = int(value)
            continue
        operation_name, number = key.split("_")
        # print(f" |----> {operation_name=}, {number=}")

        if operation_name in [building.name.lower() for building in calculator.BUILDING]:
            nested_dict[operation_name][int(number)] = value
            continue
        if operation_name == "minearea":
            # print(f"For mines {key=}, {value=}")
            if not value or not plain_dict[f'minelvl_{number}']: continue
            nested_dict['mines'][int(value)] = int(plain_dict[f'minelvl_{number}'])
            continue
        if operation_name == "mineareaN":
            if not plain_dict[f'minelvlN_{number}'] or not plain_dict[f'mineareaN_{number}']: continue

            nested_dict['mines'][int(value)] = int(plain_dict[f'minelvlN_{number}'])
            continue
        if "minelvl" in operation_name: continue
    return nested_dict


# async def save_cookies(response: Response):

class _Cookie:
    @staticmethod
    def dump(value):
        return codecs.encode(pickle.dumps(value, 5),
                             encoding='base64').decode()

    @staticmethod
    def load(value):
        return pickle.loads(codecs.decode(value.encode(),
                                          "base64"))


def speeds_sorting(speed):
    if speed.speed < 0:
        return abs(speed.speed) * 1000000
    return speed.speed


@app.get("/planner", response_class=HTMLResponse)
async def planner(request: Request,
                  planner_model: Optional[str] = Cookie(None)):
    save_cookies = True

    if request.query_params.__len__() > 0:
        print("Reading from parameters")
        _planner_model = plain_to_dict(request.query_params,
                                       default_planner.dict())
        # print(f"{_planner_model=}")

    elif planner_model:
        print("Reading from cookies")
        _planner_model = _Cookie.load(planner_model)
        # _planner_model = pickle.loads(codecs.decode(planner_model.encode(),
        #                                             "base64"))
        # print(f"{_planner_model=}")

    else:
        _planner_model = default_planner.dict()
        print("QUERY IS EMPTY!")

    result = evaluate_planner(_planner_model)

    _planner_model["mines"] = collections.OrderedDict(
        sorted(_planner_model['mines'].items()))
    context = {
        "request": request,
        "result": result,
        **_planner_model
        }

    response = templates.TemplateResponse("planner.html", context=context)
    try:
        response.set_cookie(key='planner_model',
                            value=_Cookie.dump(_planner_model),
                            max_age=cookies_expire_time
                            )
    except Exception as e:
        print(f"Caught error: {e}")
    return response


def evaluate_planner(planner_model):

    # print(f"Starting evaluate_planner {planner_model}")
    list_of_speeds = []
    for operation, data in planner_model.items():
        # print(f"{operation=} {data=}")
        if operation in ['boosters', 'recipes_for_dropdown', 'count_of_mines']:
            continue
        # Define speed for mines
        if operation in ['mines']:
            for area, lvl in data.items():
                if not area or not lvl: continue
                list_of_speeds += mine_calculator.Mine(area=area,
                                                       level=lvl).get_items_speed()
            continue
        # Define speeds for smelting / crafting etc
        for _, recipe in data.items():
            if recipe == "" or recipe is None: continue
            list_of_speeds += calculator.RecipeSpeed(
                calculator.Recipe(recipe)).all
    sum_list_of_speeds = calculator.sum_items_by_rpm(list_of_speeds)
    sorted_sum_list = sorted(sum_list_of_speeds,
                             key=speeds_sorting,
                             reverse=True)
    #   Group like SPEED, COUNT FOR 5h , COUNT for 1 DAY
    result = [
        (speed,
         speed.quantity(time_sec=timedelta(hours=1)),
         speed.quantity(time_sec=timedelta(hours=8)),
         speed.quantity(time_sec=timedelta(days=1))
         )
        for speed in sorted_sum_list]
    # print(f"TRIPLE VARS {result=}")
    return result


if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host='0.0.0.0', port=8000)


