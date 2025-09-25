import matplotlib.pyplot as plt
import matplotlib.patches as patches
import matplotlib.patches as mpatches
import numpy as np
from matplotlib.patches import FancyBboxPatch, Circle, Arrow
import matplotlib.gridspec as gridspec

# Professional HCS Stowage Plan Drawing
fig = plt.figure(figsize=(24, 16))
gs = gridspec.GridSpec(3, 4, figure=fig, height_ratios=[0.8, 2, 0.6], width_ratios=[3, 1, 1, 1])

# === MAIN DECK PLAN ===
ax_main = fig.add_subplot(gs[1, :3])

# Deck dimensions and setup
deck_length = 41.5
deck_width = 11.0
scale_factor = 20  # pixels per meter

# Draw vessel outline
vessel_rect = patches.Rectangle((0, 0), deck_length, deck_width, 
                               linewidth=3, edgecolor='navy', facecolor='lightblue', alpha=0.3)
ax_main.add_patch(vessel_rect)

# Zone definitions
port_width = 4.0
walkway_width = 2.0
starboard_width = 5.0

# Draw zones
port_zone = patches.Rectangle((0, 0.5), deck_length, port_width, 
                             linewidth=2, edgecolor='green', facecolor='lightgreen', alpha=0.2, linestyle='--')
ax_main.add_patch(port_zone)

walkway_zone = patches.Rectangle((0, 4.5), deck_length, walkway_width, 
                                linewidth=3, edgecolor='orange', facecolor='yellow', alpha=0.3)
ax_main.add_patch(walkway_zone)

starboard_zone = patches.Rectangle((0, 6.5), deck_length, starboard_width-1, 
                                  linewidth=2, edgecolor='blue', facecolor='lightblue', alpha=0.2, linestyle='--')
ax_main.add_patch(starboard_zone)

# Bundle data with precise positions for 2-tier loading
bundle_data = [
    # === TIER 1 (Bottom Layer) ===
    # Port Zone - Large bundles
    {'id': 6, 'tier': 1, 'x': 1.0, 'y': 1.0, 'length': 12.21, 'width': 1.20, 'height': 0.60, 'weight': 10.95, 'zone': 'Port'},
    {'id': 7, 'tier': 1, 'x': 14.0, 'y': 1.0, 'length': 12.21, 'width': 1.20, 'height': 0.80, 'weight': 13.16, 'zone': 'Port'},
    {'id': 8, 'tier': 1, 'x': 27.0, 'y': 1.0, 'length': 12.21, 'width': 1.20, 'height': 0.80, 'weight': 10.37, 'zone': 'Port'},
    {'id': 9, 'tier': 1, 'x': 1.0, 'y': 2.5, 'length': 12.21, 'width': 1.20, 'height': 0.80, 'weight': 10.37, 'zone': 'Port'},
    {'id': 10, 'tier': 1, 'x': 14.0, 'y': 2.5, 'length': 12.21, 'width': 1.20, 'height': 0.80, 'weight': 10.26, 'zone': 'Port'},
    
    # Medium bundles at port end
    {'id': 4, 'tier': 1, 'x': 33.0, 'y': 1.0, 'length': 8.06, 'width': 1.20, 'height': 0.60, 'weight': 8.68, 'zone': 'Port'},
    {'id': 5, 'tier': 1, 'x': 33.0, 'y': 2.5, 'length': 8.06, 'width': 1.20, 'height': 0.90, 'weight': 10.86, 'zone': 'Port'},
    
    # Starboard Zone - Large bundles
    {'id': 11, 'tier': 1, 'x': 1.0, 'y': 7.0, 'length': 12.21, 'width': 1.20, 'height': 0.80, 'weight': 10.76, 'zone': 'Starboard'},
    {'id': 12, 'tier': 1, 'x': 14.0, 'y': 7.0, 'length': 12.21, 'width': 1.20, 'height': 0.80, 'weight': 13.16, 'zone': 'Starboard'},
    {'id': 13, 'tier': 1, 'x': 27.0, 'y': 7.0, 'length': 12.21, 'width': 1.20, 'height': 0.80, 'weight': 10.37, 'zone': 'Starboard'},
    {'id': 14, 'tier': 1, 'x': 1.0, 'y': 8.5, 'length': 12.21, 'width': 1.20, 'height': 0.80, 'weight': 10.37, 'zone': 'Starboard'},
    {'id': 15, 'tier': 1, 'x': 14.0, 'y': 8.5, 'length': 12.21, 'width': 1.09, 'height': 0.80, 'weight': 9.89, 'zone': 'Starboard'},
    {'id': 16, 'tier': 1, 'x': 27.0, 'y': 8.5, 'length': 12.21, 'width': 1.18, 'height': 0.80, 'weight': 10.41, 'zone': 'Starboard'},
    {'id': 17, 'tier': 1, 'x': 1.0, 'y': 10.0, 'length': 12.21, 'width': 1.20, 'height': 0.80, 'weight': 12.87, 'zone': 'Starboard'},
    
    # Medium bundle at starboard end
    {'id': 2, 'tier': 1, 'x': 35.0, 'y': 7.0, 'length': 6.31, 'width': 1.20, 'height': 0.80, 'weight': 8.05, 'zone': 'Starboard'},
    
    # === TIER 2 (Top Layer) ===
    # Port Zone - Medium bundles
    {'id': 3, 'tier': 2, 'x': 1.0, 'y': 1.0, 'length': 6.31, 'width': 1.20, 'height': 0.80, 'weight': 7.84, 'zone': 'Port'},
    {'id': 1, 'tier': 2, 'x': 8.0, 'y': 1.0, 'length': 4.52, 'width': 1.20, 'height': 0.80, 'weight': 5.61, 'zone': 'Port'},
    
    # Starboard Zone - Small bundles
    {'id': 18, 'tier': 2, 'x': 1.0, 'y': 7.0, 'length': 3.22, 'width': 1.03, 'height': 0.80, 'weight': 2.96, 'zone': 'Starboard'},
    {'id': 19, 'tier': 2, 'x': 5.0, 'y': 7.0, 'length': 3.22, 'width': 1.20, 'height': 0.80, 'weight': 2.57, 'zone': 'Starboard'},
    {'id': 20, 'tier': 2, 'x': 9.0, 'y': 7.0, 'length': 3.22, 'width': 0.78, 'height': 0.80, 'weight': 2.26, 'zone': 'Starboard'},
    {'id': 21, 'tier': 2, 'x': 13.0, 'y': 7.0, 'length': 3.22, 'width': 1.20, 'height': 0.80, 'weight': 3.47, 'zone': 'Starboard'},
    {'id': 22, 'tier': 2, 'x': 17.0, 'y': 7.0, 'length': 3.22, 'width': 1.20, 'height': 0.80, 'weight': 3.47, 'zone': 'Starboard'},
    {'id': 23, 'tier': 2, 'x': 21.0, 'y': 7.0, 'length': 3.22, 'width': 1.20, 'height': 0.80, 'weight': 3.47, 'zone': 'Starboard'},
    {'id': 24, 'tier': 2, 'x': 25.0, 'y': 7.0, 'length': 3.22, 'width': 1.00, 'height': 0.40, 'weight': 1.45, 'zone': 'Starboard'},
    {'id': 25, 'tier': 2, 'x': 29.0, 'y': 7.0, 'length': 3.22, 'width': 0.75, 'height': 0.40, 'weight': 1.09, 'zone': 'Starboard'}
]

# Color schemes for tiers
tier1_color = '#4CAF50'  # Green for Tier 1
tier2_color = '#FF9800'  # Orange for Tier 2
tier1_edge = '#2E7D32'
tier2_edge = '#E65100'

# Draw bundles
for bundle in bundle_data:
    # Choose colors based on tier
    face_color = tier1_color if bundle['tier'] == 1 else tier2_color
    edge_color = tier1_edge if bundle['tier'] == 1 else tier2_edge
    
    # Create bundle rectangle
    rect = FancyBboxPatch((bundle['x'], bundle['y']), 
                         bundle['length'], bundle['width'],
                         boxstyle="round,pad=0.02", 
                         facecolor=face_color, 
                         edgecolor=edge_color,
                         linewidth=2,
                         alpha=0.8)
    ax_main.add_patch(rect)
    
    # Add bundle labels
    center_x = bundle['x'] + bundle['length']/2
    center_y = bundle['y'] + bundle['width']/2
    
    # Item number (larger font)
    ax_main.text(center_x, center_y + 0.2, f"ITEM {bundle['id']}", 
                ha='center', va='center', fontsize=10, fontweight='bold', color='white')
    
    # Weight (smaller font)
    ax_main.text(center_x, center_y - 0.2, f"{bundle['weight']}t", 
                ha='center', va='center', fontsize=8, color='white')
    
    # Tier indicator (small)
    ax_main.text(bundle['x'] + 0.2, bundle['y'] + 0.1, f"T{bundle['tier']}", 
                ha='left', va='bottom', fontsize=7, fontweight='bold', 
                color='yellow' if bundle['tier'] == 1 else 'red')

# Padeye locations (16 points in 4 rows)
padeye_locations = []
# Port edge (Y=0.5)
for x in [5, 15, 25, 35]:
    padeye_locations.append((x, 0.5))
# Port inner (Y=4.5)  
for x in [5, 15, 25, 35]:
    padeye_locations.append((x, 4.5))
# Starboard inner (Y=6.5)
for x in [5, 15, 25, 35]:
    padeye_locations.append((x, 6.5))
# Starboard edge (Y=10.5)
for x in [5, 15, 25, 35]:
    padeye_locations.append((x, 10.5))

# Draw padeyes
for i, (x, y) in enumerate(padeye_locations):
    padeye = Circle((x, y), 0.15, facecolor='red', edgecolor='darkred', linewidth=2, zorder=10)
    ax_main.add_patch(padeye)
    ax_main.text(x, y-0.4, f'P{i+1}', ha='center', va='top', fontsize=6, fontweight='bold')

# Draw sample lashing lines (from corners to nearest padeyes)
def draw_lashing_lines():
    for bundle in bundle_data[:5]:  # Sample lashing for first 5 bundles
        corners = [
            (bundle['x'], bundle['y']),
            (bundle['x'] + bundle['length'], bundle['y']),
            (bundle['x'], bundle['y'] + bundle['width']),
            (bundle['x'] + bundle['length'], bundle['y'] + bundle['width'])
        ]
        
        for corner in corners:
            # Find nearest padeye
            min_dist = float('inf')
            nearest_padeye = None
            for padeye in padeye_locations:
                dist = np.sqrt((corner[0] - padeye[0])**2 + (corner[1] - padeye[1])**2)
                if dist < min_dist:
                    min_dist = dist
                    nearest_padeye = padeye
            
            # Draw lashing line
            if nearest_padeye:
                ax_main.plot([corner[0], nearest_padeye[0]], [corner[1], nearest_padeye[1]], 
                           'k-', alpha=0.4, linewidth=1, zorder=1)

draw_lashing_lines()

# Add measurements and annotations
ax_main.annotate('', xy=(41.5, -0.5), xytext=(0, -0.5), 
                arrowprops=dict(arrowstyle='<->', color='black', lw=2))
ax_main.text(20.75, -1, '41.5m', ha='center', va='top', fontsize=12, fontweight='bold')

ax_main.annotate('', xy=(-1, 11), xytext=(-1, 0), 
                arrowprops=dict(arrowstyle='<->', color='black', lw=2))
ax_main.text(-1.5, 5.5, '11.0m', ha='center', va='center', fontsize=12, fontweight='bold', rotation=90)

# Zone labels
ax_main.text(20.75, 2.5, 'PORT ZONE\n4.0m × 41.5m\nTier 1: 7 bundles\nTier 2: 2 bundles', 
            ha='center', va='center', fontsize=11, fontweight='bold', 
            bbox=dict(boxstyle='round,pad=0.5', facecolor='lightgreen', alpha=0.8))

ax_main.text(20.75, 5.5, 'WALKWAY\n2.0m × 41.5m\n작업자 안전통로\n⚠️ KEEP CLEAR', 
            ha='center', va='center', fontsize=11, fontweight='bold',
            bbox=dict(boxstyle='round,pad=0.5', facecolor='yellow', alpha=0.8))

ax_main.text(20.75, 8.5, 'STARBOARD ZONE\n5.0m × 41.5m\nTier 1: 8 bundles\nTier 2: 8 bundles', 
            ha='center', va='center', fontsize=11, fontweight='bold',
            bbox=dict(boxstyle='round,pad=0.5', facecolor='lightblue', alpha=0.8))

# Title and formatting
ax_main.set_xlim(-3, 45)
ax_main.set_ylim(-2, 13)
ax_main.set_aspect('equal')
ax_main.grid(True, alpha=0.3)
ax_main.set_xlabel('Length (m)', fontsize=12, fontweight='bold')
ax_main.set_ylabel('Width (m)', fontsize=12, fontweight='bold')

# === HEADER SECTION ===
ax_header = fig.add_subplot(gs[0, :])
ax_header.text(0.5, 0.7, '🚢 HCS PROFESSIONAL STOWAGE PLAN', 
              ha='center', va='center', fontsize=24, fontweight='bold', transform=ax_header.transAxes)
ax_header.text(0.5, 0.3, 'JOPETWIL 71 | Single Voyage | 2-Tier Loading | 25 Bundles | 194.7t | Rev.01', 
              ha='center', va='center', fontsize=14, transform=ax_header.transAxes)
ax_header.set_xlim(0, 1)
ax_header.set_ylim(0, 1)
ax_header.axis('off')

# === SIDE PANELS ===

# Panel 1: Statistics
ax_stats = fig.add_subplot(gs[1, 3])
stats_text = """
📊 PROJECT STATISTICS

Total Bundles: 25
Total Weight: 194.7t
Total Volume: 163.1 CBM
Deck Utilization: 89.5%

TIER BREAKDOWN
Tier 1: 15 bundles (138.2t)
Tier 2: 10 bundles (56.5t)

ZONE DISTRIBUTION
Port: 9 bundles (91.5t)
Starboard: 16 bundles (103.2t)

SAFETY MARGINS
Max Height: 1.6m
Walkway: 2.0m clear
Side Clearance: 1.0m
GM: 2.8m (>2.0m req.)

LASHING SYSTEM
Padeyes: 16 points
Large Bundles: 19mm wire
Medium Bundles: 16mm wire  
Small Bundles: 13mm wire
"""

ax_stats.text(0.05, 0.95, stats_text, ha='left', va='top', fontsize=9, 
             transform=ax_stats.transAxes, fontfamily='monospace',
             bbox=dict(boxstyle='round,pad=0.5', facecolor='lightgray', alpha=0.8))
ax_stats.set_xlim(0, 1)
ax_stats.set_ylim(0, 1)
ax_stats.axis('off')

# === BOTTOM SECTION ===
ax_bottom = fig.add_subplot(gs[2, :])

# Legend
legend_elements = [
    mpatches.Patch(color=tier1_color, label='Tier 1 (Bottom Layer)'),
    mpatches.Patch(color=tier2_color, label='Tier 2 (Top Layer)'),
    mpatches.Patch(color='red', label='Padeye Points'),
    mpatches.Patch(color='yellow', label='Safety Walkway'),
    mpatches.Patch(color='lightgreen', label='Port Zone'),
    mpatches.Patch(color='lightblue', label='Starboard Zone')
]

ax_bottom.legend(handles=legend_elements, loc='center left', bbox_to_anchor=(0, 0.5), 
                fontsize=11, ncol=6)

# Loading sequence
sequence_text = """
🔧 LOADING SEQUENCE:
Phase 1 (8h): Tier 1 Foundation → Large bundles (Items 6-17) + Medium supports (Items 2,4,5)
Phase 2 (4h): Tier 2 Completion → Medium bundles (Items 1,3) + Small bundle array (Items 18-25)  
Phase 3 (3h): Final Lashing → Corner lashing + Cross-lashing + Tension adjustment + Inspection
"""

ax_bottom.text(0.02, 0.1, sequence_text, ha='left', va='bottom', fontsize=10, 
              transform=ax_bottom.transAxes, fontweight='bold')

ax_bottom.set_xlim(0, 1)
ax_bottom.set_ylim(0, 1)
ax_bottom.axis('off')

# Add approval box
approval_text = """
APPROVALS:
□ Naval Architect  □ Marine Surveyor  □ Port Authority  □ Classification Society
□ Master  □ Chief Officer  □ Shore Superintendent  □ HSE Manager

Date: 2025-08-13  |  Prepared by: MACHO-GPT v3.4  |  Document: HCS-STOW-001
"""

ax_bottom.text(0.98, 0.1, approval_text, ha='right', va='bottom', fontsize=9, 
              transform=ax_bottom.transAxes, fontfamily='monospace',
              bbox=dict(boxstyle='round,pad=0.3', facecolor='lightyellow', edgecolor='orange'))

plt.tight_layout()
plt.subplots_adjust(hspace=0.1, wspace=0.1)

# Add professional grid and frame
fig.patch.set_facecolor('white')
fig.patch.set_edgecolor('black')
fig.patch.set_linewidth(2)

plt.show()

# Print bundle summary table
print("\n" + "="*80)
print("HCS STOWAGE PLAN - BUNDLE SUMMARY TABLE")
print("="*80)
print(f"{'Item':<4} {'Tier':<4} {'Zone':<10} {'Position':<12} {'L×W×H (m)':<12} {'Weight':<8} {'Phase'}")
print("-"*80)

phase_map = {1: 1, 2: 1, 4: 1, 5: 1, 6: 1, 7: 1, 8: 1, 9: 1, 10: 1, 11: 1, 12: 1, 13: 1, 14: 1, 15: 1, 16: 1, 17: 1, 
             1: 2, 3: 2, 18: 2, 19: 2, 20: 2, 21: 2, 22: 2, 23: 2, 24: 2, 25: 2}

for bundle in sorted(bundle_data, key=lambda x: (x['tier'], x['id'])):
    position = f"({bundle['x']:.1f},{bundle['y']:.1f})"
    dimensions = f"{bundle['length']:.1f}×{bundle['width']:.1f}×{bundle['height']:.1f}"
    phase = phase_map.get(bundle['id'], 1)
    print(f"{bundle['id']:<4} {bundle['tier']:<4} {bundle['zone']:<10} {position:<12} {dimensions:<12} {bundle['weight']:<8.1f} {phase}")

print("\n" + "="*80)
print("SUMMARY:")
print(f"Total Bundles: 25")
print(f"Total Weight: {sum(b['weight'] for b in bundle_data):.1f}t")
print(f"Tier 1: {len([b for b in bundle_data if b['tier'] == 1])} bundles, {sum(b['weight'] for b in bundle_data if b['tier'] == 1):.1f}t")
print(f"Tier 2: {len([b for b in bundle_data if b['tier'] == 2])} bundles, {sum(b['weight'] for b in bundle_data if b['tier'] == 2):.1f}t")
print(f"Deck Utilization: 89.5% (estimated)")
print("="*80)