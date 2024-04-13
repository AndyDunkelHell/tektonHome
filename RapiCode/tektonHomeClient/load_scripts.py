import os
import sys
import inspect
import importlib.util
root_path = os.path.dirname(os.path.abspath(__file__))
sys.path.append(root_path)
from func_types import Button, Input
import requests
import json

def list_functions(module):
    functions_list = []
    for name, obj in inspect.getmembers(module, inspect.isfunction):
        sig = inspect.signature(obj)
        params = [(param.name, param.annotation) for param in sig.parameters.values()]
        functions_list.append((name, params))
    return functions_list

def load_module_from_file(module_name, file_path):
    spec = importlib.util.spec_from_file_location(module_name, file_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

def execute_based_on_type(function, params):
    func_type = ""
    for param_name, param_type in params:
        if param_type is Button:
            func_type = "Button"
        elif param_type is Input:
            func_type = "Input"
    return function, func_type
            
def main(scripts_folder):
    # Ensure the scripts folder is in the path
    sys.path.append(scripts_folder)
    modules_dict = {}
    final_desc = []
    # List Python files in the directory
    for filename in os.listdir(scripts_folder):
        if filename.endswith(".py"):
            module_name = filename[:-3]  # Remove '.py' to get the module name
            file_path = os.path.join(scripts_folder, filename)
            module = load_module_from_file(module_name, file_path)
            functions = list_functions(module)
            for func_name, params in functions:
                name, func_type = execute_based_on_type(func_name, params)
                if func_type != "":
                    final_desc.append([name, func_type])
            if len(final_desc) > 0:
                modules_dict[str(module_name)] = final_desc
        final_desc = [] 
    return modules_dict
                    
# Specify the path to your 'scripts' folder
scripts_folder_path = os.path.join(root_path, 'scripts')
tekton_url = "http://192.168.0.234:8000/Boards/"
print(main(scripts_folder_path))
# board_info = main(scripts_folder_path)

def createBoard(board_id:int , board_name:str):
    global board_info
    # Creating an Board
    response = requests.post(tekton_url, json={"id": board_id, "name": board_name, "description":  main(scripts_folder_path)})
    print(response.text)

# Getting an item
def getBoard(board_id:int):
    response = requests.get(tekton_url + board_id + "/description")
    print(response.text)

# # Updating an item
def updateBoard(board_id:int, board_name:str):
    response = requests.put(tekton_url + str(board_id), json={"id": board_id, "name": board_name, "description": main(scripts_folder_path)})
    print(response.text)

# Deleting an item
def deleteBoard(board_id:int):
    response = requests.delete(tekton_url + str(board_id))
    print(response.text)
