import calculator
import mine_calculator
from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse

from .dependencies import global_data, \
    templates, saved_mines_page

router = APIRouter()


@router.get("/mines", response_class=HTMLResponse)
async def mines(request: Request):
    context = {
        "request": request,
        **saved_mines_page.dict(),
        **global_data.dict()
        }
    return templates.TemplateResponse("mines.html", context=context)


@router.post("/mines", response_class=HTMLResponse)
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
        **global_data.dict()
        }
    return templates.TemplateResponse("mines.html", context=context)
