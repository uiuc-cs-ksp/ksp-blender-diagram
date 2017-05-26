from argparse import ArgumentParser
a_parser = ArgumentParser()
a_parser.add_argument("-s","--stage",type=int,default=1000,help="Remove parts from any stage earlier than this.")
a_parser.add_argument("-r","--render",type=str,help="Render to the specified png file.")
a_parser.add_argument("ship_file",help="The ship file to read in.")
a_parser.add_argument("output_scene",nargs="?",help="If optionally provided, the scene to save to.")

args = a_parser.parse_args()


#
#This path setup stuff is really only needed for the non-installed script, when testing.
#This should ideally be done with the PYTHONPATH
#
import sys
sys.path.append("./io_kspblender")
sys.path.append("./io_object_mu")



#Import blender
import bpy

def deselect_all():
    bpy.context.scene.objects.active = None
    bpy.ops.object.select_all(action="DESELECT")
    for obj in bpy.data.objects:
        obj.select = False

def iterate_normal_objects(object_set=None):
    if object_set == None:
        object_set = bpy.data.objects
    for one_obj in object_set:
        if one_obj.type in ["CAMERA","LAMP"]:
            continue
        yield one_obj


#
#Import and setup the blender plugins we rely on.
#
import io_kspblender
io_kspblender.register()
import io_object_mu
io_object_mu.register()

import io_kspblender.import_craft as imp

from cfgnode import ConfigNode

def get_cfg_values(one_node,val_type):
    return [i[1] for i in one_node.values if i[0] == val_type]

part_node_dict = dict()
child_parent_map = dict()
parent_children_map = dict()
all_partnames = list()
parentage_crosses_stage = list()

loaded_config_nodes = ConfigNode.load(open(args.ship_file,encoding="utf-8").read())
print("Load successful")
theparts = [p[1] for p in loaded_config_nodes.nodes if p[0] == "PART"]

for partNode in theparts:
    partpart = [i[1] for i in partNode.values if i[0] == "part"][0]
    partNode_childlinks = [i[1] for i in partNode.values if i[0] == "link"]
    for one_child in partNode_childlinks:
        child_parent_map[one_child] = partpart
    parent_children_map[partpart] = partNode_childlinks
    all_partnames.append(partpart)
    part_node_dict[partpart] = partNode

for child,parent in child_parent_map.items():
    child_stage = get_cfg_values(part_node_dict[child],"istg")[0]
    parent_stage = get_cfg_values(part_node_dict[parent],"istg")[0]
    if not child_stage == parent_stage:
        parentage_crosses_stage.append(child)
#
#Not sure yet, we might need a tree traversal if Blender changes the position of objects while parenting.
#We'll see.
#



#
#Setup Scene
#TODO: find a better way to create an empty default scene. Does blender really always create a cube and lamp?
#
#Delete the default cube
bpy.data.objects["Cube"].select =True
bpy.ops.object.delete()
bpy.data.objects["Lamp"].select =True
bpy.ops.object.delete()


#######################################
#import the ship
foo = imp.import_craft(None,bpy.context,sys.argv[1])

#
#Fix the parent child relationships from the importer
#Maybe eventually this should create empties for the stages.
#
#https://blender.stackexchange.com/a/9204
#
for parent_name,its_childrens_names in parent_children_map.items():
    if not parent_name in bpy.data.objects.keys():
        print("Object {} ({} children) was not available for reparenting.".format(parent_name,len(its_childrens_names)),
            file=sys.stderr)
        continue

    deselect_all()
    p_part = bpy.data.objects[parent_name]
    p_part.select = True
    for c_name in its_childrens_names:
        if not c_name in bpy.data.objects.keys():
            print("Object {} child of {} was not available for reparenting".format(c_name,parent_name),
                file=sys.stderr)
            continue
        c_part = bpy.data.objects[c_name]
        c_part.select = True

    bpy.context.scene.objects.active = p_part    #the active object will be the parent of all selected object
    bpy.ops.object.parent_set()
    bpy.context.scene.objects.active = None

#
#TODO: Make the mesh parts unselectable so that manipulation is easier for animation.
#This code doesn't work.
_ = """
partname_set = set(all_partnames)
for obj in bpy.data.objects:
    deselect_all()
    if obj.type in ["CAMERA","LAMP"]:
        continue
    if not obj.name in partname_set:
        #obj.select = True
        bpy.context.scene.objects.active = obj
        import ipdb;ipdb.set_trace()
        #bpy.ops.outliner.object_operation(type="TOGSEL")
"""
#Need to remove canopies
####
#Need to handle multiple parachutes



#
#REMOVE PARACHUTE CANOPIES
#
deselect_all()

#clean out some useless obejects
for obj in bpy.data.objects:
	if obj.type == "CAMERA":
		continue
	if obj.name.startswith("Collider") or obj.name.startswith("collider") or obj.name.startswith("node_collider") or obj.name.startswith("canopy"):
		obj.select = True
bpy.ops.object.delete()
deselect_all()

scene = bpy.data.scenes["Scene"]

#
#Setup Lighting if not using ambient.
#

#lamp_data = bpy.data.lamps.new(name="Sun Lamp", type='SUN')
#lamp_object = bpy.data.objects.new(name="Sun Lamp", object_data=lamp_data)
#scene.objects.link(lamp_object)

#lamp_object.location = (10.0,10.0,10.0)
#lamp_object.rotation_euler = (3.14159/2.0,0.0,3.14159/4.0)

#
#Setup Camera
#

data_cam = bpy.data.cameras["Camera"]
data_cam.type = "ORTHO"
data_cam.ortho_scale = 5.0 #will be overwritten later

obj_camera = bpy.data.objects["Camera"]
obj_camera.location = (0.0,-15.0,-10)
obj_camera.rotation_euler = (3.14159/2.0,0.0,0.0)

#bring everything into view:
#
#https://blender.stackexchange.com/a/51566
#
# Select objects that will be rendered, then zoom the camera to fit them.
deselect_all()
for obj in bpy.context.visible_objects:
    if not (obj.hide or obj.hide_render):
        obj.select = True
bpy.ops.view3d.camera_to_view_selected()
deselect_all()

#
#Setup Rendering
#
bpy.data.scenes["Scene"].render.engine="BLENDER_RENDER"
bpy.data.scenes["Scene"].render.use_freestyle = True
#bpy.data.scenes["Scene"].render.use_shadows = False
bpy.data.worlds["World"].light_settings.use_environment_light = True


#
#Output
#
if args.output_scene:
    bpy.ops.wm.save_as_mainfile(filepath=args.output_scene)
if args.render:
    bpy.context.scene.render.filepath = args.render
    bpy.ops.render.render(write_still=True)
