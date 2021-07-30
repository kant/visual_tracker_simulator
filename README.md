# Visual Tracker Simulator
Generates scenes on which to test visual trackers on.

## How to instal
Download the project, unzip it, create a folder called *visual_tracker_simulator*, place the _init_ file in it. Copy this folder inside the add-on folder in the location you installed Blender.
\
Inside Blender, go _Edit > Preferences > Add-ons_. Find the add-on, its category is *render*. Enable the add-on.

## How to use
In Object Mode, press **N** on your keyboard to get the sidebar. Click the Visual Tracker Simulator button.
\
There are two ways to generate a scene. The first is to generate the scene in Blender using *Randomize* button.
\
The second way is to load the scene generation parameters from a file, then clicking "Load" to generate it. One can also use **generate_sequences.py** to generate sequences. This python file can be run in a location of choice.
\
To render a scene and a mask, use *Render Scene* and *Render Mask* buttons respectivelly. Since masks are rendered using *Eevee* engine, make sure to switch to Cycles render engine once mask rendering is finished, should you desire that.

## Creating your own scenes
The scene must have the following collections:
* _MainObjects_ - objects you want to follow. Each of the objects you want to follow should be put in its own collection with the same name as the following object (for example an object named Boat should be in the collection named _Boat_, inside a collection named _MainObjects_)
* _GeneratingObjects_ - objects that you want to generate. Objects in this folder will be duplicated, then randomly put on paths in the collection _FollowingPaths_
The name of the path should contain the name of the layer/object you're following. Make sure that only that object has such a name (layer and object names should be the same, and only them). The following path should be cyclic, to prevent the path jumping from one point to another. Generating objects should only consist of one mesh
* _CameraParents_ - paths which the camera will follow. The path the camera follows has the same prefix as the object we are following, and the path will be chosen at random out of those paths
* _GeneratedObjects_ - a collection in which the objects generated with the add-on are stored
* _FollowingPaths_ - in here, put the paths you want the generated objects to follow. The path will be chosen at random
Other collections can be used to make the scene view more organised, but they are not needed.
<!-- end of the list -->
\
For each of the objects we want to follow, a layer must be created. Create a layer for each of the collections in _MainObject_, give it the same name as the collection (for example, a collection boat) and using holdout mask out all the collection except the one object itself.
\
The scene should have an HDRI skybox an animation with three keyframes under World Properties > Surface > Strength. Make sure that the animation is named *Shader NodetreeAction*. Make sure the animation is cyclic.
\
When creating the animations for objects following the paths, make sure all the animations are cyclic, so you can generate the animation to be as long as you want.
\
Each scene should have a fog object. At least one path should be present in _FollowingPaths_ and at least one object in _GeneratingObjects_.

## Version information

### Recommended Blender Version
2.92.0, not guaranteed to work on other versions.

### Known issues
* When clicking on delete generated with one of the generated objects selected, the add-on will disappear from the sidebar. In such case, just click anywhere (or anywhere on the sidebar) and it should reappear.

#### Version 0.2.2

###