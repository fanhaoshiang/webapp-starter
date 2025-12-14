from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

@app.get("/")
def root():
    return {"ok": True, "msg": "Hello from Codespaces"}

# A) 帶參數 GET
@app.get("/hello")
def hello(name: str = "KKK"):
    return {"hello": name}

# B) POST JSON
class Item(BaseModel):
    title: str
    price: float

@app.post("/items")
def create_item(item: Item):
    return {"ok": True, "item": item.model_dump()}
