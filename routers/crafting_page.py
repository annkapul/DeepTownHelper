import calculator
from fastapi import APIRouter, Cookie, Request
from fastapi.responses import HTMLResponse

from typing import Optional
from .dependencies import _Cookie, global_data, \
    templates, cookies_expire_time

router = APIRouter()


@router.get("/items", response_class=HTMLResponse)
async def item(request: Request,
               saved_resource_page: Optional[str] = Cookie(None)):

    if saved_resource_page:
        _saved_resource_page = _Cookie.load(saved_resource_page)
    else:
        _saved_resource_page = dict(
            opened_recipes=dict()
        )
    context = {"request": request,
               **global_data.dict(),
               **_saved_resource_page
               }
    return templates.TemplateResponse("index.html", context=context)


@router.post("/items", response_class=HTMLResponse)
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
               **global_data.dict(),
               **saved_resource_page}

    response = templates.TemplateResponse("index.html", context=context)

    response.set_cookie("saved_resource_page",
                        _Cookie.dump(saved_resource_page),
                        max_age=cookies_expire_time)

    return response


@router.post("/add_product", response_class=HTMLResponse)
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
               **global_data.dict(),
               **_saved_resource_page}

    response = templates.TemplateResponse("index.html", context=context)
    response.set_cookie('saved_resource_page',
                        _Cookie.dump(_saved_resource_page),
                        max_age=cookies_expire_time)
    return response


@router.post("/del_product", response_class=HTMLResponse)
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
               **global_data.dict(),
               **_saved_resource_page}
    response = templates.TemplateResponse("index.html", context=context)
    response.set_cookie("saved_resource_page",
                        _Cookie.dump(_saved_resource_page),
                        max_age=cookies_expire_time)
    return response