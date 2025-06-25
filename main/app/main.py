from typing import Union
from graphs.testing import test

from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def read_root():
    test()
    return {"Hello": "world"}
