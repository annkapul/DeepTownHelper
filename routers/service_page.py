
import calculator
from fastapi import APIRouter, Request, Cookie
from fastapi.responses import HTMLResponse
from typing import Optional

from .dependencies import global_data, \
    templates, _Cookie

import dictdiffer

router = APIRouter()


@router.get("/", response_class=HTMLResponse)
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
               **global_data.dict()
               }
    return templates.TemplateResponse("index.html", context=context)


@router.get("/info")
async def info():
    return {
        **global_data.dict()
    }


@router.post("/reload_resources", response_class=HTMLResponse)
async def reload_resources(request: Request,
                           saved_resource_page: Optional[str] = Cookie(None)):
    updated_res = calculator.all_resources()
    print(list(dictdiffer.diff(updated_res, global_data.all_resources)))

    global_data.all_resources = updated_res
    global_data.recipes_for_dropdown = \
        calculator.recipes_by_operation()

    context = {"request": request,
               **global_data.dict(),
               **_Cookie.load(saved_resource_page)
               }

    response = templates.TemplateResponse("index.html", context=context)
    return response
