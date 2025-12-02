import bpy
import bmesh
import mathutils
import random
import math
import numpy as np


# Clear everything from the scene
for object in bpy.data.objects:
    bpy.context.scene.collection.objects.unlink(object)
    bpy.data.objects.remove(object)
for mesh in bpy.data.meshes:
    bpy.data.meshes.remove(mesh)
for material in bpy.data.materials:
    bpy.data.materials.remove(material)
for image in bpy.data.images:
    bpy.data.images.remove(image)
    
    
# Helper Methods
def get_non_zero_uniform(a, b):
    while True:
        value = random.uniform(a, b)
        if value != 0.0:
            return value


# Trunk line
mesh = bpy.data.meshes.new("Tree_data")
object = bpy.data.objects.new("Tree", mesh)
bpy.context.scene.collection.objects.link(object)

bm = bmesh.new()

x = y = z = 0

trunk_height = random.randint(10, 30)

a1 = get_non_zero_uniform(-0.3, 0.3)
b1 = -(a1 - 0.1)
if a1 < 0:
    b1 = -(a1 + 0.1)
a2 = get_non_zero_uniform(-0.3, 0.3)
b2 = -(a2 - 0.1)
if a2 < 0:
    b2 = -(a2 + 0.1)

trunk_coords = []
for index in range(trunk_height):
    bm.verts.new(mathutils.Vector((x, y, z)))
    trunk_coords.append((x, y, z))
    x = a1*z**2 + b1*z
    y = a2*z**2 + b2*z
    z += 0.1
    
bm.verts.ensure_lookup_table()
bm.verts.index_update()

for index in range(len(bm.verts)-1):
    bm.edges.new((bm.verts[index], bm.verts[index+1]))

    
# Branch lines
max_branches = int(trunk_height / 5)
branch_count = random.randint(1, max_branches)

starting_verts = []
branch_idx = []
for index in range(branch_count):
    idx = random.randint(max_branches, trunk_height-1)
    branch_idx.append(idx)
branch_idx.sort()
for idx in branch_idx:
    starting_verts.append(bm.verts[idx])

all_branch_coords = []
for index in range(len(starting_verts)):
    vert = starting_verts[index]
    x = vert.co[0]
    y = vert.co[1]
    z = vert.co[2]
    
    branch_length = random.randint(5, int(trunk_height/3)+5)
    if branch_length > trunk_height - branch_idx[index]:
        branch_length = trunk_height - branch_idx[index]
    
    a1 = get_non_zero_uniform(-0.3, 0.3)
    b1 = -(a1 - 0.1)
    if a1 < 0:
        b1 = -(a1 + 0.1)
    a2 = get_non_zero_uniform(-0.3, 0.3)
    b2 = -(a2 - 0.1)
    if a2 < 0:
        b2 = -(a2 + 0.1)
        
    new_x = a1*z**2 + b1*z
    new_y = a2*z**2 + b2*z
    offset = (new_x - x, new_y - y, 0.1)
        
    branch_verts = []
    branch_coords = []
    for index in range(branch_length):
        x = a1*z**2 + b1*z
        y = a2*z**2 + b2*z
        z += 0.1
        branch_verts.append( bm.verts.new(mathutils.Vector((x-offset[0], y-offset[1], z-offset[2]))) )
        branch_coords.append((x-offset[0], y-offset[1], z-offset[2]))
    all_branch_coords.append(branch_coords)
        
    for index in range(len(branch_verts)-1):
        bm.edges.new((branch_verts[index], branch_verts[index+1]))

bm.to_mesh(mesh)
bm.free()


# Trunk circles
trunk_width = random.uniform(0.2, 0.05)
circle_width = trunk_width
all_branch_widths = []
for index in range(len(trunk_coords)-1):
    mesh = bpy.data.meshes.new("Circle_data")
    object = bpy.data.objects.new("Circle", mesh)
    bpy.context.scene.collection.objects.link(object)

    bm = bmesh.new()

    bmesh.ops.create_circle(
        bm,
        segments=16,
        radius=circle_width,
        cap_ends=False
    )
    object.location = trunk_coords[index]
    if index in branch_idx:
        all_branch_widths.append(circle_width)
    
    circle_width = trunk_width - (index / len(trunk_coords) * trunk_width)
    
    bm.to_mesh(mesh)
    bm.free()


# Join circles and end point into Trunk object
mesh = bpy.data.meshes.new("Trunk_data")
object = bpy.data.objects.new("Trunk", mesh)
bpy.context.scene.collection.objects.link(object)

bm = bmesh.new()
bmesh.ops.create_circle(
    bm,
    segments=16,
    radius=0.0001,
    cap_ends=False
)
bmesh.ops.translate(
    bm,
    verts=bm.verts,
    vec=trunk_coords[len(trunk_coords)-1]
)
bm.to_mesh(mesh)
bm.free()

for object in bpy.data.objects:
    if object.name != 'Tree':
        object.select_set(True)
bpy.context.view_layer.objects.active = bpy.data.objects['Trunk']
bpy.ops.object.join()
bpy.data.objects['Trunk'].select_set(False)


# Create faces between circles
bpy.ops.object.editmode_toggle()
bpy.ops.mesh.select_mode(type='EDGE')
bpy.ops.mesh.select_all(action='SELECT')
bpy.ops.mesh.bridge_edge_loops(
    type='SINGLE',
    use_merge=False,
    number_cuts=0,
    smoothness=0.25,
    interpolation='PATH'
)
bpy.ops.mesh.select_all(action='DESELECT')
bpy.ops.object.editmode_toggle()


# Branch circles
for index in range(len(all_branch_widths)):
    branch_width = all_branch_widths[index]
    circle_width = branch_width
    
    for index2 in range(len(all_branch_coords[index])-1):
        mesh = bpy.data.meshes.new("Circle_data")
        object = bpy.data.objects.new("Circle", mesh)
        bpy.context.scene.collection.objects.link(object)
        
        bm = bmesh.new()
        
        bmesh.ops.create_circle(
            bm,
            segments=16,
            radius=circle_width,
            cap_ends=False
        )
        object.location = all_branch_coords[index][index2]
        object.select_set(True)
        
        circle_width = branch_width - (index2 / len(all_branch_coords[index]) * branch_width)
        bm.to_mesh(mesh)
        bm.free()
        
    # Join circles into Branch object
    mesh = bpy.data.meshes.new("Branch_data")
    object = bpy.data.objects.new("Branch", mesh)
    bpy.context.scene.collection.objects.link(object)
    
    bm = bmesh.new()
    bmesh.ops.create_circle(
        bm,
        segments=16,
        radius=0.0001,
        cap_ends=False
    )
    bmesh.ops.translate(
        bm,
        verts=bm.verts,
        vec=all_branch_coords[index][len(all_branch_coords[index])-1]
    )
    bm.to_mesh(mesh)
    bm.free()

    object.select_set(True)
    bpy.context.view_layer.objects.active = object
    bpy.ops.object.join()

    # Create faces between circles
    bpy.ops.object.editmode_toggle()
    bpy.ops.mesh.select_mode(type='EDGE')
    bpy.ops.mesh.select_all(action='SELECT')
    bpy.ops.mesh.bridge_edge_loops(
        type='SINGLE',
        use_merge=False,
        number_cuts=0,
        smoothness=0.25,
        interpolation='PATH'
    )
    bpy.ops.mesh.select_all(action='DESELECT')
    bpy.ops.object.editmode_toggle()
    object.select_set(False)
    

# Remove tree wireframe
bpy.data.objects['Tree'].select_set(True)
bpy.ops.object.delete(use_global=False, confirm=False)


# Apply colored materials to each object
material = bpy.data.materials.new("Material")
material.diffuse_color = (0.607, 0.0, 1.851, 1.0)
for object in bpy.data.objects:
    object.data.materials.append(material)
