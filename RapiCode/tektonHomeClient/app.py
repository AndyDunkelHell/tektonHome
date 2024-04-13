from fastapi import FastAPI, Form, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, HTMLResponse
import shlex
import importlib
import load_scripts as board

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
        return JSONResponse(content={"message": result})
    except Exception as e:
         raise HTTPException(status_code=500, detail=str(e))

@app.post("/run-function-params/")
async def run_function(moduleName: str = Form(...), functionName: str = Form(...), functionParams:str = Form(None)):
    # print(moduleName)
    # print(functionName)
    # print(functionParams)
    # module = importlib.import_module(f'scripts.{moduleName}')
    # func = getattr(module, functionName)
    # result = func(None, button)
    # print(func)
    # print(result)
    try:
        module = importlib.import_module(f'scripts.{moduleName}')
        func = getattr(module, functionName)
        result = func(None, functionParams)
        return JSONResponse(content={"message": result})
    except Exception as e:
         raise HTTPException(status_code=500, detail=str(e))

# board.createBoard(1, "DunkelHell_4")
# board.deleteBoard(1)


@app.post("/run-script/")
async def run_script(button: str = Form(...), updateName: str = Form(None)):
    args = []
    if button == "createBoard":
        board.createBoard(1, "DunkelHell_4")
        message = 'Create Board executed successfully!'
    elif button == "deleteBoard":
        board.deleteBoard(1)
        message = 'Delete Board executed successfully!'
    elif button == "updateBoard":
        board.updateBoard(1, "DunkelHell_4")
        message = 'Board and Scripts Updated '

    return {"message": message}

