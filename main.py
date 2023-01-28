from fastapi import FastAPI , Request
from fastapi.middleware.cors import CORSMiddleware
from routers import route_trade_information , route_auth
from schemas import SuccessMsg , CsrfSettings
from fastapi.responses import JSONResponse
from fastapi_csrf_protect import CsrfProtect
from fastapi_csrf_protect.exceptions import CsrfProtectError

app = FastAPI()
app.include_router(route_trade_information.router)
app.include_router(route_auth.router)

origin = ["http://locahost:3000", "http://127.0.0.1:8000/api/csrftoken"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origin,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@CsrfProtect.load_config
def get_csrf_config():
    return CsrfSettings()


@app.exception_handler(CsrfProtectError)
def csrf_protect_exception_handler(request: Request, exc: CsrfProtectError):
    return JSONResponse(
        status_code=exc.status_code,
        content={'detail':  exc.message
                 }
    )


@app.get("/", response_model=SuccessMsg)
def root():
    return {"message": "Welcome to Fast API"}
