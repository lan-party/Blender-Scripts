import bpy
import bmesh
import math
import mathutils


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


# Create a circle
object_name = "circle"
mesh_name = f"{object_name}_data"
segments = 2*13 #7-16
    
mesh = bpy.data.meshes.new(mesh_name)
object = bpy.data.objects.new(object_name, mesh)
bpy.context.scene.collection.objects.link(object)

bm = bmesh.new()
bm.verts.ensure_lookup_table()
bm.verts.index_update()
bmesh.ops.create_circle(
    bm,
    segments=2*12,
    radius=segments/20,
    cap_ends=True
)


# Get vertex coordinates from around the circle
circle_coords = []
for vert in bm.verts:
    co = (vert.co[0], vert.co[1], vert.co[2])
    circle_coords.append(co)

bm.to_mesh(mesh)
mesh.update()
bm.free()


# Create ellipsoids facing the center
counter = 0
for coords in circle_coords:
    mesh = bpy.data.meshes.new(f"{str(counter)}_data")
    object = bpy.data.objects.new(str(counter), mesh)
    if counter % 2 == 0:
        object.scale = (1.5, 0.75, 3)
    else:
        object.scale = (3, 0.8, 3.5)
    object.location = coords
    object.rotation_euler[2] = math.radians(((360 / len(circle_coords)) * counter))
    bpy.context.scene.collection.objects.link(object)
    
    bm = bmesh.new()
    bmesh.ops.create_uvsphere(bm, u_segments=32, v_segments=16, radius=0.1)
    bm.to_mesh(mesh)
    mesh.update()
    bm.free()
    
    counter += 1

bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
    
    
# Join all objects
for object in bpy.data.objects:
    object.select_set(True)
bpy.context.view_layer.objects.active = bpy.data.objects['0']
bpy.ops.object.join()


# Bisect and fill the top of the mesh
mesh = bpy.data.objects['0'].data
bm = bmesh.new()
bm.from_mesh(mesh)

bm.verts.ensure_lookup_table()
bm.edges.ensure_lookup_table()
bm.faces.ensure_lookup_table()

result = bmesh.ops.bisect_plane(
    bm,
    geom=bm.verts[:] + bm.edges[:] + bm.faces[:],
    plane_co=mathutils.Vector((0, 0, 0)),
    plane_no=mathutils.Vector((0, 0, 1)),
    clear_outer=True,
    clear_inner=False,
    use_snap_center=False
)

cut_edges = [ele for ele in result['geom_cut'] if isinstance(ele, bmesh.types.BMEdge)]
boundary_edges = [e for e in cut_edges if len(e.link_faces) == 1]
bmesh.ops.edgeloop_fill(bm, edges=boundary_edges)

bm.to_mesh(mesh)
mesh.update()
bm.free()


# Create rounded cone
mesh = bpy.data.meshes.new('cone_data')
object = bpy.data.objects.new('cone', mesh)
bpy.context.scene.collection.objects.link(object)

bm = bmesh.new()

bm.verts.ensure_lookup_table()
bm.edges.ensure_lookup_table()
bm.faces.ensure_lookup_table()

depth=segments/20 + 0.25
bmesh.ops.create_cone(
    bm,
    cap_ends=True,
    segments=64,
    radius1=0.3,
    radius2=segments/20,
    depth=depth
)
object.location = (0,0,-(depth/1.9))

bottom_circle_edges=[]
for edge in bm.edges:
    if edge.verts[0].co[2] < 0 and edge.verts[0].co[2] == edge.verts[1].co[2]:
        bottom_circle_edges.append(edge)

bmesh.ops.bevel(
    bm,
    geom=bottom_circle_edges,
    offset=0.2,
    segments=10,
    profile=0.5,
    affect='EDGES'
)


bm.to_mesh(mesh)
mesh.update()
bm.free()


# Unwrap UV map
for object in bpy.data.objects:
    bpy.context.view_layer.objects.active = object
    bpy.ops.object.editmode_toggle()
    bpy.ops.mesh.select_all(action='SELECT')
    bpy.ops.uv.smart_project()
    bpy.ops.object.editmode_toggle()

# Apply colored materials to each object
top_material = bpy.data.materials.new("Top_Material")
top_material.diffuse_color = (0.0, 1.0, 1.0, 1.0)
bpy.data.objects['0'].data.materials.append(top_material)

bottom_material = bpy.data.materials.new("Bottom_Material")
bottom_material.diffuse_color = (1.0, 0.368, 0.914, 1.0)
bpy.data.objects['cone'].data.materials.append(bottom_material)
