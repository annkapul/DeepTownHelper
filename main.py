from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from routers import crafting_page, planning_page, mining_page, service_page


app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")
app.mount("/images", StaticFiles(directory="images"), name="images")

app.include_router(service_page.router)
app.include_router(crafting_page.router)
app.include_router(mining_page.router)
app.include_router(planning_page.router)


if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host='0.0.0.0', port=8000)
