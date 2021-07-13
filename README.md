# Visual Tracker Simulator
Generates a desired number of scenes to run the tracker on. Then gets a text file containing parameters as an input and exports a rendered scene and its mask.

## How to instal
Download the project, unzip it, create a folder called *visual_tracker_simulator*, place the _init_ file in it. Copy this folder inside the add-on folder in the location you installed Blender.\
Inside Blender, go _Edit > Preferences > Add-ons_. Find the add-on, its category is *render*. Enable the add-on.

## How to use
First, generate some random scenes by running **generate_sequences.py**. Tell the program how many scenes to generate. This file can be run in a location of choice.\
Secondly, open Blender and press **N** on your keyboard to get the sidebar. Click the Visual Tracker Simulator button.\
Choose your scene file either by opening file explorer or pasting the text file address into the field. Then press run to change your scene according to the file.\
To render a scene and a mask, use *Render Scene* and *Render Mask* buttons respectivelly. Since masks are rendered using *Eevee* engine, make sure to switch to Cycles render engine once mask rendering is finished, should you desire that.

## Creating your own scenes
The name of the path should contain the name of the layer/object you're following. Make sure only that object has such a name (layer and object names should be the same, and only them). The following path should be cyclic, to prevent the path jumping from one point to another.

## Version information

### Recommended Blender Version
2.92.0, not guaranteed to work on other versions.

### Known issues
* When clicking on delete generated with one of the generated objects selected, the add-on will disappear from the sidebar. In such case, just click anywhere (or anywhere on the sidebar) and it should reappear.

#### Version 0.1.0

###