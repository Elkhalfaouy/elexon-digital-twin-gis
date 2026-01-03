"""
hdv_blocks.py

Purpose: Reusable geometric blocks for HDV charging station blueprint
Status: Independent module - does not modify or reference app.py
Usage: Academic/thesis - indicative layout only

Author: ELEXON Infrastructure Design
"""

import math


class ChargingBay:
    """Single HDV charging bay with charger cabinet"""
    
    def __init__(self, x, y, angle=0):
        self.x = x
        self.y = y
        self.angle = angle
        self.length = 25.0  # meters
        self.width = 4.0    # meters
        
    def get_corners(self):
        """Returns bay corner coordinates [x, y] in clockwise order"""
        rad = math.radians(self.angle)
        cos_a = math.cos(rad)
        sin_a = math.sin(rad)
        
        corners = [
            (0, 0),
            (self.length, 0),
            (self.length, self.width),
            (0, self.width)
        ]
        
        rotated = []
        for cx, cy in corners:
            rx = cx * cos_a - cy * sin_a + self.x
            ry = cx * sin_a + cy * cos_a + self.y
            rotated.append((rx, ry))
        
        return rotated
    
    def get_charger_position(self):
        """Returns charger cabinet center position"""
        rad = math.radians(self.angle)
        charger_offset_x = 2.5  # 2.5m from start of bay
        charger_offset_y = -1.5  # 1.5m outside bay
        
        cos_a = math.cos(rad)
        sin_a = math.sin(rad)
        
        cx = charger_offset_x * cos_a - charger_offset_y * sin_a + self.x
        cy = charger_offset_x * sin_a + charger_offset_y * cos_a + self.y
        
        return (cx, cy)


class ChargerCabinet:
    """DC charger cabinet (350 kW typical)"""
    
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.width = 1.2   # meters
        self.height = 0.8  # meters
        
    def get_outline(self):
        """Returns cabinet outline as list of (x,y) tuples"""
        hw = self.width / 2
        hh = self.height / 2
        return [
            (self.x - hw, self.y - hh),
            (self.x + hw, self.y - hh),
            (self.x + hw, self.y + hh),
            (self.x - hw, self.y + hh),
            (self.x - hw, self.y - hh)
        ]


class TransformerPad:
    """MV/LV transformer foundation pad"""
    
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.width = 6.0   # meters
        self.depth = 4.0   # meters
        
    def get_outline(self):
        """Returns transformer pad outline"""
        hw = self.width / 2
        hd = self.depth / 2
        return [
            (self.x - hw, self.y - hd),
            (self.x + hw, self.y - hd),
            (self.x + hw, self.y + hd),
            (self.x - hw, self.y + hd),
            (self.x - hw, self.y - hd)
        ]
    
    def get_safety_zone(self):
        """Returns 3m safety clearance zone around transformer"""
        safety_margin = 3.0
        hw = self.width / 2 + safety_margin
        hd = self.depth / 2 + safety_margin
        return [
            (self.x - hw, self.y - hd),
            (self.x + hw, self.y - hd),
            (self.x + hw, self.y + hd),
            (self.x - hw, self.y + hd),
            (self.x - hw, self.y - hd)
        ]


class SwitchgearCabinet:
    """LV switchgear cabinet"""
    
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.width = 3.0   # meters
        self.depth = 1.5   # meters
        
    def get_outline(self):
        """Returns switchgear outline"""
        hw = self.width / 2
        hd = self.depth / 2
        return [
            (self.x - hw, self.y - hd),
            (self.x + hw, self.y - hd),
            (self.x + hw, self.y + hd),
            (self.x - hw, self.y + hd),
            (self.x - hw, self.y - hd)
        ]


class CableTrench:
    """Underground cable routing trench"""
    
    def __init__(self, start_point, end_point):
        self.start = start_point
        self.end = end_point
        self.width = 0.6  # 600mm typical trench width
        
    def get_centerline(self):
        """Returns trench centerline coordinates"""
        return [self.start, self.end]
    
    def get_parallel_offset(self, offset_distance):
        """Returns parallel line at offset distance"""
        dx = self.end[0] - self.start[0]
        dy = self.end[1] - self.start[1]
        length = math.sqrt(dx**2 + dy**2)
        
        if length == 0:
            return [self.start, self.end]
        
        nx = -dy / length
        ny = dx / length
        
        p1 = (self.start[0] + nx * offset_distance, 
              self.start[1] + ny * offset_distance)
        p2 = (self.end[0] + nx * offset_distance,
              self.end[1] + ny * offset_distance)
        
        return [p1, p2]


class TruckCirculation:
    """Truck traffic circulation path generator"""
    
    @staticmethod
    def generate_entry_curve(start_point, end_point, radius=12.0):
        """Generate entry curve with minimum truck turning radius"""
        x1, y1 = start_point
        x2, y2 = end_point
        
        points = []
        num_segments = 20
        
        for i in range(num_segments + 1):
            t = i / num_segments
            x = x1 + (x2 - x1) * t
            y = y1 + (y2 - y1) * t
            points.append((x, y))
        
        return points
    
    @staticmethod
    def generate_arc(center, radius, start_angle, end_angle, segments=30):
        """Generate circular arc for turning path"""
        points = []
        angle_range = end_angle - start_angle
        
        for i in range(segments + 1):
            angle = start_angle + (angle_range * i / segments)
            rad = math.radians(angle)
            x = center[0] + radius * math.cos(rad)
            y = center[1] + radius * math.sin(rad)
            points.append((x, y))
        
        return points


class EmergencyStop:
    """Emergency stop button location"""
    
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.symbol_radius = 0.5  # meters
        
    def get_circle(self):
        """Returns emergency stop symbol as circle"""
        return (self.x, self.y, self.symbol_radius)


class EarthingPoint:
    """Earthing/grounding connection point"""
    
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.symbol_size = 0.8
        
    def get_symbol(self):
        """Returns earthing symbol as cross"""
        s = self.symbol_size / 2
        horizontal = [(self.x - s, self.y), (self.x + s, self.y)]
        vertical = [(self.x, self.y - s), (self.x, self.y + s)]
        return [horizontal, vertical]
