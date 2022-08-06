

import bpy
import os
import platform
import requests
import addon_utils
from bpy.props import (FloatProperty,
                        StringProperty, 
                        EnumProperty, 
                        BoolProperty,
)

try:
    import pwd
except ModuleNotFoundError:
    pass

class addonPrefs(bpy.types.PropertyGroup):
    bl_idname = "QHDRI.prefs"
    
    resolution_list = (("1k", "1K", ""), ("2k", "2K", ""), ("4k", "4K", ""), ("8k", "8K", ""),)
    filetype_list = (("hdr", "HDR", ""), ("exr", "EXR", ""),)
    
    textPath: bpy.props.StringProperty(
        name="Link",
        default="",
        description="Text box to insert directory for HDRI links from Polyhaven",
    )
    
    selectRes: bpy.props.EnumProperty(
        name='',
        description = 'List of available resolutions',
        items = resolution_list,
    )
    
    selectFileType: bpy.props.EnumProperty(
        name="",
        description = "List of available file types",
        items = filetype_list,
    )

class qhdri_import(bpy.types.Operator):
    bl_idname = "qhdri.import"
    bl_label = "Import"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):

        scene = context.scene
        addonPrefs = scene.qhdri
        file_name = addonPrefs.textPath
                
        for i in range(4): #checking if it's a valid link, may change later for more accurate one
            try:
                file_name = file_name.split("/", 1)[1]
            except IndexError:
                return {'FINISHED'}
            
        
        #creating nodes
        
        world = bpy.data.worlds['World']
        world.use_nodes = True
        node_tree = world.node_tree.nodes
        
        #deletes background node 
        bg_node = node_tree.get('Background')
        print(bg_node)
        if bg_node is not None:
            world.node_tree.nodes.remove(bg_node)
        
        #NODES - ordered from closest the world output
        
        rgb = world.node_tree.nodes.new('ShaderNodeRGBCurve')
        rgb.location = (50, 300)
        
        envTex = world.node_tree.nodes.new('ShaderNodeTexEnvironment')
        envTex.location = (-250, 300)
   
        mapping = world.node_tree.nodes.new('ShaderNodeMapping')
        mapping.location = (-450, 300)
        
        texCord = world.node_tree.nodes.new('ShaderNodeTexCoord')
        texCord.location = (-650, 300)
        
        #connections 
        world.node_tree.links.new(rgb.outputs[0], node_tree.get('World Output').inputs[0])
        world.node_tree.links.new(envTex.outputs[0], rgb.inputs[1])
        world.node_tree.links.new(mapping.outputs[0], envTex.inputs[0])
        world.node_tree.links.new(texCord.outputs['Object'], mapping.inputs[0])
        
        #print(file_name)
        hdriFile = 'https://dl.polyhaven.org/file/ph-assets/HDRIs/'+ addonPrefs.selectFileType+'/'+addonPrefs.selectRes+'/'+file_name+'_'+addonPrefs.selectRes.lower()+'.'+addonPrefs.selectFileType.lower()
        r = requests.get(hdriFile)
        
        if platform.system() == 'Windows': 
            username = str(os.environ['USERPROFILE']+'\\Downloads\\')
            f = open(username+file_name+'_'+addonPrefs.selectRes.lower()+'.'+addonPrefs.selectFileType.lower(), 'wb')
            f.write(r.content)
            f.close()
            envTex.image = bpy.data.images.load(username+file_name+'_'+addonPrefs.selectRes.lower()+'.'+addonPrefs.selectFileType.lower())
        elif platform.system() == 'Darwin':
            username = pwd.getpwuid(os.getuid())[0]
            f = open('/Users/'+username+'/Downloads/'+file_name+'_'+addonPrefs.selectRes.lower()+'.'+addonPrefs.selectFileType.lower(), 'wb')
            f.write(r.content)
            f.close()
            
            envTex.image = bpy.data.images.load('/Users/'+username+'/Downloads/'+file_name+'_'+addonPrefs.selectRes.lower()+'.'+addonPrefs.selectFileType.lower())
        elif platform.system() == 'Linux':
            username = pwd.getpwuid(os.getuid())[0]
            f = open('/home/'+username+'/Downloads/'+file_name+'_'+addonPrefs.selectRes.lower()+'.'+addonPrefs.selectFileType.lower(), 'wb')
            f.write(r.content)
            f.close()
            
            envTex.image = bpy.data.images.load('/home/'+username+'/Downloads/'+file_name+'_'+addonPrefs.selectRes.lower()+'.'+addonPrefs.selectFileType.lower())
        

        #print(hdriFile)
        addonPrefs.qhdriBool = True
        return {'FINISHED'}

class quickHDRI(bpy.types.Panel): #replace the class name 

    #Replace names and ids with desired ones
    bl_label = "Quick HDRI"
    bl_idname = "qhdri"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "Quick HDRI"
    
    def draw(self, context):
        layout = self.layout
        scene = context.scene
        addonPrefs = scene.qhdri
        col = layout.column(align=True)
        
        layout.prop(addonPrefs, "textPath") 
        layout.separator()
        r = col.row()
        r = layout.row(align=True)
        r.prop(addonPrefs, "selectRes")
        r.prop(addonPrefs, "selectFileType")
        r.operator(qhdri_import.bl_idname, text="Import", icon="IMPORT")
        
classes = ( #add the classes here
    addonPrefs,
    qhdri_import,
    quickHDRI, 
)

def register():
    for cls in classes:
        bpy.utils.register_class(cls)
        bpy.types.Scene.qhdri = bpy.props.PointerProperty(type=addonPrefs)
        
def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)
        del bpy.types.Scene.my_tools
        
if __name__ == "__main__":
    register() 

#https://dl.polyhaven.org/file/ph-assets/HDRIs/hdr/1k/dark_autumn_forest_1k.hdr
#                                               ^   ^     ^
# options:                               exr/hdr 1k~24k  name 
