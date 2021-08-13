
import calculator
import mine_calculator
from fastapi import APIRouter, Cookie, Request
from fastapi.responses import HTMLResponse
from typing import Optional

from datetime import timedelta

from .dependencies import global_data, \
    templates, default_planner, _Cookie, cookies_expire_time

import collections

router = APIRouter()


def plain_to_dict(plain_dict, base_dict):
    # print(f"{plain_dict=}")
    # print(f"{base_dict=}")
    nested_dict = base_dict
    nested_dict["mines"] = collections.OrderedDict()
    for key, value in plain_dict.items():
        # print(f"{key=}, {value=}")
        if key in ["count_of_mines", "count_of_chmines"]:
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
            if not plain_dict[f'minelvlN_{number}'] or not plain_dict[f'mineareaN_{number}']:
                continue

            nested_dict['mines'][int(value)] = int(plain_dict[f'minelvlN_{number}'])
            continue

        if operation_name == "chminelvl":
            if not plain_dict[f'chmineres_{number}']:
                continue
            nested_dict['chemmines'][int(number)] = (str(plain_dict[f'chmineres_{number}']), int(value))
            # print(f"CHEMMINES {operation_name=} {value=}")
            continue
        if operation_name == "chmineres":
            continue
        if "minelvl" in operation_name: continue
    # print(f"after {nested_dict=}")
    return nested_dict


# async def save_cookies(response: Response):


def speeds_sorting(speed):
    if speed.speed < 0:
        return abs(speed.speed) * 1000000
    return speed.speed


@router.get("/planner", response_class=HTMLResponse)
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
        **_planner_model,
        **global_data.dict()
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
        if operation in ['chemmines']:
            for resource, lvl in data.values():
                list_of_speeds += mine_calculator.ChemMine(resource=mine_calculator.CHEM[resource],
                                                           level=lvl).get_items_speed()
        # Define speeds for smelting / crafting etc
        if operation in ["smelting", "crafting", "jewelling", "planting", "chemistry"]:
            for _, recipe in data.items():
                if recipe == "" or recipe is None: continue
                list_of_speeds += calculator.RecipeSpeed(
                    calculator.Recipe(recipe)).all
    sum_list_of_speeds = calculator.sum_items_by_rpm(list_of_speeds)
    print(f"{sum_list_of_speeds=}")
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
