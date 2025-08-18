# Node: Project Director v1.0

import os

class ProjectDirector_Akki:
    """
    A simple UI node to define the project name and output a base path
    for all project-related file saving operations.
    """
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "project_name": ("STRING", {"default": "Project01"}),
                "base_output_folder": ("STRING", {"default": "output/AKKILLM"}),
            }
        }

    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("project_path",)
    FUNCTION = "get_project_path"
    CATEGORY = "AkkiNodes/FileIO"

    def get_project_path(self, project_name, base_output_folder):
        # Sanitize project name to be a valid folder name
        clean_project_name = "".join(c for c in project_name if c.isalnum() or c in (' ', '_')).rstrip()
        project_path = os.path.join(base_output_folder, clean_project_name)
        return (project_path,)

NODE_CLASS_MAPPINGS = {"ProjectDirector-Akki": ProjectDirector_Akki}
NODE_DISPLAY_NAME_MAPPINGS = {"ProjectDirector-Akki": "Project Director v1.0 - Akki"}