# MACHO-GPT Warehouse 3D Blender Import Script
# HVDC PROJECT | Samsung C&T | ADNOC·DSV Partnership
# Generated: 2025-07-29 20:24:49

import bpy
import csv
import math

def clear_scene():
    """Clear existing objects"""
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete(use_global=False)

def create_warehouse_floor():
    """Create warehouse floor"""
    bpy.ops.mesh.primitive_plane_add(size=1)
    floor = bpy.context.active_object
    floor.name = "Warehouse_Floor"
    floor.scale = (35, 15, 1)
    
    # Apply material
    material = bpy.data.materials.new(name="Concrete")
    material.use_nodes = True
    material.node_tree.nodes["Principled BSDF"].inputs[0].default_value = (0.7, 0.7, 0.7, 1)
    floor.data.materials.append(material)

def create_crate(x, y, l, w, h, case_no, weight):
    """Create individual crate"""
    bpy.ops.mesh.primitive_cube_add(location=(x + l/2, y + w/2, h/2))
    crate = bpy.context.active_object
    crate.name = "Crate_" + case_no
    crate.scale = (l/2, w/2, h/2)
    
    # Apply material based on weight
    if weight > 2000:
        material_name = "Steel"
        color = (0.8, 0.8, 0.8, 1)
    elif weight > 1000:
        material_name = "Wood"
        color = (0.6, 0.4, 0.2, 1)
    else:
        material_name = "Plastic"
        color = (0.2, 0.6, 0.8, 1)
    
    material = bpy.data.materials.new(name=material_name)
    material.use_nodes = True
    material.node_tree.nodes["Principled BSDF"].inputs[0].default_value = color
    crate.data.materials.append(material)

def setup_lighting():
    """Setup warehouse lighting"""
    # Remove default light
    if "Light" in bpy.data.objects:
        bpy.data.objects.remove(bpy.data.objects["Light"])
    
    # Add area lights
    for i in range(4):
        bpy.ops.object.light_add(type='AREA', location=(8.75 + i*8.75, 7.5, 8))
        light = bpy.context.active_object
        light.data.energy = 1000
        light.data.size = 5

def setup_camera():
    """Setup camera for rendering"""
    bpy.ops.object.camera_add(location=(17.5, 7.5, 15))
    camera = bpy.context.active_object
    camera.rotation_euler = (math.radians(60), 0, math.radians(45))
    
    # Set as active camera
    bpy.context.scene.camera = camera

def import_warehouse_data():
    """Import warehouse data from CSV"""
    csv_file = "zoneAB_layout.csv"
    
    try:
        with open(csv_file, 'r') as f:
            reader = csv.DictReader(f)
            for row in reader:
                x = float(row['X'])
                y = float(row['Y'])
                l = float(row['L'])
                w = float(row['W'])
                h = float(row['H'])
                case_no = row['Case_No']
                weight = float(row['Weight_kg'])
                
                create_crate(x, y, l, w, h, case_no, weight)
        
            print("✅ Imported warehouse data from " + csv_file)
    except Exception as e:
        print("❌ Error importing data: " + str(e))

def main():
    """Main execution function"""
    print("�� Starting MACHO-GPT Warehouse 3D Import...")
    
    # Clear scene
    clear_scene()
    
    # Create warehouse floor
    create_warehouse_floor()
    
    # Import warehouse data
    import_warehouse_data()
    
    # Setup lighting
    setup_lighting()
    
    # Setup camera
    setup_camera()
    
    # Set render settings
    bpy.context.scene.render.engine = 'CYCLES'
    bpy.context.scene.render.resolution_x = 3840
    bpy.context.scene.render.resolution_y = 2160
    
    print("✅ Warehouse 3D scene created successfully!")

# Run main function
if __name__ == "__main__":
    main()
