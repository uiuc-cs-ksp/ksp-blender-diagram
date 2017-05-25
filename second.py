import sys
sys.path.append("./io_kspblender")
sys.path.append("./io_object_mu")

import io_kspblender
io_kspblender.register()
import io_object_mu
io_object_mu.register()

import io_kspblender.import_craft as imp



import bpy

#Delete the default cube
bpy.data.objects["Cube"].select =True
bpy.ops.object.delete()
bpy.data.objects["Lamp"].select =True
bpy.ops.object.delete()

bpy.data.cameras["Camera"].type = "ORTHO"

#######################################
#import the ship
foo = imp.import_craft(None,bpy.context,sys.argv[1])

#Need to remove canopies
####
bpy.data.objects["canopy"].select =True
bpy.ops.object.delete()

_ = """
#                          Name,   Data
o = bpy.data.objects.new( "empty", None )
bpy.context.scene.objects.link( o )
foo_list = [i for i in bpy.data.objects if i.parent == None and not i == o]
for i in foo_list:
    i.parent = o
"""

_ = """
objects_list = [ obj for obj in bpy.data.objects if obj.type in ['MESH']]
foo_list = [i for i in objects_list if i.parent == None]
for ob in foo_list:
    tmp_location = ob.matrix_world * ob.location
    ob.parent = None
    ob.location = tmp_location

empty_objects = bpy.ops.object.select_by_type(type="EMPTY")
foo_list = [i for i in objects_list if ]
bpy.ops.object.delete()

active_object = objects_list[0]
bpy.ops.object.select_by_type(type="MESH")
bpy.context.scene.objects.active = active_object
bpy.ops.object.join()

import mathutils
min_vector = mathutils.Vector([1000,1000,1000])
max_vector = mathutils.Vector([-1000,-1000,-1000])

meshes_list = [ obj for obj in bpy.data.objects if obj.type in ['MESH']]
for one_obj in meshes_list:
    bb_vectors = [one_obj.matrix_world*mathutils.Vector(v) for v in one_obj.bound_box]
    for i in bb_vectors:
        min_vector = min(i,min_vector)
        #max_vector = max(i.location + half_dimension,max_vector) #doesn't work
        max_vector = -min(-i,-max_vector)

print("min max MESH extents: ", min_vector, max_vector)
"""

scene = bpy.data.scenes["Scene"]


lamp_data = bpy.data.lamps.new(name="Sun Lamp", type='SUN')
lamp_object = bpy.data.objects.new(name="Sun Lamp", object_data=lamp_data)
scene.objects.link(lamp_object)

lamp_object.location = (10.0,10.0,10.0)
lamp_object.rotation_euler = (3.14159/2.0,0.0,3.14159/4.0)


data_cam = bpy.data.cameras["Camera"]
data_cam.type = "ORTHO"
data_cam.ortho_scale = 5.0

obj_camera = bpy.data.objects["Camera"]
obj_camera.location = (0.0,-15.0,-10)
obj_camera.rotation_euler = (3.14159/2.0,0.0,0.0)
#obj_camera.ortho_scale = 7
#my_cam.location.x = 50
#my_cam.location.y = 50
#my_cam.location.z = 100

#bring everything into view:
#
#https://blender.stackexchange.com/a/51566
#
# Select objects that will be rendered
for obj in bpy.context.scene.objects:
    obj.select = False
for obj in bpy.context.visible_objects:
    if not (obj.hide or obj.hide_render):
        obj.select = True
bpy.ops.view3d.camera_to_view_selected()


bpy.ops.wm.save_as_mainfile(filepath="/data/another.blend")
if len(sys.argv) >= 3:
    bpy.context.scene.render.filepath = sys.argv[2]
    bpy.ops.render.render(write_still=True)
