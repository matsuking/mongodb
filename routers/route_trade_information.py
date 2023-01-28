from fastapi import APIRouter
from fastapi import Response , Request , HTTPException , Depends
from fastapi.encoders import jsonable_encoder
from schemas import TradeInformation , TradeInformationBody , SuccessMsg
from database import db_create_trade_information , db_get_trade_information , db_get_single_trade_information , \
    db_update_trade_information , db_delete_trade_information
from starlette.status import HTTP_201_CREATED
from typing import List
from fastapi_csrf_protect import CsrfProtect
from auth_utils import AuthJwtCsrf

router = APIRouter()
auth = AuthJwtCsrf()


@router.post("/api/trade_information" , response_model=TradeInformation)
async def create_trade_information(request: Request , response: Response , data: TradeInformationBody ,
                                   csrf_protect: CsrfProtect = Depends()) :
    new_token = auth.verify_csrf_update_jwt(request, csrf_protect, request.headers)

    # convert json to dic
    trade_information = jsonable_encoder(data)

    res = await db_create_trade_information(trade_information)

    response.status_code = HTTP_201_CREATED
    # CSRF Token、JWTが有効かどうかを検証したあと、書き換える必要があれば書き換える
    response.set_cookie(key="access_token", value=f"Bearer {new_token}", httponly=True, samesite="none", secure=True)

    if res :
        return res
    raise HTTPException(status_code=404 , detail="Create trade information failed.")


@router.get("/api/trade_information" , response_model=List[TradeInformation])
async def get_trade_information(request: Request) :
    # auth.verify_jwt(request)
    res = await db_get_trade_information()

    return res


@router.get("/api/trade_information/{id}" , response_model=TradeInformation)
async def get_single_trade_information(request: Request, response: Response, id: str) :
    new_token, _ = auth.verify_update_jwt(request)

    res = await db_get_single_trade_information(id)
    response.set_cookie(key="access_token" , value=f"Bearer {new_token}" , httponly=True , samesite="none" ,
                        secure=True)

    if res :
        return res
    raise HTTPException(status_code=404 , detail=f"Trade Information of ID: {id} doesn't exist")


@router.put("/api/trade_information/{id}" , response_model=TradeInformation)
async def update_trade_information(request: Request , response: Response ,id: str , data: TradeInformationBody,csrf_protect: CsrfProtect = Depends()) :
    new_token = auth.verify_csrf_update_jwt(request , csrf_protect , request.headers)

    trade_information = jsonable_encoder(data)

    res = await db_update_trade_information(id , trade_information)
    response.set_cookie(key="access_token" , value=f"Bearer {new_token}" , httponly=True , samesite="none" ,
                        secure=True)
    if res :
        return res
    raise HTTPException(status_code=404 , detail=f"Update task failed.")


@router.delete("/api/trade_information/{id}" , response_model=SuccessMsg)
async def delete_trade_information(request: Request , response: Response ,id: str, csrf_protect: CsrfProtect = Depends()) :
    new_token = auth.verify_csrf_update_jwt(request , csrf_protect , request.headers)

    res = await db_delete_trade_information(id)
    response.set_cookie(key="access_token" , value=f"Bearer {new_token}" , httponly=True , samesite="none" ,
                        secure=True)

    if res :
        return {"message" : "Successfully deleted"}
    raise HTTPException(status_code=404 , detail=f"Delete task failed.")
