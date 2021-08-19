# --------------------------------------------------------------------------------
# ADDON DESCRIPTION
# --------------------------------------------------------------------------------

bl_info = {
    "name": "Visual Tracker Simulator",
    'author': 'Luka Kuzman',
    "version" : (0, 2, 2),
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



# --------------------------------------------------------------------------------
# RANDOMIZATION OF PARAMETERS
# --------------------------------------------------------------------------------

# Default value for the following object
following_object = ""
masked_object = 1

# Default values for parameters
camera_distance = 5
track_to_distance = 5
generated_density = 5
animation_length_randomized = 250
fog_likelyhood = 0.8



# Values that are gonna be modified trough Blender's UI
class RandomizationProperties(PropertyGroup):
    camera_distance: FloatProperty(
        name = "Camera distance",
        description = "Camera distance",
        default = 5,
        min = 0,
        step = 1
        )

    track_to_distance: FloatProperty(
        name = "Track-to distance",
        description = "Track-to distance",
        default = 5,
        min = 0,
        step = 1
        )

    generated_density: IntProperty(
        name = "Generated density",
        description="Generated density",
        default = 5,
        min = 0
        )
    
    following_object: StringProperty(
        name = "Object to follow",
        description=":",
        default="",
        maxlen=1024
        )

    fog_likelyhood: FloatProperty(
        name = "Fog likelyhood",
        description = "Fog likelyhood",
        default = 0.8,
        min = 0,
        max = 1,
        step = 0.1
        )

    animation_length_randomized: IntProperty(
        name = "Animation length",
        description="Animation length",
        default = 250,
        min = 0
        )



# Randomization of parameters
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
        self.track_to_control()
        self.generated_density_control()
        self.fog_control()
        self.animation_control()
        self.light_offset_control()

        return {'FINISHED'}

    def delete_generated_controler(self):
        print("Deleted previously generated objects")
        for object in bpy.data.collections['GeneratedObjects'].all_objects:
            bpy.data.objects.remove(object, do_unlink=True)

    # ----------------------------------------------------------------------------------------------
    # STUFF THAT CONTROLS THE SCENE
    # ----------------------------------------------------------------------------------------------

    # Choose following object
    def choose_following_object(self):
        global following_object
        global masked_object

        mask_index = 0

        # Check if the user has chosen a particular object to follow
        # If an arguement was given, try getting the object with that name
        if following_object != "":
            layer_index = 0
            for layer in bpy.context.scene.view_layers:
                if layer.name == following_object:
                    mask_index = layer_index
                layer_index += 1
            # If an object with the given name was not found, choose a random object to follow
            if mask_index == 0:
                masked_object = random.randint(1, len(bpy.context.scene.view_layers) - 1)
            # If an object with the given name was found, set that one as the one to follow
            else:
                masked_object = mask_index
        else:
            masked_object = random.randint(1, len(bpy.context.scene.view_layers) - 1)

        masked_object_name = bpy.context.scene.view_layers[masked_object].name

        # Set the name randomly chosen object to follow to a global variable so that it can be used elsewhere
        following_object = masked_object_name

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

    # Camera control
    def camera_control(self):
        camera = bpy.context.scene.camera

        global camera_distance
        max_dist = camera_distance

        max_dist_x = max_dist
        max_dist_y = max_dist
        max_dist_z = max_dist
        
        # Move the camera from the path by a certain ammount
        camera.location[0] = float(random.uniform(-max_dist_x, max_dist_x))
        camera.location[1] = float(random.uniform(-max_dist_y, max_dist_y))
        camera.location[2] = float(random.uniform(0, max_dist_z))

    # Track-to control
    def track_to_control(self):
        global following_object
        global track_to_distance

        collection = bpy.data.collections[following_object]

        for object in collection.all_objects:
            if object.name == following_object:
                track_to_object = object

        max_dist = track_to_distance

        max_dist_x = max_dist
        max_dist_y = max_dist
        max_dist_z = max_dist
        
        # Move the camera from the path by a certain ammount
        track_to_object.location[0] = float(random.uniform(-max_dist_x, max_dist_x))
        track_to_object.location[1] = float(random.uniform(-max_dist_y, max_dist_y))
        track_to_object.location[2] = float(random.uniform(0, max_dist_z))

    # Object density conrol
    def generated_density_control(self):
        global generated_density
        max_density = generated_density
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

    def fog_control(self):
        fog_mat = bpy.data.materials['FogCube']
        fog_mat.use_nodes = True
        nodes = fog_mat.node_tree.nodes

        volume_node = nodes.get("Volume Scatter")


        global fog_likelyhood
        fog = False
        if random.uniform(0, 1) < fog_likelyhood:
            fog = True

        if fog == True:
            volume_node.inputs[1].default_value = 0.01 # inputs[1] refers to density
        else:
            volume_node.inputs[1].default_value = 0

    def animation_control(self):
        global animation_length_randomized
        length = random.uniform(0, animation_length_randomized)
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

file_path = ""
masked_object_gl = ""



class SceneControlOperator(Operator):
    """Scene Control"""
    bl_idname = "object.scene_control"
    bl_label = "Scene control"

    def execute(self, context):
        # Delete all the objects that the program might have generated previously
        self.delete_generated_controler()

        with open(file_path) as f:
            lines = f.readlines()
            
            for i in range(0, len(lines)):
                self.determine_command(lines[i])

        return {'FINISHED'}
    
    # File read
    def determine_command(self, current_line):
        values = current_line.split(" ")

        print()

        if values[0] == "#":
            print("Comment")
        elif values[0] == "following_object":
            print("Following object control " + values[1])
            self.choose_following_object(values[1])
        elif values[0] == "camera":
            print("Camera control " + str(values[1]) + " "  + str(values[2]) + " "  + str(values[3]))
            self.camera_control(values[1], values[2], values[3])
        elif values[0] == "track_to":
            print("Track-to control " + str(values[1]) + " "  + str(values[2]) + " "  + str(values[3]))
            self.track_to_control(values[1], values[2], values[3])
        elif values[0] == "generate_density":
            print("Generated objects density " + str(values[1]))
            self.generated_density_control(values[1])
        elif values[0] == "fog":
            print("Fog control " + str(values[1]))
            self.fog_control(values[1])
        elif values[0] == "animation_length_offset":
            print("Animation length and offset " + str(values[1]) + " "  + str(values[2]))
            self.animation_control(values[1], values[2])
        elif values[0] == "light_offset":
            print("Light offset " + str(values[1]))
            self.light_offset_control(values[1])
        else:
            print("Unassigned")

    def delete_generated_controler(self):
        print("Deleted previously generated objects")
        for object in bpy.data.collections['GeneratedObjects'].all_objects:
            bpy.data.objects.remove(object, do_unlink=True)


    # ----------------------------------------------------------------------------------------------
    # STUFF THAT CONTROLS THE SCENE
    # ----------------------------------------------------------------------------------------------

    # Choose following object
    def choose_following_object(self, object_name):
        global masked_object_gl

        mask_index = 0

        # Check if the user has chosen a particular object to follow
        # If an arguement was given, try getting the object with that name
        if object_name != "":
            layer_index = 0
            for layer in bpy.context.scene.view_layers:
                if layer.name == object_name:
                    mask_index = layer_index
                layer_index += 1
            # If an object with the given name was not found, choose a random object to follow
            if mask_index == 0:
                masked_object = random.randint(1, len(bpy.context.scene.view_layers) - 1)
            # If an object with the given name was found, set that one as the one to follow
            else:
                masked_object = mask_index
        else:
            masked_object = random.randint(1, len(bpy.context.scene.view_layers) - 1)

        masked_object_name = bpy.context.scene.view_layers[masked_object].name

        # Set the global variable so it can be used elsewhere
        masked_object_gl = masked_object_name

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

    # Camera control
    def camera_control(self, x, y, z):
        camera = bpy.context.scene.camera
        
        # Move the camera from the path by a certain ammount
        camera.location[0] = float(x)
        camera.location[1] = float(y)
        camera.location[2] = float(z)

    # Track to object control
    def track_to_control(self, x, y, z):
        global masked_object_gl
        collection = bpy.data.collections[masked_object_gl]

        for object in collection.all_objects:
            if object.name == masked_object_gl:
                track_to_object = object
        
        # Move the object from the path by a certain ammountcamera.location[0] = float(x)
        track_to_object.location[0] = float(x)
        track_to_object.location[1] = float(y)
        track_to_object.location[2] = float(z)

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

    def animation_control(self, length, offset):
        animation_length = int(length)
        animation_offset = int(offset)

        scene = bpy.context.scene

        scene.frame_start = animation_offset
        scene.frame_end = animation_offset + animation_length

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



# --------------------------------------------------------------------------------
# DELETING GENERATED OBJECTS
# --------------------------------------------------------------------------------

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



# ----------------------------------------------------------------------------------------------
# UI
# ----------------------------------------------------------------------------------------------

class SceneControlPanel:
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "Visual Tracker Simulator"
    bl_options = {"DEFAULT_CLOSED"}
    bl_context = "objectmode"

class SceneControlPanel1(SceneControlPanel, Panel):
    bl_idname = "object.scene_control_panel_1"
    bl_label = "Random Generation"

    @classmethod
    def poll(cls, context):
        return context.object is not None

    def draw(self, context):
        global file_path
        global camera_distance
        global track_to_distance
        global following_object
        global generated_density
        global fog_likelyhood
        global animation_length_randomized
        
        layout = self.layout
        col = layout.column(align=True)
        col.operator(RandomizeControlOperator.bl_idname, text="Randomize", icon="PLAY")
        layout.label(text="Randomization parameters limits:")

        randomizer_tool = context.scene.randomizer_tool
        layout.prop(randomizer_tool, "camera_distance")
        layout.prop(randomizer_tool, "track_to_distance")
        layout.prop(randomizer_tool, "following_object")
        layout.prop(randomizer_tool, "generated_density")
        layout.prop(randomizer_tool, "fog_likelyhood")
        layout.prop(randomizer_tool, "animation_length_randomized")
        
        camera_distance = randomizer_tool.camera_distance
        track_to_distance = randomizer_tool.track_to_distance
        following_object = randomizer_tool.following_object
        generated_density = randomizer_tool.generated_density
        fog_likelyhood = randomizer_tool.fog_likelyhood
        animation_length_randomized = randomizer_tool.animation_length_randomized


class SceneControlPanel2(SceneControlPanel, Panel):
    bl_idname = "object.scene_control_panel_2"
    bl_label = "Load From File"

    @classmethod
    def poll(cls, context):
        return context.object is not None

    def draw(self, context):
        global file_path
        layout = self.layout
        col = layout.column(align=True)
        file_tool = context.scene.file_tool
        col.prop(file_tool, "path")
        file_path = bpy.path.abspath("//") + file_tool.path
        col.operator(SceneControlOperator.bl_idname, text="Load", icon="PLAY")


class SceneControlPanel3(SceneControlPanel, Panel):
    bl_idname = "object.scene_control_panel_3"
    bl_label = "Render Scene and Mask"

    @classmethod
    def poll(cls, context):
        return context.object is not None

    def draw(self, context):
        layout = self.layout
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
    SceneControlPanel1,
    SceneControlPanel2,
    SceneControlPanel3,
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
    bpy.types.Scene.randomizer_tool = bpy.props.PointerProperty(type=RandomizationProperties)


def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)
    del bpy.types.Scene.file_tool
    del bpy.types.Scene.randomizer_tool

if __name__ == "__main__":
    register()