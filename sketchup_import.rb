# MACHO-GPT Warehouse 3D Import Script
# HVDC PROJECT | Samsung C&T | ADNOC·DSV Partnership
# Generated: 2025-07-29 20:24:49

require 'csv'

def import_warehouse_layout
  model = Sketchup.active_model
  entities = model.entities
  
  # Warehouse dimensions
  warehouse_length = 35.m
  warehouse_width = 15.m
  warehouse_height = 10.m
  
  # Create warehouse floor
  floor_group = entities.add_group
  floor_face = floor_group.entities.add_face(
    [0, 0, 0],
    [warehouse_length, 0, 0],
    [warehouse_length, warehouse_width, 0],
    [0, warehouse_width, 0]
  )
  floor_face.material = "Concrete"
  
  # Import CSV data
  csv_file = "zoneAB_layout.csv"
  if File.exist?(csv_file)
    CSV.foreach(csv_file, headers: true) do |row|
      x = row['X'].to_f.m
      y = row['Y'].to_f.m
      l = row['L'].to_f.m
      w = row['W'].to_f.m
      h = row['H'].to_f.m
      
      # Create crate
      crate_group = entities.add_group
      crate_group.name = "Crate_" + row['Case_No']
      
      # Create crate geometry
      face = crate_group.entities.add_face(
        [x, y, 0],
        [x + l, y, 0],
        [x + l, y + w, 0],
        [x, y + w, 0]
      )
      
      # Extrude to height
      face.pushpull(h)
      
      # Apply material based on weight
      weight = row['Weight_kg'].to_f
      if weight > 2000
        crate_group.material = "Steel"
      elsif weight > 1000
        crate_group.material = "Wood"
      else
        crate_group.material = "Plastic"
      end
      
      # Add text label
      text_point = [x + l/2, y + w/2, h + 0.1.m]
      text_entity = crate_group.entities.add_text(row['Case_No'], text_point)
      text_entity.text = row['Case_No']
    end
    
    puts "✅ Imported warehouse items from CSV file"
  else
    puts "❌ CSV file not found: " + csv_file
  end
end

# Run import
import_warehouse_layout
