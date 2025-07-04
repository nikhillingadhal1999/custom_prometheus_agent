import os
import ast
import importlib.util
from typing import Dict, List, Any


def get_python_files(folder_path: str) -> List[str]:

    return [ os.path.join(root,file) for root, _ , files  in os.walk(folder_path) for file in files if file.endswith('.py') ]

def extract_functions_with_code(file_path: str) -> Dict[str, str]:
    with open(file_path, "r") as file:
        file_content = file.read()  # Read file content once

    tree = ast.parse(file_content)

    functions = {}
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef):
            function_name = node.name
            function_code = ast.get_source_segment(file_content, node)
            functions[function_name] = function_code
    return functions

def analyze_dependencies(function_code: str) -> List[str]:
    try:
        tree = ast.parse(function_code)
    except SyntaxError as e:
        print(f"Syntax error in function code: {e}")
        return []

    dependencies = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            if isinstance(node.func, ast.Name):
                dependencies.append(node.func.id)
            elif isinstance(node.func, ast.Attribute):
                dependencies.append(node.func.attr)

    return dependencies

def find_function_dependencies(file_path: str) -> Dict[str, List[str]]:
    functions_with_code = extract_functions_with_code(file_path)
    function_dependencies = {}

    for func_name, func_code in functions_with_code.items():
        dependencies = analyze_dependencies(func_code)
        function_dependencies[func_name] = dependencies

    return function_dependencies

def topological_sort(dependency_graph: Dict[str, List[str]]) -> List[str]:
    visited = set()
    stack = []

    def visit(node):
        if node not in visited:
            visited.add(node)
            for neighbor in dependency_graph.get(node, []):
                visit(neighbor)
            stack.append(node)

    for node in dependency_graph:
        visit(node)

    return stack[::-1]

def execute_function(file_path: str, function_name: str, attributes: Dict[str,Any]):
    dependencies = find_function_dependencies(file_path)
    sorted_functions = topological_sort(dependencies)

    if function_name not in sorted_functions:
        return

    module_name = os.path.splitext(os.path.basename(file_path))[0]
    spec = importlib.util.spec_from_file_location(module_name, file_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)   

    for func in sorted_functions:
        if hasattr(module, func):
            func_to_call = getattr(module, func)
            if callable(func_to_call):
                try:
                    args = attributes.get(func,())
                    if not isinstance(args,tuple):
                        args = (args,)
                    result = func_to_call(*args)  
                    if func == function_name:
                        return result
                except Exception as e:
                    print(f"Error executing {func}: {e}")

def main(folder_path: str, function_name: str, attributes: Dict[str,Any]):
    python_files = get_python_files(folder_path)

    for file_path in python_files:
        return execute_function(file_path, function_name,attributes)


def read_function_file(custom_path):    
    with open(custom_path,'r') as file:
        lines = file.readlines()
    return lines

def get_env_dir():
    current_path = os.getcwd()
    return os.path.abspath(os.path.join(current_path,'env/bin/activate'))

def install_requirements(requirements_path):
    env_dir = get_env_dir()
    command = f"source {env_dir}; pip3 install -r {requirements_path}"
    os.system(command)

def load_variable_from_file(file_path, variable_name="ARGS"):
    spec = importlib.util.spec_from_file_location("module_name", file_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return getattr(module, variable_name, None)

def execute_functions(folder_path,file_path):
    functions = read_function_file(file_path)
    args= { 'collect_disk_metrics' : ()}
    result = [ main(folder_path, function_name.strip('\n'), args) for function_name in functions ]
    return result