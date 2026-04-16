from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.database import db

router = APIRouter()


class GreetingInput(BaseModel):
    message: str


class GreetingOutput(BaseModel):
    message: str


@router.post("/greetings", response_model=GreetingOutput)
def create_greeting(greeting: GreetingInput):
    db.create_greeting(greeting.message)
    return GreetingOutput(message=greeting.message)


@router.get("/greetings", response_model=list[GreetingOutput])
def get_greetings():
    messages = db.get_greetings()
    return [GreetingOutput(message=msg) for msg in messages]
