"""
hdv_electrical_layout.py

Purpose: Electrical infrastructure layout for HDV charging station
Status: Independent module - does not modify or reference app.py
Usage: Academic/thesis - indicative electrical design only

Author: ELEXON Infrastructure Design
Note: Electrical design is indicative/assumed for thesis purposes
"""

from hdv_blocks import (
    TransformerPad, SwitchgearCabinet, CableTrench, 
    EmergencyStop, EarthingPoint
)


class ElectricalInfrastructure:
    """Complete electrical infrastructure layout"""
    
    def __init__(self):
        self.transformer = None
        self.switchgear = None
        self.cable_trenches = []
        self.emergency_stops = []
        self.earthing_points = []
        self.earthing_ring = []
        
    def design_primary_power(self, site_center_x, site_center_y):
        """Design transformer and switchgear placement"""
        transformer_x = site_center_x - 35.0
        transformer_y = site_center_y - 20.0
        
        self.transformer = TransformerPad(transformer_x, transformer_y)
        
        switchgear_x = transformer_x + 8.0
        switchgear_y = transformer_y
        self.switchgear = SwitchgearCabinet(switchgear_x, switchgear_y)
        
        return self.transformer, self.switchgear
    
    def route_main_feeders(self, switchgear_pos, distribution_point):
        """Route main LV feeders from switchgear to distribution point"""
        trench = CableTrench(
            (switchgear_pos[0], switchgear_pos[1]),
            (distribution_point[0], distribution_point[1])
        )
        self.cable_trenches.append(trench)
        return trench
    
    def route_bay_feeders(self, distribution_point, charger_positions):
        """Route individual feeders to each charger cabinet"""
        for charger_pos in charger_positions:
            trench = CableTrench(
                (distribution_point[0], distribution_point[1]),
                (charger_pos[0], charger_pos[1])
            )
            self.cable_trenches.append(trench)
    
    def place_emergency_stops(self, bay_positions):
        """Place emergency stop buttons at strategic locations"""
        for i, pos in enumerate(bay_positions):
            if i % 2 == 0:
                estop = EmergencyStop(pos[0], pos[1] - 3.0)
                self.emergency_stops.append(estop)
    
    def design_earthing_system(self, site_bounds):
        """Design perimeter earthing ring"""
        x_min, y_min, x_max, y_max = site_bounds
        
        margin = 2.0
        ring_points = [
            (x_min - margin, y_min - margin),
            (x_max + margin, y_min - margin),
            (x_max + margin, y_max + margin),
            (x_min - margin, y_max + margin),
            (x_min - margin, y_min - margin)
        ]
        
        self.earthing_ring = ring_points
        
        corners = [
            (x_min - margin, y_min - margin),
            (x_max + margin, y_min - margin),
            (x_max + margin, y_max + margin),
            (x_min - margin, y_max + margin)
        ]
        
        for corner in corners:
            ep = EarthingPoint(corner[0], corner[1])
            self.earthing_points.append(ep)
    
    def get_power_requirements_label(self):
        """Generate indicative power requirements text"""
        labels = [
            "ELECTRICAL SPECIFICATIONS (INDICATIVE - THESIS)",
            "Transformer: 2500 kVA MV/LV (assumed)",
            "Input: 10 kV or 20 kV Medium Voltage",
            "Output: 400V AC 3-phase + N + PE",
            "Charger Rating: 350 kW DC per bay (8 total)",
            "Peak Load: ~2800 kW (0.8 diversity factor)",
            "Main LV Feeder: 2x 3x300mm² Cu + PE",
            "Bay Feeders: 3x150mm² Cu + PE per charger",
            "Earthing: TN-S system, ring earth < 1 Ω",
            "Safety: EN 61851, IEC 60364, VDE 0100"
        ]
        return labels
    
    def get_all_components(self):
        """Return all electrical components for drawing"""
        return {
            'transformer': self.transformer,
            'switchgear': self.switchgear,
            'cable_trenches': self.cable_trenches,
            'emergency_stops': self.emergency_stops,
            'earthing_points': self.earthing_points,
            'earthing_ring': self.earthing_ring
        }
