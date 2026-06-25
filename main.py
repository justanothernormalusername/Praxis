# from pydantic import BaseModel
from typing import Annotated
import asyncio

async def async_function():
    variable = await sum()
    return variable

def full_name(first_name: int | None = None, last_name: str | None = None):
    return first_name.capitalize() + " " + last_name.capitalize()

#print(full_name("deng"))

def say_hello(name: Annotated[str, "string"]) -> str:
    return

say_hello("me")