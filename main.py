from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

import calculator
import mine_calculator
import dictdiffer

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")
app.mount("/images", StaticFiles(directory="images"), name="images")
templates = Jinja2Templates(directory="templates")


class RecipePageModel(BaseModel):
    recipes_for_dropdown: dict
    all_resources: dict
    last_selected_item: str
    last_selected_count: int
    opened_recipes: dict


class MinePageModel(BaseModel):
    elements: list
    mines: dict
    last_selected_item: str
    last_mines_count: int
    last_mines_level: int
    last_time_minutes: int
    last_max_area: int


saved_resource_page = RecipePageModel(
    recipes_for_dropdown=calculator.recipes_by_operation(),
    all_resources=calculator.all_resources(),
    last_selected_item="copper",
    last_selected_count=1,
    opened_recipes=dict())

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
async def root(request: Request):
    context = {"request": request,
               **saved_resource_page.dict()
               }
    return templates.TemplateResponse("index.html", context=context)


@app.get("/items", response_class=HTMLResponse)
async def item(request: Request):

    context = {"request": request,
               **saved_resource_page.dict()
               }
    return templates.TemplateResponse("index.html", context=context)


@app.post("/items", response_class=HTMLResponse)
async def calc_items(request: Request):
    form_data = await request.form()

    count = int(form_data.get("count"))
    name = form_data.get("res")

    saved_resource_page.last_selected_count = count
    saved_resource_page.last_selected_item = name

    result = calculator.Recipe(name, count).produce
    print(f"{result=}")

    saved_resource_page.opened_recipes = dict()
    saved_resource_page.opened_recipes["0"] = result

    # print(saved_resource_page.dict())
    context = {"request": request,
               "result": result,
               "total": result.get("out"),
               **saved_resource_page.dict()}
    return templates.TemplateResponse("index.html", context=context)


@app.post("/add_product", response_class=HTMLResponse)
async def add_product_from_button(request: Request):
    form_data = await request.form()

    count = int(form_data.get("count"))
    key = form_data.get("key").strip()
    uuid = form_data.get("uuid").strip()

    result = calculator.Recipe(key, count).produce
    saved_resource_page.opened_recipes[uuid] = result

    ids_opened_frames = list(saved_resource_page.opened_recipes.keys())
    print(f"{ids_opened_frames=}")

    total = [ingr
             for uuid, recipe in saved_resource_page.opened_recipes.items()
             for ingr in recipe["consume"]
             if ingr.uuid not in ids_opened_frames]
    total = calculator.sum_items_by_count( total )

    context = {"request": request,
               "result": result,
               "total": total,
               **saved_resource_page.dict()}
    return templates.TemplateResponse("index.html", context=context)


@app.post("/del_product", response_class=HTMLResponse)
async def del_product_from_button(request: Request):
    form_data = await request.form()

    uuid = form_data.get("uuid").strip()

    saved_resource_page.opened_recipes.__delitem__(uuid)

    ids_opened_frames = list(saved_resource_page.opened_recipes.keys())
    print(f"{ids_opened_frames=}")

    import json

    print(f"{saved_resource_page.opened_recipes}")
    total = [ingr
             for uuid, recipe in saved_resource_page.opened_recipes.items()
             for ingr in recipe["consume"]
             if ingr.uuid not in ids_opened_frames]
    total = calculator.sum_items_by_count( total )

    context = {"request": request,
               "total": total,
               **saved_resource_page.dict()}
    return templates.TemplateResponse("index.html", context=context)


@app.post("/reload_resources", response_class=HTMLResponse)
async def reload_resources(request: Request):
    updated_res = calculator.all_resources()
    print(list(dictdiffer.diff(updated_res, saved_resource_page.all_resources)))

    saved_resource_page.all_resources = updated_res
    saved_resource_page.recipes_for_dropdown = calculator.recipes_by_operation()
    context = {"request": request, **saved_resource_page.dict()}
    return templates.TemplateResponse("index.html", context=context)


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
    time_minutes = int(form_data.get("time_minutes"))
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


@app.get("/planner", response_class=HTMLResponse)
async def planner(request: Request):
    result= {}
    context = {
        "request": request,
        "result": result,
        }
    return templates.TemplateResponse("planner.html", context=context)


if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host='0.0.0.0', port=8000)


