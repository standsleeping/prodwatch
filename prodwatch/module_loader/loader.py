import os
import sys
import importlib


def add_project_to_path():
    project_root = os.getcwd()
    if project_root not in sys.path:
        sys.path.insert(0, project_root)


def import_user_modules():
    project_root = os.getcwd()
    for root, dirs, files in os.walk(project_root):
        dirs[:] = [d for d in dirs if not d.startswith(".")]
        for file in files:
            if file.endswith(".py"):
                module_path = os.path.relpath(os.path.join(root, file), project_root)
                module_name = module_path[:-3].replace(os.path.sep, ".")
                print(f"Importing {module_name}")
                try:
                    importlib.import_module(module_name)
                except ImportError:
                    print(f"Failed to import {module_name}")
                except Exception as e:
                    print(f"Error attempting import of {module_name}: {e}")
