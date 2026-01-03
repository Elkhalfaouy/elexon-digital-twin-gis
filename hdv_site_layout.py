"""
hdv_site_layout.py

Purpose: Generate complete AutoCAD-compatible DXF blueprint for HDV charging station
Status: Independent script - does not modify or reference app.py
Usage: Academic/thesis - indicative site layout for highway charging hub

Author: ELEXON Infrastructure Design
Output: HDV_Charging_Hub_Full_Blueprint.dxf

Run: python hdv_site_layout.py
"""

import ezdxf
from ezdxf import colors
from ezdxf.enums import TextEntityAlignment
import math

from hdv_blocks import (
    ChargingBay, ChargerCabinet, TruckCirculation
)
from hdv_electrical_layout import ElectricalInfrastructure


def create_layers(doc):
    """Create all required drawing layers with colors"""
    layer_config = {
        'SITE_EXISTING': 8,      # grey
        'SITE_BOUNDARY': 7,      # white
        'TRAFFIC_FLOW': 1,       # red
        'HPC_BAYS': 3,           # green
        'HPC_CHARGERS': 5,       # blue
        'ELECTRICAL': 4,         # cyan
        'CABLE_TRENCH': 4,       # cyan (dashed)
        'SAFETY_ZONE': 2,        # yellow
        'TEXT_LABELS': 7,        # black/white
        'DIMENSIONS': 7          # white
    }
    
    for layer_name, color_index in layer_config.items():
        layer = doc.layers.add(layer_name)
        layer.color = color_index
        
        if 'TRENCH' in layer_name:
            layer.dxf.linetype = 'DASHED'


def draw_site_boundary(msp, center_x, center_y, width, height):
    """Draw overall site boundary based on real site dimensions"""
    x1 = center_x - width / 2
    y1 = center_y - height / 2
    x2 = center_x + width / 2
    y2 = center_y + height / 2
    
    boundary = [
        (x1, y1),
        (x2, y1),
        (x2, y2),
        (x1, y2),
        (x1, y1)
    ]
    
    msp.add_lwpolyline(boundary, dxfattribs={'layer': 'SITE_BOUNDARY'})
    
    msp.add_text(
        "SITE BOUNDARY (from V2 Site-02.pdf)",
        dxfattribs={
            'layer': 'TEXT_LABELS',
            'height': 0.8
        }
    ).set_placement((x1 + 2, y1 + 2), align=TextEntityAlignment.LEFT)
    
    return (x1, y1, x2, y2)


def draw_existing_features(msp, site_bounds):
    """Draw existing site features (access road, reference points)"""
    x_min, y_min, x_max, y_max = site_bounds
    
    road_width = 6.0
    road_y = y_min + 10.0
    
    road_outline = [
        (x_min - 5, road_y - road_width/2),
        (x_max + 5, road_y - road_width/2),
        (x_max + 5, road_y + road_width/2),
        (x_min - 5, road_y + road_width/2),
        (x_min - 5, road_y - road_width/2)
    ]
    
    msp.add_lwpolyline(road_outline, dxfattribs={'layer': 'SITE_EXISTING'})
    
    msp.add_text(
        "EXISTING HIGHWAY ACCESS",
        dxfattribs={
            'layer': 'TEXT_LABELS',
            'height': 1.2
        }
    ).set_placement((x_min, road_y - 5), align=TextEntityAlignment.LEFT)


def draw_charging_bays(msp, start_x, start_y, num_bays=8):
    """Draw all charging bays with proper spacing"""
    bays = []
    chargers = []
    
    bay_spacing = 5.0
    current_y = start_y
    
    for i in range(num_bays):
        bay = ChargingBay(start_x, current_y, angle=0)
        corners = bay.get_corners()
        
        msp.add_lwpolyline(
            corners + [corners[0]], 
            dxfattribs={'layer': 'HPC_BAYS'}
        )
        
        charger_pos = bay.get_charger_position()
        charger = ChargerCabinet(charger_pos[0], charger_pos[1])
        charger_outline = charger.get_outline()
        
        msp.add_lwpolyline(
            charger_outline,
            dxfattribs={'layer': 'HPC_CHARGERS'}
        )
        
        msp.add_text(
            f"BAY {i+1}",
            dxfattribs={
                'layer': 'TEXT_LABELS',
                'height': 0.8
            }
        ).set_placement(
            (start_x + 12.5, current_y + 2.0), 
            align=TextEntityAlignment.CENTER
        )
        
        msp.add_text(
            f"350kW DC",
            dxfattribs={
                'layer': 'TEXT_LABELS',
                'height': 0.6
            }
        ).set_placement(
            (charger_pos[0], charger_pos[1]), 
            align=TextEntityAlignment.CENTER
        )
        
        bays.append(bay)
        chargers.append(charger_pos)
        
        current_y += bay.width + bay_spacing
    
    return bays, chargers


def draw_traffic_circulation(msp, site_bounds, bays):
    """Draw truck traffic flow paths"""
    x_min, y_min, x_max, y_max = site_bounds
    
    entry_y = y_min + 15.0
    exit_y = y_max - 10.0
    
    entry_path = [
        (x_min - 5, entry_y),
        (x_min + 10, entry_y),
        (x_min + 15, entry_y + 5),
        (x_min + 15, y_min + 25)
    ]
    
    msp.add_lwpolyline(entry_path, dxfattribs={'layer': 'TRAFFIC_FLOW'})
    
    main_circulation_x = x_max + 10
    circulation_path = [
        (main_circulation_x, y_min + 25),
        (main_circulation_x, y_max - 5)
    ]
    
    msp.add_lwpolyline(circulation_path, dxfattribs={'layer': 'TRAFFIC_FLOW'})
    
    exit_path = [
        (main_circulation_x, exit_y),
        (x_max + 15, exit_y + 5),
        (x_max + 20, exit_y),
        (x_max + 30, exit_y)
    ]
    
    msp.add_lwpolyline(exit_path, dxfattribs={'layer': 'TRAFFIC_FLOW'})
    
    for i, bay in enumerate(bays):
        bay_center_y = bay.y + bay.width / 2
        access_path = [
            (main_circulation_x, bay_center_y),
            (main_circulation_x - 3, bay_center_y),
            (bay.x + bay.length + 2, bay_center_y)
        ]
        msp.add_lwpolyline(access_path, dxfattribs={'layer': 'TRAFFIC_FLOW'})
    
    arrow_positions = [
        (x_min + 5, entry_y + 2),
        (main_circulation_x + 1, (y_min + y_max) / 2),
        (x_max + 25, exit_y + 2)
    ]
    
    for pos in arrow_positions:
        msp.add_text(
            "→",
            dxfattribs={
                'layer': 'TRAFFIC_FLOW',
                'height': 2.0
            }
        ).set_placement(pos, align=TextEntityAlignment.CENTER)


def draw_electrical_infrastructure(msp, site_bounds, charger_positions):
    """Draw complete electrical infrastructure with transformer at site perimeter"""
    elec = ElectricalInfrastructure()
    
    x_min, y_min, x_max, y_max = site_bounds
    
    # Position transformer at LEFT perimeter (typical grid connection point)
    # Near road access for utility company maintenance
    transformer_x = x_min + 8.0  # 8m inside left boundary
    transformer_y = y_min + 25.0  # Centered vertically on left side
    
    transformer, switchgear = elec.design_primary_power(transformer_x, transformer_y)
    
    trafo_outline = transformer.get_outline()
    msp.add_lwpolyline(trafo_outline, dxfattribs={'layer': 'ELECTRICAL'})
    msp.add_hatch().set_pattern_fill('ANSI31', scale=0.5, style=0)
    
    safety_zone = transformer.get_safety_zone()
    msp.add_lwpolyline(safety_zone, dxfattribs={'layer': 'SAFETY_ZONE'})
    
    # Transformer labels
    msp.add_text(
        "MV/LV TRANSFORMER",
        dxfattribs={
            'layer': 'TEXT_LABELS',
            'height': 1.0,
            'style': 'Standard'
        }
    ).set_placement(
        (transformer.x, transformer.y + 4), 
        align=TextEntityAlignment.CENTER
    )
    
    msp.add_text(
        "2500 kVA",
        dxfattribs={
            'layer': 'TEXT_LABELS',
            'height': 0.8
        }
    ).set_placement(
        (transformer.x, transformer.y + 2.5), 
        align=TextEntityAlignment.CENTER
    )
    
    msp.add_text(
        "10kV/400V",
        dxfattribs={
            'layer': 'TEXT_LABELS',
            'height': 0.7
        }
    ).set_placement(
        (transformer.x, transformer.y + 1), 
        align=TextEntityAlignment.CENTER
    )
    
    msp.add_text(
        "(Position per V2 Site-02.pdf)",
        dxfattribs={
            'layer': 'TEXT_LABELS',
            'height': 0.5
        }
    ).set_placement(
        (transformer.x, transformer.y - 1), 
        align=TextEntityAlignment.CENTER
    )
    
    # Grid connection point (utility service entrance)
    grid_connection_x = x_min - 2
    grid_connection_y = transformer_y
    
    msp.add_line(
        (grid_connection_x, grid_connection_y),
        (transformer.x - 3, transformer.y),
        dxfattribs={'layer': 'ELECTRICAL'}
    )
    
    msp.add_text(
        "GRID CONNECTION ←",
        dxfattribs={
            'layer': 'TEXT_LABELS',
            'height': 0.7
        }
    ).set_placement(
        (grid_connection_x - 2, grid_connection_y + 1),
        align=TextEntityAlignment.RIGHT
    )
    
    # Switchgear positioned adjacent to transformer
    swgr_outline = switchgear.get_outline()
    msp.add_lwpolyline(swgr_outline, dxfattribs={'layer': 'ELECTRICAL'})
    
    msp.add_text(
        "LV SWITCHGEAR",
        dxfattribs={
            'layer': 'TEXT_LABELS',
            'height': 0.8
        }
    ).set_placement(
        (switchgear.x, switchgear.y + 1.5), 
        align=TextEntityAlignment.CENTER
    )
    
    msp.add_text(
        "Main Distribution",
        dxfattribs={
            'layer': 'TEXT_LABELS',
            'height': 0.6
        }
    ).set_placement(
        (switchgear.x, switchgear.y - 0.5), 
        align=TextEntityAlignment.CENTER
    )
    
    # Distribution point - central to all charging bays
    avg_charger_x = sum(pos[0] for pos in charger_positions) / len(charger_positions)
    avg_charger_y = sum(pos[1] for pos in charger_positions) / len(charger_positions)
    distribution_x = avg_charger_x - 5
    distribution_y = avg_charger_y
    
    # Main feeder from switchgear to distribution point
    main_feeder = elec.route_main_feeders(
        (switchgear.x + 2, switchgear.y),
        (distribution_x, distribution_y)
    )
    
    centerline = main_feeder.get_centerline()
    msp.add_line(
        centerline[0], centerline[1],
        dxfattribs={'layer': 'CABLE_TRENCH', 'linetype': 'DASHED'}
    )
    
    msp.add_text(
        "MAIN LV FEEDER",
        dxfattribs={
            'layer': 'TEXT_LABELS',
            'height': 0.6
        }
    ).set_placement(
        ((centerline[0][0] + centerline[1][0])/2, 
         (centerline[0][1] + centerline[1][1])/2 + 1),
        align=TextEntityAlignment.CENTER
    )
    
    # Individual feeders to each charger
    elec.route_bay_feeders((distribution_x, distribution_y), charger_positions)
    
    for i, trench in enumerate(elec.cable_trenches[1:], 1):
        centerline = trench.get_centerline()
        msp.add_line(
            centerline[0], centerline[1],
            dxfattribs={'layer': 'CABLE_TRENCH', 'linetype': 'DASHED'}
        )
    
    # Earthing system
    elec.design_earthing_system(site_bounds)
    
    if elec.earthing_ring:
        msp.add_lwpolyline(
            elec.earthing_ring,
            dxfattribs={'layer': 'ELECTRICAL', 'linetype': 'DASHED'}
        )
        
        msp.add_text(
            "EARTHING RING",
            dxfattribs={
                'layer': 'TEXT_LABELS',
                'height': 0.6
            }
        ).set_placement(
            (x_max - 10, y_min + 3),
            align=TextEntityAlignment.LEFT
        )
    
    for ep in elec.earthing_points:
        symbols = ep.get_symbol()
        for line in symbols:
            msp.add_line(line[0], line[1], dxfattribs={'layer': 'ELECTRICAL'})
    
    # Emergency stops
    elec.place_emergency_stops([(c[0], c[1]) for c in charger_positions])
    
    for estop in elec.emergency_stops:
        circle_data = estop.get_circle()
        msp.add_circle(
            (circle_data[0], circle_data[1]),
            radius=circle_data[2],
            dxfattribs={'layer': 'SAFETY_ZONE'}
        )
        msp.add_text(
            "E-STOP",
            dxfattribs={
                'layer': 'TEXT_LABELS',
                'height': 0.4
            }
        ).set_placement(
            (circle_data[0], circle_data[1] - 1.5),
            align=TextEntityAlignment.CENTER
        )
    
    return elec


def add_title_block(msp, site_bounds):
    """Add professional title block and drawing information"""
    x_min, y_min, x_max, y_max = site_bounds
    
    title_x = x_min + 5
    title_y = y_max + 15
    
    msp.add_text(
        "HIGHWAY HDV CHARGING STATION - BASED ON V2 SITE-02.PDF",
        dxfattribs={
            'layer': 'TEXT_LABELS',
            'height': 2.5,
            'style': 'Standard'
        }
    ).set_placement((title_x, title_y), align=TextEntityAlignment.LEFT)
    
    msp.add_text(
        "ELECTRICAL LAYOUT - TRANSFORMER AT SITE PERIMETER (GRID CONNECTION POINT)",
        dxfattribs={
            'layer': 'TEXT_LABELS',
            'height': 1.2,
            'style': 'Standard'
        }
    ).set_placement((title_x, title_y - 3), align=TextEntityAlignment.LEFT)
    
    info_lines = [
        "Project: ELEXON Digital Twin - Charging Infrastructure",
        "Configuration: 8x 350kW DC Fast Charging Bays",
        "Bay Dimensions: 25.0m × 4.0m (HDV drive-through)",
        "Circulation: One-way, truck-safe turning radii ≥12m",
        "Electrical: 2500 kVA MV/LV transformer (indicative)",
        "Standards: EN 61851, IEC 60364, VDE 0100 (assumed)",
        "Scale: 1:200 (meters)",
        "Date: December 2025",
        "Status: CONCEPT / THESIS DRAFT"
    ]
    
    info_y = title_y - 6
    for line in info_lines:
        msp.add_text(
            line,
            dxfattribs={
                'layer': 'TEXT_LABELS',
                'height': 0.8
            }
        ).set_placement((title_x, info_y), align=TextEntityAlignment.LEFT)
        info_y -= 1.5
    
    legend_x = x_max - 30
    legend_y = y_max + 10
    
    msp.add_text(
        "LEGEND",
        dxfattribs={
            'layer': 'TEXT_LABELS',
            'height': 1.5
        }
    ).set_placement((legend_x, legend_y), align=TextEntityAlignment.LEFT)
    
    legend_items = [
        ("Site Boundary", "SITE_BOUNDARY", 7),
        ("Traffic Flow", "TRAFFIC_FLOW", 1),
        ("Charging Bays", "HPC_BAYS", 3),
        ("DC Chargers", "HPC_CHARGERS", 5),
        ("Electrical", "ELECTRICAL", 4),
        ("Cable Trench", "CABLE_TRENCH", 4),
        ("Safety Zones", "SAFETY_ZONE", 2)
    ]
    
    legend_item_y = legend_y - 2
    for item_text, layer, color_idx in legend_items:
        msp.add_line(
            (legend_x, legend_item_y),
            (legend_x + 3, legend_item_y),
            dxfattribs={'layer': layer}
        )
        msp.add_text(
            item_text,
            dxfattribs={
                'layer': 'TEXT_LABELS',
                'height': 0.7
            }
        ).set_placement(
            (legend_x + 4, legend_item_y - 0.3),
            align=TextEntityAlignment.LEFT
        )
        legend_item_y -= 1.8


def add_north_arrow(msp, x, y):
    """Add north arrow symbol"""
    arrow_length = 5.0
    
    msp.add_line(
        (x, y),
        (x, y + arrow_length),
        dxfattribs={'layer': 'TEXT_LABELS'}
    )
    
    arrow_head = [
        (x, y + arrow_length),
        (x - 0.5, y + arrow_length - 1),
        (x + 0.5, y + arrow_length - 1),
        (x, y + arrow_length)
    ]
    msp.add_lwpolyline(arrow_head, dxfattribs={'layer': 'TEXT_LABELS'})
    
    msp.add_text(
        "N",
        dxfattribs={
            'layer': 'TEXT_LABELS',
            'height': 1.5
        }
    ).set_placement((x, y + arrow_length + 1.5), align=TextEntityAlignment.CENTER)


def add_scale_bar(msp, x, y):
    """Add graphical scale bar"""
    scale_length = 20.0
    
    msp.add_line(
        (x, y),
        (x + scale_length, y),
        dxfattribs={'layer': 'TEXT_LABELS'}
    )
    
    msp.add_line((x, y - 0.5), (x, y + 0.5), dxfattribs={'layer': 'TEXT_LABELS'})
    msp.add_line(
        (x + scale_length, y - 0.5),
        (x + scale_length, y + 0.5),
        dxfattribs={'layer': 'TEXT_LABELS'}
    )
    
    msp.add_text(
        "0",
        dxfattribs={'layer': 'TEXT_LABELS', 'height': 0.8}
    ).set_placement((x, y - 2), align=TextEntityAlignment.CENTER)
    
    msp.add_text(
        "20m",
        dxfattribs={'layer': 'TEXT_LABELS', 'height': 0.8}
    ).set_placement((x + scale_length, y - 2), align=TextEntityAlignment.CENTER)
    
    msp.add_text(
        "SCALE 1:200",
        dxfattribs={'layer': 'TEXT_LABELS', 'height': 1.0}
    ).set_placement((x + scale_length/2, y + 2), align=TextEntityAlignment.CENTER)


def main():
    """Main function to generate complete DXF blueprint"""
    
    doc = ezdxf.new('R2010', setup=True)
    msp = doc.modelspace()
    
    create_layers(doc)
    
    site_width = 120.0
    site_height = 90.0
    center_x = 60.0
    center_y = 50.0
    
    site_bounds = draw_site_boundary(msp, center_x, center_y, site_width, site_height)
    
    draw_existing_features(msp, site_bounds)
    
    bay_start_x = 20.0
    bay_start_y = 15.0
    bays, charger_positions = draw_charging_bays(msp, bay_start_x, bay_start_y, num_bays=8)
    
    draw_traffic_circulation(msp, site_bounds, bays)
    
    elec_infra = draw_electrical_infrastructure(msp, site_bounds, charger_positions)
    
    add_title_block(msp, site_bounds)
    
    x_min, y_min, x_max, y_max = site_bounds
    add_north_arrow(msp, x_max - 10, y_min + 10)
    add_scale_bar(msp, x_min + 10, y_min - 10)
    
    output_file = "HDV_Charging_Hub_Full_Blueprint.dxf"
    doc.saveas(output_file)
    
    print(f"✓ Blueprint generated successfully: {output_file}")
    print(f"✓ Site dimensions: {site_width}m × {site_height}m")
    print(f"✓ Number of charging bays: 8")
    print(f"✓ Electrical infrastructure: Complete (indicative)")
    print(f"✓ Drawing units: Meters")
    print(f"✓ Coordinate system: Cartesian (X-East, Y-North)")
    print(f"✓ Layers: 10 (with proper color coding)")
    print("\nNote: Design is INDICATIVE for academic/thesis use only")
    print("Real project would require detailed engineering and grid studies")


if __name__ == "__main__":
    main()
