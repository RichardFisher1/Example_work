import ast
import importlib.util


def get_class_names_from_file(file_path):
    class_names = []

    # Open the file and read its contents
    with open(file_path, "r") as file:
        file_content = file.read()

    # Parse the file content into an Abstract Syntax Tree (AST)
    tree = ast.parse(file_content)

    # Iterate through the nodes of the AST to find class definitions
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef):
            class_names.append(node.name)

    return class_names

def import_class_from_file(class_name, file_path):
        """Dynamically import a class from a specified file."""
        module_name = file_path.split('/')[-1].replace('.py', '')  # Module name
        spec = importlib.util.spec_from_file_location(module_name, file_path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)

        if hasattr(module, class_name):
            class_ref = getattr(module, class_name)
            globals()[class_name] = class_ref  # Add class to globals
            return class_ref
        else:
            raise ImportError(f"Class {class_name} not found in {file_path}")