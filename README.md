# Visual Tracker Simulator (temporary readme)
Generates a desired number of scenes to run the tracker on. Then gets a text file containing parameters as an input and exports a rendered scene and its mask.

## How to instal
1. Download the zip file, unzip it and place the content in the addon folder in the location where you installed Blender.
2. Download the zip file, open Blender, click _Edit_ and _Preferences_, click _Install_, search for "Visual Tracker Simulator", click _Instal Add-on_ and enable it.

## How to use
First, generate some random scenes by running **generate_sequences.py**. Tell the program how many scenes to generate.\
To render the generated scene, open Blender and press **N** on your keyboard to get the sidebar. Click the Visual Tracker Simulator button.\
Choose your scene file either by opening file explorer or pasting the text file address into the field. Then press run to change your scene according to the file.

#### Version 0.0.1