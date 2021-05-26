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
import os

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
        values = current_line.split(" ")

        if values[0] == "#":
            print("Comment")
        elif values[0] == "camera":
            print("Camera control")
            self.camera_control(values[1], values[2], values[3], values[4], values[5], values[6])
        elif values[0] == "vehicle_density":
            print("Vehicle density")
            self.vehicle_density_control(values[1])
        elif values[0] == "light":
            print("Light control")
            self.light_control(values[1], values[2], values[3])
        elif values[0] == "child_of":
            print("Follower control")
            self.child_of_control(values[1])
        else:
            print("other stuff at the moment")

    # ----------------------------------------------------------------------------------------------
    # STUFF THAT CONTROLS THE SCENE
    # ----------------------------------------------------------------------------------------------

    # Camera control
    def camera_control(self, x, y, z, rx, ry, rz):
        camera = bpy.context.scene.camera
        
        camera.location[0] = float(x)
        camera.location[1] = float(y)
        camera.location[2] = float(z)
        
        camera.rotation_euler[0] = math.radians(float(rx))
        camera.rotation_euler[1] = math.radians(float(ry))
        camera.rotation_euler[2] = math.radians(float(rz))

    # Vehicle density conrol
    def vehicle_density_control(self, traffic_density):
        # TODO
        return

    def light_control(self, rx, ry, rz):
        light = bpy.data.objects['Sun']

        light.rotation_euler[0] = math.radians(float(rx))
        light.rotation_euler[1] = math.radians(float(ry))
        light.rotation_euler[2] = math.radians(float(rz))

        light = bpy.data.lights['Sun']

        # Here I used math to calculate how bright the light should be depending on the direction
        light.energy = max(math.cos(90 - abs(float(rx))), math.cos(90 - abs(float(ry))))

        return
    
    def child_of_control(self, object_name):
        camera = bpy.context.scene.camera

        if(object_name == "_none_"):
            target_object = None
        else:
            target_object = bpy.data.objects[object_name]

        for constraint in camera.constraints:
            if constraint.type == 'CHILD_OF':
                constraint.target = target_object
    
    # ----------------------------------------------------------------------------------------------



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
        file_path = bpy.path.abspath("//") + file_tool.path
        print(file_path)
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