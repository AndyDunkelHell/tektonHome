from fastapi import FastAPI, Form, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import scripts.ESP32Control as strip
import shlex
from pydantic import BaseModel
from typing import Optional
import json

app = FastAPI()


# Data model to represent the incoming data
class Board(BaseModel):
    id: int
    name: str
    description: Optional[dict] = None

# In-memory store to simulate database
database = {}

@app.post("/Boards/", status_code=status.HTTP_201_CREATED)
def create_Board(Board: Board):
    if Board.id in database:
        raise HTTPException(status_code=400, detail="Board already exists")
    database[Board.id] = Board
    return {"message": "Board created successfully", "Board": Board}

@app.get("/Boards/{Board_id}")
def read_Board(Board_id: int):
    if Board_id not in database:
        raise HTTPException(status_code=404, detail="Board not found")
    loaded_board = database[Board_id] 
    return {"message": "Board Loaded " + loaded_board.name , "Board": loaded_board.description}
    # return database[Board_id].description

@app.get("/Boards/{Board_id}/description")
def read_Board(Board_id: int):
    if Board_id not in database:
        raise HTTPException(status_code=404, detail="Board not found")
    loaded_board = database[Board_id] 
    return loaded_board.description
    # return database[Board_id].description


@app.put("/Boards/{Board_id}")
def update_Board(Board_id: int, Board: Board):
    if Board_id not in database:
        raise HTTPException(status_code=404, detail="Board not found")
    database[Board_id] = Board
    return {"message": "Board updated successfully ", "Board": Board}

@app.delete("/Boards/{Board_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_Board(Board_id: int):
    if Board_id not in database:
        raise HTTPException(status_code=404, detail="Board not found")
    del database[Board_id]
    return {"detail": "Board deleted"}

# Enable CORS for the Next.js frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://192.168.0.234:3000"],  # Adjust this to your Next.js app's URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/run-script/")
async def run_script(button: str = Form(...), RGBvalues: str = Form(None)):
    args = []
    if button == "turnOn":
        strip.turn_led_on()
        message = 'Turn on executed successfully!'
    elif button == "turnOff":
        strip.turn_led_off()
        message = 'Turn off executed successfully!'
    elif button == "changeColor" and RGBvalues:
        RGBval_list = shlex.split(RGBvalues)
        strip.change_color(RGBval_list[0], RGBval_list[1], RGBval_list[2] )
        message = 'Color Changed to: ' + RGBvalues + ' in RGB '

    return JSONResponse(content={"message": message})



def load_Board():
    board_dict = database[1].description

    parsed_dict = json.loads(board_dict)
    print("Deserialized dictionary:", parsed_dict)

    # print(f"Module: {module_name}")
    # for func_name, params in functions:
    #     print(f"  Function: {func_name}")
    #     for param, typ in params:
    #         print(f"    {param}: {typ}")
    #         func = getattr(module, func_name)
    #         execute_based_on_type(func_name, params)