from fastapi import HTTPException
from decouple import config
from typing import Union
import motor.motor_asyncio
import asyncio
from bson import ObjectId
from auth_utils import AuthJwtCsrf

MONGO_API_KEY = config("MONGO_API_KEY")

client = motor.motor_asyncio.AsyncIOMotorClient(MONGO_API_KEY)

database = client.API_DB
client.get_io_loop = asyncio.get_event_loop

collection_user = database.user
collection_trade_information = database.trade_information
collection_grid_risk = database.grid_risk

auth = AuthJwtCsrf()


# return dictionary
def trade_information_serializer(trade_information) -> dict :
    return {
        "id" : str(trade_information["_id"]) ,
        "trade" : trade_information["trade"] ,
        "book" : trade_information["book"] ,
        "product" : trade_information["product"] ,
    }


def user_serializer(user) -> dict :
    return {
        "id" : str(user["_id"]) ,
        "email" : user["email"] ,
    }


async def db_create_trade_information(data: dict) -> Union[dict , bool] :
    # create class
    trade_information = await collection_trade_information.insert_one(data)

    # create new task document
    new_trade_information = await collection_trade_information.find_one({"_id" : trade_information.inserted_id})

    if new_trade_information :
        return trade_information(new_trade_information)
    return False


async def db_get_trade_information() -> list :
    trade_information_list = []
    for trade_information in await collection_trade_information.find().to_list(length=100) :
        trade_information_list.append(trade_information_serializer(trade_information))
    return trade_information_list


async def db_get_single_trade_information(id: str) -> Union[dict , bool] :
    trade_information = await collection_trade_information.find_one({"_id" : ObjectId(id)})
    if trade_information :
        return trade_information_serializer(trade_information)
    return False


async def db_update_trade_information(id: str , data: dict) -> Union[dict , bool] :
    # 引数で受け取ったidがdbに存在するかを確認
    trade_information = await collection_trade_information.find_one({"_id" : ObjectId(id)})

    if trade_information :
        updated_trade_information = await collection_trade_information.update_one({"_id" : ObjectId(id)} ,
                                                                                  {"$set" : data})

        # updateされていたら、modified_countにupdateされた数を返す
        if updated_trade_information.modified_count > 0 :
            new_trade_information = await collection_trade_information.find_one({"_id" : ObjectId(id)})
            return trade_information_serializer(new_trade_information)

    return False


async def db_delete_trade_information(id: str) -> Union[dict , bool] :
    # 引数で受け取ったidがdbに存在するかを確認
    trade_information = await collection_trade_information.find_one({"_id" : ObjectId(id)})

    if trade_information :
        deleted_trade_information = await collection_trade_information.delete_one({"_id" : ObjectId(id)})
        # deleteされていたら、deleted_countにdeleteされた数を返す
        if deleted_trade_information.deleted_count > 0 :
            return True

    return False


async def db_signup(data: dict) -> dict :
    email = data.get("email")
    password = data.get("password")

    overlap_user = await collection_user.find_one({"email" : email})
    if overlap_user :
        raise HTTPException(status_code=400 , detail="Email is already taken.")
    if not password or len(password) < 3 :
        raise HTTPException(status_code=400 , detail="Password is short")

    user = await collection_user.insert_one({"email" : email , "password" : auth.generate_hashed_pw(password)})
    new_user = await collection_user.find_one({"_id" : user.inserted_id})

    return user_serializer(new_user)


async def db_login(data: dict) -> str :
    email = data.get("email")
    password = data.get("password")
    user = await collection_user.find_one({"email" : email})

    if not user or not auth.verify_pw(password , user["password"]) :
        raise HTTPException(
            status_code=401 , detail='Invalid email or password')

    token = auth.encode_jwt(user['email'])

    return token
