# --------------------------------------------------------------------------------
# ADDON DESCRIPTION
# --------------------------------------------------------------------------------

bl_info = {
    "name": "Visual Tracker Simulator",
    'author': 'Luka Kuzman',
    "version" : (0, 0, 1),
    "blender": (2, 80, 0),
    "location" : "View3D > Sidebar > Edit Tab",
    "description" : "Gets text file with some parameters as an input, export rendered scene and a mask.",
    "category": "Render",
}

# --------------------------------------------------------------------------------
# CODE
# --------------------------------------------------------------------------------

import bpy
from bpy.types import (Panel, Operator)
import math

file_path = ""

class SceneControlOperator(Operator):
    """Scene Control"""
    bl_idname = "object.scene_control"
    bl_label = "Scene control"

    def execute(self, context):
        # TODO - change so that it becomes dynamic, currently it is static
        with open(file_path) as f:
            lines = f.readlines()
            
            for i in range(0, len(lines)):
                self.determine_command(lines[i])

        return {'FINISHED'}
    
    # File read
    def determine_command(self, current_line):
        if current_line[0] == "#":
            print("Comment")
        elif current_line[0] == "c":
            print("Camera control")
            values = current_line.split(" ")
            self.camera_control(values[1], values[2], values[3], values[4], values[5], values[6])
        else:
            print("other stuff at the moment")

    # Camera control
    def camera_control(self, x, y, z, rx, ry, rz):
        camera = bpy.context.scene.camera
        
        camera.location[0] = float(x)
        camera.location[1] = float(y)
        camera.location[2] = float(z)
        
        camera.rotation_euler[0] = math.radians(float(rx))
        camera.rotation_euler[1] = math.radians(float(ry))
        camera.rotation_euler[2] = math.radians(float(rz))



class FileSettings(bpy.types.PropertyGroup):
    path : bpy.props.StringProperty(name="File path",
                                        description="",
                                        default="",
                                        maxlen=1024,
                                        subtype="FILE_PATH")



class FileSelector(Operator):
    bl_idname = "object.file_selector"
    bl_label = "File select"

    filepath = bpy.props.StringProperty(subtype="FILE_PATH")

    def execute(self, context):
        display = "filepath= "+self.filepath  
        print(display)
        return {'FINISHED'}
 
    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}



class SceneControlPanel(Panel):
    bl_idname = "object.scene_control_panel"
    bl_label = "Visual Tracker Simulator"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "Visual Tracker Simulator"
    bl_context = "objectmode"

    @classmethod
    def poll(cls, context):
        return context.object is not None

    def draw(self, context):
        global file_path
        
        layout = self.layout
        layout.label(text="Scene control:")

        col = layout.column(align=True)
        file_tool = context.scene.file_tool
        col.prop(file_tool, "path")
        print("TEST START")
        print(file_tool.path)
        print("TEST END")
        file_path = file_tool.path
        col.operator(SceneControlOperator.bl_idname, text="Run", icon="TRIA_RIGHT")
        # layout.seperator()



classes = (
    SceneControlOperator,
    SceneControlPanel,
    FileSettings,
    FileSelector
)

# --------------------------------------------------------------------------------
# CLASS REGISTRATION
# --------------------------------------------------------------------------------

def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    bpy.types.Scene.file_tool = bpy.props.PointerProperty(type=FileSettings)


def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)
    del bpy.types.Scene.file_tool 

if __name__ == "__main__":
    register()