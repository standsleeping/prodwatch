import os
import sys
import importlib
import logging

logger = logging.getLogger(__name__)


def add_project_to_path() -> None:
    project_root = os.getcwd()
    if project_root not in sys.path:
        sys.path.insert(0, project_root)
        logger.debug(f"Added {project_root} to Python path")


def import_user_modules() -> None:
    project_root = os.getcwd()
    for root, dirs, files in os.walk(project_root):
        dirs[:] = [d for d in dirs if not d.startswith(".")]
        for file in files:
            if file.endswith(".py"):
                module_path = os.path.relpath(os.path.join(root, file), project_root)
                module_name = str(module_path[:-3]).replace(os.path.sep, ".")
                logger.info(f"Importing module: {module_name}")
                try:
                    importlib.import_module(module_name)
                except ImportError:
                    logger.error(f"Failed to import module: {module_name}")
                except Exception as e:
                    logger.error(f"Error importing module {module_name}: {e}")
