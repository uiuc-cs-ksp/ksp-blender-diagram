import sys

import bpy

#Delete the default cube
bpy.data.objects["Cube"].select =True
bpy.ops.object.delete()
bpy.data.objects["Lamp"].select =True
bpy.ops.object.delete()

bpy.data.cameras["Camera"].type = "ORTHO"





scene = bpy.data.scenes["Scene"]
lamp_data = bpy.data.lamps.new(name="Sun Lamp", type='SUN')
lamp_object = bpy.data.objects.new(name="Sun Lamp", object_data=lamp_data)
scene.objects.link(lamp_object)

lamp_object.location = (10.0,10.0,10.0)
lamp_object.rotation_euler = (3.14159/2.0,0.0,3.14159/4.0)


data_cam = bpy.data.cameras["Camera"]
data_cam.type = "ORTHO"
data_cam.ortho_scale = 25.0

obj_camera = bpy.data.objects["Camera"]
obj_camera.location = (0.0,-15.0,10)
obj_camera.rotation_euler = (3.14159/2.0,0.0,0.0)
#obj_camera.ortho_scale = 7
#my_cam.location.x = 50
#my_cam.location.y = 50
#my_cam.location.z = 100

#                          Name,   Data
o = bpy.data.objects.new( "empty", None )
bpy.context.scene.objects.link( o )


for i in range(20):
    a = bpy.ops.mesh.primitive_cone_add(
    vertices=40,
    radius1=1,
    depth=1,
    end_fill_type="TRIFAN")


bpy.data.objects["Cone"].location.z = 10
bpy.data.objects["Cone.001"].location.z = 13

for i in range(1,9):
    bpy.data.objects["Cone.00{}".format(i)].location.z = i

active_object = bpy.data.objects["Cone"]
active_object.select = True

bpy.ops.object.select_by_type(type="MESH")

bpy.context.scene.objects.active = active_object
bpy.ops.object.join()


bpy.ops.wm.save_as_mainfile(filepath="/data/shootme.blend")
bpy.context.scene.render.filepath = "/data/shootme.png"
bpy.ops.render.render(write_still=True)
