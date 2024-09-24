from fastapi import FastAPI, Form, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, HTMLResponse
import shlex
import importlib
import load_scripts as board
import traceback

glob_board_id = 10

app = FastAPI()
@app.get("/", response_class=HTMLResponse)
def read_root():
    return """
<head>
    <title>Webapp Control Panel</title>
</head>
<body>
    <h1>Control Panel</h1>
    <form action="/run-script" method="post">
        <button name="button" value="createBoard" type="post">Create Board</button>
        <button name="button" value="deleteBoard" type="post">Delete Board</button>
        <button name="button" value="updateBoard" type="post">Update Board</button>
        <!-- Add more buttons with different values as needed -->
    </form>
</body>
</html>

    """

# Enable CORS for the Next.js frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://192.168.0.234:3000"],  # Adjust this to your Next.js app's URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.post("/run-function/")
async def run_function(moduleName: str = Form(...), functionName: str = Form(...) ):
    try:
        module = importlib.import_module(f'scripts.{moduleName}')
        func = getattr(module, functionName)
        result = func()
        return {"message": result}
    except Exception as e:
        return {"message": str(type(e)) + traceback.format_exc()}
        

@app.post("/run-function-params/")
async def run_function(moduleName: str = Form(...), functionName: str = Form(...), functionParams:str = Form(None)):
    try:
        module = importlib.import_module(f'scripts.{moduleName}')
        func = getattr(module, functionName)
        result = func(None, functionParams)
        return {"message": result}
    except Exception as e:
        return {"message": str(type(e)) + traceback.format_exc()}
        



@app.post("/run-script/")
async def run_script(button: str = Form(...), updateName: str = Form(None)):
    global glob_board_id
    args = []
    if button == "createBoard":
        board.createBoard(glob_board_id, "DunkelHell_4")
        message = 'Create Board executed successfully!'
    elif button == "deleteBoard":
        board.deleteBoard(glob_board_id)
        message = 'Delete Board executed successfully!'
        print('dele')
    elif button == "updateBoard":
        board.updateBoard(glob_board_id, "DunkelHell_4")
        message = 'Board and Scripts Updated '

    return {"message": message}

@app.get("/deleteBoard/")
async def run_script():
    global glob_board_id
    try:
        board.deleteBoard(glob_board_id)
        return {"message": "Delete Board executed successfully!", "BoardId" : str(glob_board_id)}
    except Exception as e:
        return {"message": str(type(e)) + traceback.format_exc()}
        raise HTTPException(status_code=500, detail=str(e))