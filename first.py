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

#import the ship
foo = imp.import_craft(None,bpy.context,sys.argv[1])


#Need to remove canopies
####

scene = bpy.data.scenes["Scene"]


lamp_data = bpy.data.lamps.new(name="Sun Lamp", type='SUN')
lamp_object = bpy.data.objects.new(name="Sun Lamp", object_data=lamp_data)
scene.objects.link(lamp_object)

lamp_object.location = (10.0,10.0,10.0)
lamp_object.rotation_euler = (3.14159/2.0,0.0,3.14159/4.0)


data_cam = bpy.data.cameras["Camera"]
data_cam.type = "ORTHO"
data_cam.ortho_scale = 20.0

obj_camera = bpy.data.objects["Camera"]
obj_camera.location = (0.0,-15.0,10)
obj_camera.rotation_euler = (3.14159/2.0,0.0,0.0)
#obj_camera.ortho_scale = 7
#my_cam.location.x = 50
#my_cam.location.y = 50
#my_cam.location.z = 100


bpy.ops.wm.save_as_mainfile(filepath="/data/gya.blend")

bpy.context.scene.render.filepath = sys.argv[2]
bpy.ops.render.render(write_still=True)
