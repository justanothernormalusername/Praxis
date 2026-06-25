from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

class Animal(BaseModel):
    name: str
    weight: int

@app.get("/")
async def root():
    return {"message": "Hello World"}

@app.post("/animal")
async def add_animal(animal: Animal):
    summary = f"{animal.name} weighs {animal.weight} tons"
    return {"summary": summary}
