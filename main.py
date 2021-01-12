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
templates = Jinja2Templates(directory="templates")


class PageModel(BaseModel):
    all_resources: dict
    last_selected_item: str
    last_selected_count: int
    last_selected_recursive: bool


class MinePageModel(BaseModel):
    elements: list
    mines: dict
    last_selected_item: str
    last_mines_count: int
    last_mines_level: int
    last_time_minutes: int


saved_resource_page = PageModel(
    all_resources=calculator.all_resources(),
    last_selected_recursive=False,
    last_selected_item="copper",
    last_selected_count=1)

saved_mines_page = MinePageModel(
    elements=mine_calculator.elements,
    mines=mine_calculator.all_mines(),
    last_selected_item='coal',
    last_mines_count=1,
    last_mines_level=1,
    last_time_minutes=1000
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
    recursive = form_data.get("recursive")

    saved_resource_page.last_selected_count = count
    saved_resource_page.last_selected_item = name
    saved_resource_page.last_selected_recursive = recursive

    result = calculator.Recipe(name).produce(count, recursive=recursive)

    # print(saved_resource_page.dict())
    context = {"request": request, "result": result, **saved_resource_page.dict()}
    return templates.TemplateResponse("index.html", context=context)
    # return {"username": username, "id": id}


@app.post("/reload_resources", response_class=HTMLResponse)
async def reload_resources(request: Request):
    updated_res = calculator.all_resources()
    print(list(dictdiffer.diff(updated_res, saved_resource_page.all_resources)))

    saved_resource_page.all_resources = calculator.all_resources()
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

    saved_mines_page.last_selected_item = item
    saved_mines_page.last_mines_count = mines_count
    saved_mines_page.last_mines_level = mines_level
    saved_mines_page.last_time_minutes = time_minutes

    result = mine_calculator.find_best_mines(
            item=calculator.Item(item),
            mines_count=mines_count,
            mines_level=mines_level,
            time_minutes=time_minutes
            )
    context = {
        "request": request,
        "result": result,
        **saved_mines_page.dict(),
        }
    return templates.TemplateResponse("mines.html", context=context)


@app.post("/add_item")
async def add_item(item_id: str = Form(...)):
    return {"item_id": item_id}


