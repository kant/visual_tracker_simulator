# --------------------------------------------------------------------------------
# ADDON DESCRIPTION
# --------------------------------------------------------------------------------

bl_info = {
    "name": "Visual Tracker Simulator",
    'author': 'Luka Kuzman',
    "version" : (0, 0, 1),
    "blender": (2, 92, 0),
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
import random

file_path = ""

class SceneControlOperator(Operator):
    """Scene Control"""
    bl_idname = "object.scene_control"
    bl_label = "Scene control"

    def execute(self, context):
        # TODO - change so that it becomes dynamic, currently it is static

        # First I delete all the objects that the program might have generated previously
        self.delete_generated_controler()

        # Determine which object to follow with a camera randomly
        self.choose_following_object()

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
            # Temporarily disabled, to not move camera from it's path
            #self.camera_control(values[1], values[2], values[3], values[4], values[5], values[6])
        elif values[0] == "vehicle_density":
            print("Vehicle density")
            self.vehicle_density_control(values[1])
        elif values[0] == "light":
            print("Light control")
            self.light_control(values[1], values[2], values[3])
        elif values[0] == "child_of":
            print("Follower control")
            self.child_of_control(values[1])
        elif values[0] == "fog":
            print("Fog control")
            self.fog_control(values[1])
        elif values[0] == "animation_length":
            print("Animation length")
            self.animation_control(values[1])
        else:
            print("Unassigned")

    def delete_generated_controler(self):
        print("Deleted previously generated objects")
        for object in bpy.data.collections['GeneratedObjects'].all_objects:
            bpy.data.objects.remove(object, do_unlink=True)

    # Choose following object
    def choose_following_object(self):
        number_of_parents = len(bpy.data.collections['CameraParents'].all_objects)
        choose_random = random.randint(0, number_of_parents)

        camera = bpy.context.scene.camera

        current_object = 0
        for object in bpy.data.collections['CameraParents'].all_objects:
            if current_object == choose_random:
                for constraint in camera.constraints:
                    if constraint.type == 'FOLLOW_PATH':
                        constraint.target = object
                        return

            current_object += 1


    # ----------------------------------------------------------------------------------------------
    # STUFF THAT CONTROLS THE SCENE
    # ----------------------------------------------------------------------------------------------

    # Camera control
    def camera_control(self, x, y, z, rx, ry, rz):
        camera = bpy.context.scene.camera
        
        camera.location[0] = float(x)
        camera.location[1] = float(y)
        camera.location[2] = float(z)
        
        #camera.rotation_euler[0] = math.radians(float(rx))
        #camera.rotation_euler[1] = math.radians(float(ry))
        #camera.rotation_euler[2] = math.radians(float(rz))
        
        # Instead of taking these inputs, I rotate the camera to look at the object
        sign = 1
        if float(y) < 0:
            sign = 0
        camera.rotation_euler[0] = math.radians(90 - math.atan(float(z)/math.sqrt(float(x) * float(x) + float(y) * float(y))) / math.pi * 180)
        camera.rotation_euler[2] = math.radians((math.atan(-float(x)/float(y))/math.pi * 180) + 180 * sign)

    # Vehicle density conrol
    def vehicle_density_control(self, traffic_density):
        traffic_car = bpy.data.objects['Nissan']

        layer_collection = bpy.data.collections['GeneratedObjects']

        # Duplicate cars as given by the txt file
        for i in range(int(traffic_density)):
            car = traffic_car.copy()

            action = car.animation_data.action
            car.animation_data.action = action.copy()

            car.animation_data.action = None

            layer_collection.objects.link(car)

    def light_control(self, rx, ry, rz):
        light = bpy.data.objects['Sun']

        # Setting the angle of the sun
        light.rotation_euler[0] = math.radians(float(rx))
        light.rotation_euler[2] = math.radians(float(rz))

        light = bpy.data.lights['Sun']

        # Here I used math to calculate how bright the light should be depending on the direction
        strength = math.cos(abs(float(rx))*math.pi/180)
        light.energy = strength

        # Setting the strength of HDR to the same value
        world = bpy.data.worlds['World']
        world.use_nodes = True
        surface = world.node_tree.nodes['Background']
        surface.inputs[1].default_value = strength
    
    def child_of_control(self, object_name):
        camera = bpy.context.scene.camera

        if(object_name == "_none_"):
            target_object = None
        else:
            target_object = bpy.data.objects[object_name]

        for constraint in camera.constraints:
            if constraint.type == 'FOLLOW_PATH':
                constraint.target = target_object

    def fog_control(self, fog):
        fog_mat = bpy.data.materials['FogCube']
        fog_mat.use_nodes = True
        nodes = fog_mat.node_tree.nodes

        volume_node = nodes.get("Volume Scatter")

        if fog == "True":
            volume_node.inputs[1].default_value = 0.01 # inputs[1] refers to density
        else:
            volume_node.inputs[1].default_value = 0

    def animation_control(self, length):
        animation_length = int(length)

        scene = bpy.context.scene
        scene.frame_end = animation_length
    
    # ----------------------------------------------------------------------------------------------


class DeleteGeneratedOperator(Operator):
    """Delete Generated"""
    bl_idname = "object.delete_generated"
    bl_label = "Delete generated"

    def execute(self, context):
        for object in bpy.data.collections['GeneratedObjects'].all_objects:
            bpy.data.objects.remove(object, do_unlink=True)

        return {'FINISHED'}


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
        layout.label(text="Scene generation options:")
        col = layout.column(align=True)
        col.operator(DeleteGeneratedOperator.bl_idname, text="Delete Generated", icon="TRASH")



classes = (
    SceneControlOperator,
    DeleteGeneratedOperator,
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