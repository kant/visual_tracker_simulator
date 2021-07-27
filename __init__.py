# --------------------------------------------------------------------------------
# ADDON DESCRIPTION
# --------------------------------------------------------------------------------

bl_info = {
    "name": "Visual Tracker Simulator",
    'author': 'Luka Kuzman',
    "version" : (0, 2, 1),
    "blender": (2, 92, 0),
    "location" : "View3D > Sidebar > Edit Tab",
    "description" : "Gets text file with some parameters as an input, export rendered scene and a mask.",
    "category": "Render",
}

# --------------------------------------------------------------------------------
# IMPORTS AND GLOBAL VARIABLES
# --------------------------------------------------------------------------------

import bpy
import math
import os
import random
from bpy.types import (Panel, Operator, PropertyGroup)
from bpy.props import (StringProperty, BoolProperty, IntProperty, FloatProperty)

file_path = ""
masked_object = 1

class RandomizationProperties(PropertyGroup):
    generated_density: IntProperty(
        name = "Generated density",
        description="Generated density:",
        default = 5,
        min = 0
        )

    camera_distance: FloatProperty(
        name = "Camera distance",
        description = "Camera distance",
        default = 5,
        min = 0
        )
    
    following_object: StringProperty(
        name = "Object to follow",
        description=":",
        default="",
        maxlen=1024
        )

# --------------------------------------------------------------------------------
# RANDOMIZATION OF PARAMETERS FILES
# --------------------------------------------------------------------------------

# TODO
class RandomizeControlOperator(Operator):
    """Randomize Control"""
    bl_idname = "object.randomize_control"
    bl_label = "Randomize control"

    def execute(self, context):
        # Delete all the objects that the program might have generated previously
        self.delete_generated_controler()

        # Determine which object to follow with a camera randomly
        self.choose_following_object()

        # Randomize parameters
        self.camera_control()
        self.generated_density_control()
        self.child_of_control()
        self.fog_control()
        self.animation_control()
        self.light_offset_control()

        return {'FINISHED'}

    def delete_generated_controler(self):
        print("Deleted previously generated objects")
        for object in bpy.data.collections['GeneratedObjects'].all_objects:
            bpy.data.objects.remove(object, do_unlink=True)

    # Choose following object
    def choose_following_object(self):
        global masked_object
        masked_object = random.randint(1, len(bpy.context.scene.view_layers) - 1)

        masked_object_name = bpy.context.scene.view_layers[masked_object].name

        # Count how many paths the object has
        number_of_paths = 0
        for object in bpy.data.collections['CameraParents'].all_objects:
            if masked_object_name in object.name:
                number_of_paths += 1

        choose_random = random.randint(0, number_of_paths - 1)

        camera = bpy.context.scene.camera

        # Make the followed object the center of the camera
        for object in bpy.data.collections['MainObjects'].all_objects:
            if masked_object_name == object.name:
                for constraint in camera.constraints:
                    if constraint.type == 'TRACK_TO':
                        constraint.target = object

        # Choose the path at random out of those
        current_object = 0
        for object in bpy.data.collections['CameraParents'].all_objects:
            if masked_object_name in object.name:
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
    def camera_control(self):
        camera = bpy.context.scene.camera

        # TODO - changed hardcoded values
        max_dist_x = 10
        max_dist_y = 10
        max_dist_z = 10
        
        # Move the camera from the path by a certain ammount
        camera.location[0] = float(random.uniform(-max_dist_x, max_dist_x))
        camera.location[1] = float(random.uniform(-max_dist_y, max_dist_y))
        camera.location[2] = float(random.uniform(-max_dist_z, max_dist_z))

    # Object density conrol
    def generated_density_control(self):
        # TODO - change hardcoded value
        max_density = 10
        generate_density = random.uniform(0, max_density)

        # First delete all the objects that were previously there
        for object in bpy.data.collections['GeneratedObjects'].all_objects:
            bpy.data.objects.remove(object, do_unlink=True)

        layer_collection = bpy.data.collections['GeneratedObjects']

        # Duplicate objects as given by the txt file
        for i in range(int(generate_density)):
            # Choose random object to duplicate
            choose_random = random.randint(0, len(bpy.data.collections['GeneratingObjects'].all_objects) - 1)
            index = 0

            for object in bpy.data.collections['GeneratingObjects'].all_objects:
                if index == choose_random: 
                    generated_object = object.copy()

                    action = generated_object.animation_data.action
                    generated_object.animation_data.action = action.copy()

                    generated_animation_legth = generated_object.animation_data.action.fcurves[0].keyframe_points[1].co[0] - generated_object.animation_data.action.fcurves[0].keyframe_points[0].co[0]
                    offset = int((i + 1)*generated_animation_legth/(int(generate_density)+1))
                    print(offset)

                    # Setting which path the object should follow
                    number_of_paths = len(bpy.data.collections['FollowingPaths'].all_objects)
                    choose_random_path = random.randint(0, number_of_paths - 1)

                    current_path = 0
                    for path in bpy.data.collections['FollowingPaths'].all_objects:
                        if current_path == choose_random_path:
                            for constraint in generated_object.constraints:
                                if constraint.type == 'FOLLOW_PATH':
                                    constraint.target = path

                        current_path += 1

                    # Adjusting the path data
                    generated_object.animation_data.action.fcurves[0].keyframe_points[0].co[0] = generated_object.animation_data.action.fcurves[0].keyframe_points[0].co[0] - offset
                    generated_object.animation_data.action.fcurves[0].keyframe_points[1].co[0] = generated_object.animation_data.action.fcurves[0].keyframe_points[1].co[0] - offset

                    fc = generated_object.animation_data.action.fcurves[0]

                    for mod in fc.modifiers:
                        fc.modifiers.remove(mod)

                    fc.modifiers.new(type='CYCLES')

                    layer_collection.objects.link(generated_object)
                index += 1

    def child_of_control(self):
        camera = bpy.context.scene.camera

        following_objects = ["_none_"]

        for collection in bpy.data.collections:
            if collection.name == "MainObjects":
                for i in range(0, len(collection.children)):
                    following_objects.append(collection.children[i].name)
        
        random_index = int(random.uniform(0, len(following_objects)))

        object_name = following_objects[random_index]

        if(object_name == "_none_"):
            target_object = None
        else:
            target_object = bpy.data.objects[object_name]

        for constraint in camera.constraints:
            if constraint.type == 'FOLLOW_PATH':
                constraint.target = target_object

    def fog_control(self):
        fog_mat = bpy.data.materials['FogCube']
        fog_mat.use_nodes = True
        nodes = fog_mat.node_tree.nodes

        volume_node = nodes.get("Volume Scatter")


        # TODO - change hardoced value
        fog = False
        if random.uniform(0, 10) < 8:
            fog = True

        if fog == True:
            volume_node.inputs[1].default_value = 0.01 # inputs[1] refers to density
        else:
            volume_node.inputs[1].default_value = 0

    def animation_control(self):
        # TODO - change hardcoded value
        length = random.uniform(0, 1000)
        animation_length = int(length)

        scene = bpy.context.scene

        random_start = int(random.uniform(0, animation_length))
        scene.frame_start = random_start
        scene.frame_end = random_start + animation_length

    def light_offset_control(self):
        # "Shader NodetreeAction" is the node controlling the intensity of light
        # Make sure that the action controling it is named so
        light_cycle_length = bpy.data.actions["Shader NodetreeAction"].fcurves[0].keyframe_points[2].co[0] - bpy.data.actions["Shader NodetreeAction"].fcurves[0].keyframe_points[0].co[0]

        offset_length = random.uniform(0, light_cycle_length)

        # Move the keyframes acordingly
        bpy.data.actions["Shader NodetreeAction"].fcurves[0].keyframe_points[0].co[0] = -offset_length
        bpy.data.actions["Shader NodetreeAction"].fcurves[0].keyframe_points[1].co[0] = light_cycle_length / 2 - offset_length
        bpy.data.actions["Shader NodetreeAction"].fcurves[0].keyframe_points[2].co[0] = light_cycle_length - offset_length

        fc = bpy.data.actions["Shader NodetreeAction"].fcurves[0]

        for mod in fc.modifiers:
            fc.modifiers.remove(mod)

        fc.modifiers.new(type='CYCLES')


# --------------------------------------------------------------------------------
# LOADING PARAMETERS FROM FILES
# --------------------------------------------------------------------------------

class SceneControlOperator(Operator):
    """Scene Control"""
    bl_idname = "object.scene_control"
    bl_label = "Scene control"

    def execute(self, context):
        # Delete all the objects that the program might have generated previously
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
            self.camera_control(values[1], values[2], values[3])
        elif values[0] == "generate_density":
            print("Generated objects density")
            self.generated_density_control(values[1])
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
        elif values[0] == "light_offset":
            print("Light offset")
            self.light_offset_control(values[1])
        else:
            print("Unassigned")

    def delete_generated_controler(self):
        print("Deleted previously generated objects")
        for object in bpy.data.collections['GeneratedObjects'].all_objects:
            bpy.data.objects.remove(object, do_unlink=True)

    # Choose following object
    def choose_following_object(self):
        global masked_object
        masked_object = random.randint(1, len(bpy.context.scene.view_layers) - 1)

        masked_object_name = bpy.context.scene.view_layers[masked_object].name

        # Count how many paths the object has
        number_of_paths = 0
        for object in bpy.data.collections['CameraParents'].all_objects:
            if masked_object_name in object.name:
                number_of_paths += 1

        choose_random = random.randint(0, number_of_paths - 1)

        camera = bpy.context.scene.camera

        # Make the followed object the center of the camera
        for object in bpy.data.collections['MainObjects'].all_objects:
            if masked_object_name == object.name:
                for constraint in camera.constraints:
                    if constraint.type == 'TRACK_TO':
                        constraint.target = object

        # Choose the path at random out of those
        current_object = 0
        for object in bpy.data.collections['CameraParents'].all_objects:
            if masked_object_name in object.name:
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
    def camera_control(self, x, y, z):
        camera = bpy.context.scene.camera
        
        # Move the camera from the path by a certain ammount
        camera.location[0] = float(x)
        camera.location[1] = float(y)
        camera.location[2] = float(z)

    # Object density conrol
    def generated_density_control(self, generate_density):
        # First delete all the objects that were previously there
        for object in bpy.data.collections['GeneratedObjects'].all_objects:
            bpy.data.objects.remove(object, do_unlink=True)

        layer_collection = bpy.data.collections['GeneratedObjects']

        # Duplicate objects as given by the txt file
        for i in range(int(generate_density)):
            # Choose random object to duplicate
            choose_random = random.randint(0, len(bpy.data.collections['GeneratingObjects'].all_objects) - 1)
            index = 0

            for object in bpy.data.collections['GeneratingObjects'].all_objects:
                if index == choose_random: 
                    generated_object = object.copy()

                    action = generated_object.animation_data.action
                    generated_object.animation_data.action = action.copy()

                    generated_animation_legth = generated_object.animation_data.action.fcurves[0].keyframe_points[1].co[0] - generated_object.animation_data.action.fcurves[0].keyframe_points[0].co[0]
                    offset = int((i + 1)*generated_animation_legth/(int(generate_density)+1))
                    print(offset)

                    # Setting which path the object should follow
                    number_of_paths = len(bpy.data.collections['FollowingPaths'].all_objects)
                    choose_random_path = random.randint(0, number_of_paths - 1)

                    current_path = 0
                    for path in bpy.data.collections['FollowingPaths'].all_objects:
                        if current_path == choose_random_path:
                            for constraint in generated_object.constraints:
                                if constraint.type == 'FOLLOW_PATH':
                                    constraint.target = path

                        current_path += 1

                    # Adjusting the path data
                    generated_object.animation_data.action.fcurves[0].keyframe_points[0].co[0] = generated_object.animation_data.action.fcurves[0].keyframe_points[0].co[0] - offset
                    generated_object.animation_data.action.fcurves[0].keyframe_points[1].co[0] = generated_object.animation_data.action.fcurves[0].keyframe_points[1].co[0] - offset

                    fc = generated_object.animation_data.action.fcurves[0]

                    for mod in fc.modifiers:
                        fc.modifiers.remove(mod)

                    fc.modifiers.new(type='CYCLES')

                    layer_collection.objects.link(generated_object)
                index += 1

    # TODO - Currently not used
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

        random_start = int(random.uniform(0, animation_length))
        scene.frame_start = random_start
        scene.frame_end = random_start + animation_length

    def light_offset_control(self, offset_frames):
        offset_lenght = int(offset_frames)

        # "Shader NodetreeAction" is the node controlling the intensity of light
        # Make sure that the action controling it is named so
        light_cycle_length = bpy.data.actions["Shader NodetreeAction"].fcurves[0].keyframe_points[2].co[0] - bpy.data.actions["Shader NodetreeAction"].fcurves[0].keyframe_points[0].co[0]

        # Move the keyframes acordingly
        bpy.data.actions["Shader NodetreeAction"].fcurves[0].keyframe_points[0].co[0] = -offset_lenght
        bpy.data.actions["Shader NodetreeAction"].fcurves[0].keyframe_points[1].co[0] = light_cycle_length / 2 - offset_lenght
        bpy.data.actions["Shader NodetreeAction"].fcurves[0].keyframe_points[2].co[0] = light_cycle_length - offset_lenght

        fc = bpy.data.actions["Shader NodetreeAction"].fcurves[0]

        for mod in fc.modifiers:
            fc.modifiers.remove(mod)

        fc.modifiers.new(type='CYCLES')
    
    # ----------------------------------------------------------------------------------------------



class DeleteGeneratedOperator(Operator):
    """Delete Generated"""
    bl_idname = "object.delete_generated"
    bl_label = "Delete generated"

    def execute(self, context):
        for object in bpy.data.collections['GeneratedObjects'].all_objects:
            bpy.data.objects.remove(object, do_unlink=True)

        return {'FINISHED'}

# ----------------------------------------------------------------------------------------------
# RENDERING THE SCENE AND ITS MASK
# ----------------------------------------------------------------------------------------------

class RenderSceneOperator(Operator):
    """Render Scene"""
    bl_idname = "object.render_scene"
    bl_label = "Render scene"
    
    def execute(self, context):
        # Render scene
        self.render_scene()

        return {'FINISHED'}

    def render_scene(self):
        bpy.context.scene.use_nodes = True
        tree = bpy.context.scene.node_tree

        # Clearning default nodes
        for node in tree.nodes:
            tree.nodes.remove(node)

        # Create render output node
        default_render_layer = tree.nodes.new(type='CompositorNodeRLayers')
        default_render_layer.layer = bpy.context.scene.view_layers[0].name
        default_render_layer.location = 0,0

        output_node = tree.nodes.new(type='CompositorNodeComposite')
        output_node.location = 400,0

        links = tree.links
        link = links.new(default_render_layer.outputs[0], output_node.inputs[0])

        bpy.ops.render.render('INVOKE_DEFAULT', animation=True)

class RenderMaskOperator(Operator):
    """Render Mask"""
    bl_idname = "object.render_mask"
    bl_label = "Render mask"
    
    def execute(self, context):
        # Render mask
        self.render_mask()

        return {'FINISHED'}

    def render_mask(self):
        # Change render engine to Eevee to render the mask
        bpy.context.scene.render.engine = 'BLENDER_EEVEE'

        bpy.context.scene.use_nodes = True
        tree = bpy.context.scene.node_tree

        # Clearning default nodes
        for node in tree.nodes:
            tree.nodes.remove(node)

        # Create render output node
        default_render_layer = tree.nodes.new(type='CompositorNodeRLayers')
        global masked_object
        default_render_layer.layer = bpy.context.scene.view_layers[masked_object].name
        default_render_layer.location = 0,0

        alpha_over_node = tree.nodes.new(type='CompositorNodeAlphaOver')
        alpha_over_node.location = 400,0

        links = tree.links
        link = links.new(default_render_layer.outputs[1], alpha_over_node.inputs[2])

        blur_node = tree.nodes.new(type='CompositorNodeBlur')
        blur_node.location = 800,0

        links = tree.links
        link = links.new(alpha_over_node.outputs[0], blur_node.inputs[0])

        output_node = tree.nodes.new(type='CompositorNodeComposite')
        output_node.location = 1200,0

        links = tree.links
        link = links.new(blur_node.outputs[0], output_node.inputs[0])

        bpy.ops.render.render('INVOKE_DEFAULT', animation=True)

# ----------------------------------------------------------------------------------------------
# FILE LOADING
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
        layout.label(text="Random scene generate:")
        col = layout.column(align=True)
        col.operator(RandomizeControlOperator.bl_idname, text="Randomize", icon="PLAY")
        layout.label(text="Randomization parameters limits:")

        randomizer_tool = context.scene.my_tool
        layout.prop(randomizer_tool, "camera_distance")
        layout.prop(randomizer_tool, "following_object")
        layout.prop(randomizer_tool, "generated_density")


        layout.label(text="Generate from file:")
        col = layout.column(align=True)
        file_tool = context.scene.file_tool
        col.prop(file_tool, "path")
        file_path = bpy.path.abspath("//") + file_tool.path
        col.operator(SceneControlOperator.bl_idname, text="Load", icon="PLAY")

        layout.label(text="Scene generation options:")
        col = layout.column(align=True)
        col.operator(DeleteGeneratedOperator.bl_idname, text="Delete Generated", icon="TRASH")

        layout.label(text="Render scene:")
        col = layout.column(align=True)
        col.operator(RenderSceneOperator.bl_idname, text="Render Scene", icon="SEQUENCE")
        col.operator(RenderMaskOperator.bl_idname, text="Render Mask", icon="CLIPUV_DEHLT")



classes = (
    RandomizeControlOperator,
    RandomizationProperties,
    SceneControlOperator,
    DeleteGeneratedOperator,
    RenderSceneOperator,
    RenderMaskOperator,
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
    bpy.types.Scene.my_tool = bpy.props.PointerProperty(type=RandomizationProperties)


def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)
    del bpy.types.Scene.file_tool
    del bpy.types.Scene.my_tool

if __name__ == "__main__":
    register()