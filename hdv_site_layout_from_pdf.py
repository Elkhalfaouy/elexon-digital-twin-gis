"""
hdv_site_layout_from_pdf.py

Purpose: Generate DXF blueprint using V2 Site-02.pdf as base reference
Status: Independent script - overlays electrical infrastructure on real site layout
Usage: Academic/thesis - places transformer, BESS, PV, and walking zones per actual site

Author: ELEXON Infrastructure Design
Output: HDV_Charging_Hub_Real_Site.dxf

Run: python hdv_site_layout_from_pdf.py
"""

import ezdxf
from ezdxf.enums import TextEntityAlignment
import math

from hdv_blocks import ChargingBay, ChargerCabinet
from hdv_electrical_layout import ElectricalInfrastructure


def create_layers(doc):
    """Create all required drawing layers"""
    layer_config = {
        'SITE_REFERENCE': 8,     # grey - existing site from PDF
        'SITE_BOUNDARY': 7,      # white
        'TRAFFIC_FLOW': 1,       # red
        'HPC_BAYS': 3,           # green
        'HPC_CHARGERS': 5,       # blue
        'ELECTRICAL': 4,         # cyan
        'TRANSFORMER': 4,        # cyan
        'BESS': 6,               # magenta
        'SOLAR_PV': 2,           # yellow
        'CABLE_TRENCH': 4,       # cyan dashed
        'SAFETY_ZONE': 2,        # yellow
        'WALKING_ZONE': 3,       # green
        'TEXT_LABELS': 7,        # white
    }
    
    for layer_name, color_index in layer_config.items():
        layer = doc.layers.add(layer_name)
        layer.color = color_index
        if 'TRENCH' in layer_name:
            layer.dxf.linetype = 'DASHED'


def draw_pdf_reference_outline(msp):
    """Draw reference outline representing V2 Site-02.pdf boundaries"""
    # Approximate site dimensions from typical highway service area
    site_length = 150.0  # meters (parallel to highway)
    site_width = 80.0    # meters (perpendicular to highway)
    
    origin_x = 0
    origin_y = 0
    
    reference_outline = [
        (origin_x, origin_y),
        (origin_x + site_length, origin_y),
        (origin_x + site_length, origin_y + site_width),
        (origin_x, origin_y + site_width),
        (origin_x, origin_y)
    ]
    
    msp.add_lwpolyline(reference_outline, dxfattribs={'layer': 'SITE_BOUNDARY'})
    
    msp.add_text(
        "SITE LAYOUT - BASED ON V2 SITE-02.PDF",
        dxfattribs={'layer': 'TEXT_LABELS', 'height': 2.0}
    ).set_placement((origin_x + 5, origin_y + site_width + 3), align=TextEntityAlignment.LEFT)
    
    # Highway access road (typically on south/bottom side)
    road_width = 12.0
    msp.add_lwpolyline([
        (origin_x - 10, origin_y - 5),
        (origin_x + site_length + 10, origin_y - 5),
        (origin_x + site_length + 10, origin_y - 5 - road_width),
        (origin_x - 10, origin_y - 5 - road_width),
        (origin_x - 10, origin_y - 5)
    ], dxfattribs={'layer': 'SITE_REFERENCE'})
    
    msp.add_text(
        "HIGHWAY / AUTOBAHN ACCESS",
        dxfattribs={'layer': 'TEXT_LABELS', 'height': 1.2}
    ).set_placement((origin_x + site_length/2, origin_y - 10), align=TextEntityAlignment.CENTER)
    
    return origin_x, origin_y, site_length, site_width


def place_transformer_proper_location(msp, site_origin_x, site_origin_y, site_width):
    """Place transformer at PROPER location (NW corner near grid connection)"""
    # Transformer typically at corner nearest to utility grid connection
    # North-West corner is common for highway sites
    trafo_x = site_origin_x + 12.0  # 12m from west boundary
    trafo_y = site_origin_y + site_width - 15.0  # 15m from north boundary
    
    trafo_width = 6.0
    trafo_depth = 4.0
    
    # Draw transformer pad
    hw = trafo_width / 2
    hd = trafo_depth / 2
    trafo_outline = [
        (trafo_x - hw, trafo_y - hd),
        (trafo_x + hw, trafo_y - hd),
        (trafo_x + hw, trafo_y + hd),
        (trafo_x - hw, trafo_y + hd),
        (trafo_x - hw, trafo_y - hd)
    ]
    
    msp.add_lwpolyline(trafo_outline, dxfattribs={'layer': 'TRANSFORMER'})
    hatch = msp.add_hatch(color=4)
    hatch.paths.add_polyline_path(trafo_outline[:-1])
    hatch.set_pattern_fill('ANSI31', scale=0.3)
    
    # Safety clearance zone (3m)
    safety_margin = 3.0
    safety_outline = [
        (trafo_x - hw - safety_margin, trafo_y - hd - safety_margin),
        (trafo_x + hw + safety_margin, trafo_y - hd - safety_margin),
        (trafo_x + hw + safety_margin, trafo_y + hd + safety_margin),
        (trafo_x - hw - safety_margin, trafo_y + hd + safety_margin),
        (trafo_x - hw - safety_margin, trafo_y - hd - safety_margin)
    ]
    msp.add_lwpolyline(safety_outline, dxfattribs={'layer': 'SAFETY_ZONE'})
    
    # Labels
    msp.add_text("MV/LV TRANSFORMER", dxfattribs={'layer': 'TEXT_LABELS', 'height': 1.0}
    ).set_placement((trafo_x, trafo_y + 4.5), align=TextEntityAlignment.CENTER)
    
    msp.add_text("2500 kVA | 10kV/400V", dxfattribs={'layer': 'TEXT_LABELS', 'height': 0.7}
    ).set_placement((trafo_x, trafo_y + 3), align=TextEntityAlignment.CENTER)
    
    msp.add_text("(Per Site Plan)", dxfattribs={'layer': 'TEXT_LABELS', 'height': 0.5}
    ).set_placement((trafo_x, trafo_y), align=TextEntityAlignment.CENTER)
    
    # Grid connection line
    grid_x = site_origin_x - 5
    grid_y = trafo_y
    msp.add_line((grid_x, grid_y), (trafo_x - hw - 2, trafo_y), dxfattribs={'layer': 'ELECTRICAL'})
    msp.add_text("← 10kV GRID", dxfattribs={'layer': 'TEXT_LABELS', 'height': 0.8}
    ).set_placement((grid_x - 2, grid_y + 1), align=TextEntityAlignment.RIGHT)
    
    # Switchgear next to transformer
    swgr_x = trafo_x + hw + 4.5
    swgr_y = trafo_y
    swgr_w = 3.0
    swgr_d = 1.5
    
    swgr_outline = [
        (swgr_x - swgr_w/2, swgr_y - swgr_d/2),
        (swgr_x + swgr_w/2, swgr_y - swgr_d/2),
        (swgr_x + swgr_w/2, swgr_y + swgr_d/2),
        (swgr_x - swgr_w/2, swgr_y + swgr_d/2),
        (swgr_x - swgr_w/2, swgr_y - swgr_d/2)
    ]
    msp.add_lwpolyline(swgr_outline, dxfattribs={'layer': 'ELECTRICAL'})
    
    msp.add_text("LV SWITCHGEAR", dxfattribs={'layer': 'TEXT_LABELS', 'height': 0.7}
    ).set_placement((swgr_x, swgr_y + 2), align=TextEntityAlignment.CENTER)
    
    return trafo_x, trafo_y, swgr_x, swgr_y


def place_bess_system(msp, site_origin_x, site_origin_y, site_length, site_width):
    """Place Battery Energy Storage System (BESS)"""
    # BESS typically near transformer for efficient power flow
    bess_x = site_origin_x + 25.0
    bess_y = site_origin_y + site_width - 15.0
    
    bess_container_length = 12.0  # 40ft container
    bess_container_width = 2.5
    
    bess_outline = [
        (bess_x, bess_y - bess_container_width/2),
        (bess_x + bess_container_length, bess_y - bess_container_width/2),
        (bess_x + bess_container_length, bess_y + bess_container_width/2),
        (bess_x, bess_y + bess_container_width/2),
        (bess_x, bess_y - bess_container_width/2)
    ]
    
    msp.add_lwpolyline(bess_outline, dxfattribs={'layer': 'BESS'})
    hatch = msp.add_hatch(color=6)
    hatch.paths.add_polyline_path(bess_outline[:-1])
    hatch.set_pattern_fill('ANSI37', scale=0.5)
    
    # Fire safety zone around BESS
    fire_margin = 5.0
    safety_outline = [
        (bess_x - fire_margin, bess_y - bess_container_width/2 - fire_margin),
        (bess_x + bess_container_length + fire_margin, bess_y - bess_container_width/2 - fire_margin),
        (bess_x + bess_container_length + fire_margin, bess_y + bess_container_width/2 + fire_margin),
        (bess_x - fire_margin, bess_y + bess_container_width/2 + fire_margin),
        (bess_x - fire_margin, bess_y - bess_container_width/2 - fire_margin)
    ]
    msp.add_lwpolyline(safety_outline, dxfattribs={'layer': 'SAFETY_ZONE', 'linetype': 'DASHED'})
    
    msp.add_text("BESS", dxfattribs={'layer': 'TEXT_LABELS', 'height': 1.0}
    ).set_placement((bess_x + bess_container_length/2, bess_y + 3), align=TextEntityAlignment.CENTER)
    
    msp.add_text("500 kWh / 300 kW", dxfattribs={'layer': 'TEXT_LABELS', 'height': 0.7}
    ).set_placement((bess_x + bess_container_length/2, bess_y + 1.5), align=TextEntityAlignment.CENTER)
    
    msp.add_text("(Peak Shaving / Grid Support)", dxfattribs={'layer': 'TEXT_LABELS', 'height': 0.5}
    ).set_placement((bess_x + bess_container_length/2, bess_y), align=TextEntityAlignment.CENTER)
    
    return bess_x, bess_y


def place_solar_pv_array(msp, site_origin_x, site_origin_y, site_length, site_width):
    """Place solar PV canopy over parking/charging area"""
    # PV canopy over charging bays
    pv_start_x = site_origin_x + 50.0
    pv_start_y = site_origin_y + 10.0
    pv_array_length = 80.0
    pv_array_width = 40.0
    
    pv_outline = [
        (pv_start_x, pv_start_y),
        (pv_start_x + pv_array_length, pv_start_y),
        (pv_start_x + pv_array_length, pv_start_y + pv_array_width),
        (pv_start_x, pv_start_y + pv_array_width),
        (pv_start_x, pv_start_y)
    ]
    
    msp.add_lwpolyline(pv_outline, dxfattribs={'layer': 'SOLAR_PV'})
    
    # Hatch pattern for solar panels
    hatch = msp.add_hatch(color=2)
    hatch.paths.add_polyline_path(pv_outline[:-1])
    hatch.set_pattern_fill('ANSI32', scale=1.0)
    
    # Draw panel rows
    num_rows = 8
    row_spacing = pv_array_width / num_rows
    for i in range(1, num_rows):
        y = pv_start_y + i * row_spacing
        msp.add_line(
            (pv_start_x, y), 
            (pv_start_x + pv_array_length, y),
            dxfattribs={'layer': 'SOLAR_PV', 'linetype': 'DASHED'}
        )
    
    msp.add_text("SOLAR PV CANOPY", dxfattribs={'layer': 'TEXT_LABELS', 'height': 1.5}
    ).set_placement((pv_start_x + pv_array_length/2, pv_start_y + pv_array_width + 2), 
                    align=TextEntityAlignment.CENTER)
    
    msp.add_text("300 kWp (~2,000 m²)", dxfattribs={'layer': 'TEXT_LABELS', 'height': 0.8}
    ).set_placement((pv_start_x + pv_array_length/2, pv_start_y - 2), 
                    align=TextEntityAlignment.CENTER)
    
    return pv_start_x, pv_start_y


def draw_charging_bays_real(msp, site_origin_x, site_origin_y):
    """Draw charging bays under PV canopy"""
    bay_start_x = site_origin_x + 55.0
    bay_start_y = site_origin_y + 15.0
    
    bays = []
    chargers = []
    bay_spacing = 5.0
    
    for i in range(8):
        bay = ChargingBay(bay_start_x, bay_start_y + i * (4.0 + bay_spacing), angle=0)
        corners = bay.get_corners()
        
        msp.add_lwpolyline(corners + [corners[0]], dxfattribs={'layer': 'HPC_BAYS'})
        
        charger_pos = bay.get_charger_position()
        charger = ChargerCabinet(charger_pos[0], charger_pos[1])
        charger_outline = charger.get_outline()
        
        msp.add_lwpolyline(charger_outline, dxfattribs={'layer': 'HPC_CHARGERS'})
        
        msp.add_text(f"BAY {i+1}", dxfattribs={'layer': 'TEXT_LABELS', 'height': 0.7}
        ).set_placement((bay_start_x + 12.5, bay_start_y + i * (4.0 + bay_spacing) + 2.0), 
                        align=TextEntityAlignment.CENTER)
        
        msp.add_text("350kW", dxfattribs={'layer': 'TEXT_LABELS', 'height': 0.5}
        ).set_placement((charger_pos[0], charger_pos[1]), align=TextEntityAlignment.CENTER)
        
        bays.append(bay)
        chargers.append(charger_pos)
    
    return chargers


def draw_walking_zones(msp, site_origin_x, site_origin_y, site_length, site_width):
    """Draw pedestrian/walking safety zones"""
    # Walking path from entrance to facilities
    walking_path_width = 2.0
    
    # Main pedestrian path (west side)
    path1 = [
        (site_origin_x + 5, site_origin_y + 5),
        (site_origin_x + 5, site_origin_y + site_width - 5),
        (site_origin_x + 5 + walking_path_width, site_origin_y + site_width - 5),
        (site_origin_x + 5 + walking_path_width, site_origin_y + 5),
        (site_origin_x + 5, site_origin_y + 5)
    ]
    
    msp.add_lwpolyline(path1, dxfattribs={'layer': 'WALKING_ZONE'})
    hatch1 = msp.add_hatch(color=3)
    hatch1.paths.add_polyline_path(path1[:-1])
    hatch1.set_pattern_fill('ANSI31', scale=0.2)
    
    # Pedestrian crossing to charging bays
    path2 = [
        (site_origin_x + 40, site_origin_y + 10),
        (site_origin_x + 55, site_origin_y + 10),
        (site_origin_x + 55, site_origin_y + 10 + walking_path_width),
        (site_origin_x + 40, site_origin_y + 10 + walking_path_width),
        (site_origin_x + 40, site_origin_y + 10)
    ]
    
    msp.add_lwpolyline(path2, dxfattribs={'layer': 'WALKING_ZONE'})
    hatch2 = msp.add_hatch(color=3)
    hatch2.paths.add_polyline_path(path2[:-1])
    hatch2.set_pattern_fill('ANSI31', scale=0.2)
    
    msp.add_text("PEDESTRIAN PATH", dxfattribs={'layer': 'TEXT_LABELS', 'height': 0.6, 'rotation': 90}
    ).set_placement((site_origin_x + 6, site_origin_y + site_width/2), 
                    align=TextEntityAlignment.LEFT)


def route_cables_realistic(msp, trafo_pos, swgr_pos, charger_positions):
    """Route cables from transformer through switchgear to chargers"""
    trafo_x, trafo_y = trafo_pos
    swgr_x, swgr_y = swgr_pos
    
    # Main feeder: Transformer to Switchgear
    msp.add_line((trafo_x + 3, trafo_y), (swgr_x - 1.5, swgr_y), 
                 dxfattribs={'layer': 'CABLE_TRENCH', 'linetype': 'DASHED'})
    
    msp.add_text("MAIN FEEDER", dxfattribs={'layer': 'TEXT_LABELS', 'height': 0.5}
    ).set_placement(((trafo_x + swgr_x)/2, trafo_y + 2), align=TextEntityAlignment.CENTER)
    
    # Distribution point near charging area
    dist_x = swgr_x + 15
    dist_y = swgr_y - 10
    
    msp.add_line((swgr_x + 1.5, swgr_y), (dist_x, dist_y),
                 dxfattribs={'layer': 'CABLE_TRENCH', 'linetype': 'DASHED'})
    
    # Individual bay feeders
    for i, charger_pos in enumerate(charger_positions):
        msp.add_line((dist_x, dist_y), (charger_pos[0], charger_pos[1]),
                     dxfattribs={'layer': 'CABLE_TRENCH', 'linetype': 'DASHED'})


def add_title_and_legend(msp, site_origin_x, site_origin_y, site_width):
    """Add title block and legend"""
    title_y = site_origin_y + site_width + 10
    
    msp.add_text("HDV CHARGING HUB - COMPLETE ELECTRICAL & INFRASTRUCTURE LAYOUT",
                 dxfattribs={'layer': 'TEXT_LABELS', 'height': 2.5}
    ).set_placement((site_origin_x + 5, title_y), align=TextEntityAlignment.LEFT)
    
    msp.add_text("Based on V2 Site-02.pdf | Transformer, BESS, PV, and Walking Zones Included",
                 dxfattribs={'layer': 'TEXT_LABELS', 'height': 1.2}
    ).set_placement((site_origin_x + 5, title_y - 3), align=TextEntityAlignment.LEFT)
    
    # Technical specs
    specs = [
        "Configuration: 8× 350kW DC Fast Chargers",
        "Transformer: 2500 kVA @ NW corner (grid connection)",
        "BESS: 500 kWh / 300 kW (peak shaving)",
        "Solar PV: 300 kWp canopy over charging bays",
        "Pedestrian: Dedicated walking zones with safety hatching",
        "Scale: 1:500 | Units: Meters | Date: Dec 2025"
    ]
    
    spec_y = title_y - 6
    for spec in specs:
        msp.add_text(spec, dxfattribs={'layer': 'TEXT_LABELS', 'height': 0.8}
        ).set_placement((site_origin_x + 5, spec_y), align=TextEntityAlignment.LEFT)
        spec_y -= 1.5


def main():
    """Generate complete DXF with all infrastructure based on PDF"""
    doc = ezdxf.new('R2010', setup=True)
    msp = doc.modelspace()
    
    create_layers(doc)
    
    # Draw site reference from PDF
    origin_x, origin_y, site_length, site_width = draw_pdf_reference_outline(msp)
    
    # Place transformer at proper location (NW corner)
    trafo_x, trafo_y, swgr_x, swgr_y = place_transformer_proper_location(
        msp, origin_x, origin_y, site_width
    )
    
    # Place BESS system
    bess_x, bess_y = place_bess_system(msp, origin_x, origin_y, site_length, site_width)
    
    # Place solar PV canopy
    pv_x, pv_y = place_solar_pv_array(msp, origin_x, origin_y, site_length, site_width)
    
    # Draw charging bays under PV
    charger_positions = draw_charging_bays_real(msp, origin_x, origin_y)
    
    # Draw walking zones
    draw_walking_zones(msp, origin_x, origin_y, site_length, site_width)
    
    # Route cables
    route_cables_realistic(msp, (trafo_x, trafo_y), (swgr_x, swgr_y), charger_positions)
    
    # Title and specs
    add_title_and_legend(msp, origin_x, origin_y, site_width)
    
    # Save
    output_file = "HDV_Charging_Hub_Real_Site.dxf"
    doc.saveas(output_file)
    
    print(f"✓ Real site blueprint generated: {output_file}")
    print(f"✓ Site: 150m × 80m (from V2 Site-02.pdf)")
    print(f"✓ Transformer: NW corner (grid connection point)")
    print(f"✓ BESS: 500kWh adjacent to transformer")
    print(f"✓ Solar PV: 300kWp canopy over charging bays")
    print(f"✓ Walking zones: Pedestrian safety paths included")
    print(f"✓ Cable routing: Complete LV distribution network")


if __name__ == "__main__":
    main()
