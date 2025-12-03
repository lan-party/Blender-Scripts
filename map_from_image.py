import bpy
import bmesh
#import mathutils
import random
#import math
#import numpy as np
from PIL import Image


# Clear everything from the scene
for object in bpy.data.objects:
#    bpy.context.scene.collection.objects.unlink(object)
    bpy.data.objects.remove(object)
for mesh in bpy.data.meshes:
    bpy.data.meshes.remove(mesh)
for material in bpy.data.materials:
    bpy.data.materials.remove(material)
for image in bpy.data.images:
    bpy.data.images.remove(image)


unit_width = 2
islands = [
    'islands/7seg.glb',
    'islands/8seg.glb',
    'islands/9seg.glb',
    'islands/10seg.glb',
    'islands/11seg.glb',
    'islands/12seg.glb',
    'islands/13seg.glb',
    'islands/14seg.glb',
    'islands/15seg.glb',
    'islands/16seg.glb',
]
trees = [
    'trees/tree1.glb',
    'trees/tree2.glb',
    'trees/tree3.glb',
    'trees/tree4.glb',
    'trees/tree5.glb',
    'trees/tree6.glb',
    'trees/tree7.glb',
    'trees/tree8.glb',
    'trees/tree9.glb',
    'trees/tree10.glb'
]
tree_spawn_rate = 1/3
img = Image.open("map.png")
width, height = img.size

mesh = bpy.data.meshes.new("Map_data")
object = bpy.data.objects.new("Map", mesh)
bpy.context.scene.collection.objects.link(object)

for x in range(width):
    for y in range(height):
        r, g, b, a = img.getpixel((x, y))
        
        island_index = int(r/255 * (len(islands)+1))
        if island_index > 0:
            if random.random() > r*2/255:
                continue
            
            # Import and reposition island object
            bpy.ops.import_scene.gltf(filepath=islands[island_index-1])
            
            offset_max = (len(islands)+1) / island_index / 3
            z_offset = random.uniform(-offset_max, offset_max)
            x_offset = random.uniform(-0.25,0.25)
            y_offset = random.uniform(-0.25,0.25)
            
            top_object = bpy.data.objects['0']
            top_object.location.x = x * unit_width + x_offset
            top_object.location.y = y * unit_width + y_offset
            top_object.location.z += z_offset
            top_object.select_set(True)
            
            island_width = top_object.dimensions.y
            
            bottom_object = bpy.data.objects['cone']
            bottom_object.location.x = x * unit_width + x_offset
            bottom_object.location.y = y * unit_width - bottom_object.dimensions.y / 2 + y_offset
            bottom_object.location.z += z_offset
            bottom_object.select_set(True)
            
            # Merge objects
            bpy.data.objects['Map'].select_set(True)
            bpy.context.view_layer.objects.active = bpy.data.objects['Map']
            bpy.ops.object.join()
            
            
            # Import trees
            tree_count = random.randint(1, 3)
            if random.random() < tree_spawn_rate:
                for index in range(tree_count):
                    bpy.ops.import_scene.gltf(filepath=trees[random.randint(0, len(trees)-1)])
                    x_offset = random.uniform(-(island_width/3),island_width/3)
                    y_offset = random.uniform(-(island_width/3),island_width/3)
                    
                    for obj in bpy.data.objects:
                        if "Branch" in obj.name or "Trunk" in obj.name:
                            obj.location.x = x * unit_width + x_offset
                            obj.location.y = y * unit_width - island_width / 2 + y_offset
                            obj.location.z = z_offset
                            obj.select_set(True)
                            
                    # Merge objects
                    bpy.data.objects['Map'].select_set(True)
                    bpy.context.view_layer.objects.active = bpy.data.objects['Map']
                    bpy.ops.object.join()
