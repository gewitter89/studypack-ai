from reportlab.graphics.shapes import Drawing, Group, Circle, Rect, Polygon, Line, PolyLine, String
from reportlab.lib import colors
from reportlab.lib.units import mm
import math

def _create_drawing(width, height):
    return Drawing(width, height)

def draw_shape(shape_type, size=15*mm, color=colors.black, fill_color=colors.white):
    """Draws a basic shape."""
    d = _create_drawing(size, size)
    g = Group()
    
    if shape_type == "circle":
        g.add(Circle(size/2, size/2, size/2 - 1, strokeColor=color, fillColor=fill_color, strokeWidth=1.5))
    elif shape_type == "square":
        g.add(Rect(1, 1, size-2, size-2, strokeColor=color, fillColor=fill_color, strokeWidth=1.5))
    elif shape_type == "triangle":
        g.add(Polygon([size/2, size-1, 1, 1, size-1, 1], strokeColor=color, fillColor=fill_color, strokeWidth=1.5))
    else:
        # fallback
        g.add(Rect(1, 1, size-2, size-2, strokeColor=colors.red, fillColor=colors.transparent, strokeWidth=1))
        
    d.add(g)
    return d

def draw_checkbox(size=10*mm, color=colors.black, checked=False):
    d = _create_drawing(size, size)
    g = Group()
    g.add(Rect(0, 0, size, size, strokeColor=color, fillColor=colors.white, strokeWidth=1.5))
    if checked:
        # draw a checkmark
        g.add(PolyLine([size*0.2, size*0.5, size*0.4, size*0.2, size*0.8, size*0.8], 
                       strokeColor=color, strokeWidth=2))
    d.add(g)
    return d

def draw_star(size=15*mm, color=colors.gold):
    d = _create_drawing(size, size)
    g = Group()
    
    # Calculate 5-point star
    cx, cy = size/2, size/2
    r_outer = size/2 - 1
    r_inner = r_outer * 0.4
    points = []
    for i in range(10):
        angle = i * (math.pi / 5) - (math.pi / 2)
        r = r_outer if i % 2 == 0 else r_inner
        points.extend([cx + r * math.cos(angle), cy - r * math.sin(angle)])
        
    g.add(Polygon(points, strokeColor=colors.darkorange, fillColor=color, strokeWidth=1))
    d.add(g)
    return d

def draw_answer_line(width=40*mm, color=colors.black):
    d = _create_drawing(width, 10*mm)
    g = Group()
    g.add(Line(0, 2*mm, width, 2*mm, strokeColor=color, strokeWidth=1))
    d.add(g)
    return d

def draw_thematic_icon(icon_type, count=1, size=15*mm, color=colors.black):
    """Draws a row of thematic icons."""
    gap = 3 * mm
    width = (size + gap) * count
    d = _create_drawing(width, size)
    
    for i in range(count):
        x_offset = i * (size + gap)
        g = Group()
        g.translate(x_offset, 0)
        
        # Simple vector definitions
        if icon_type == "egg":
            g.add(Circle(size/2, size/2, size/3, strokeColor=color, fillColor=colors.whitesmoke, strokeWidth=1.5))
            g.add(Circle(size/2, size/2 + size/6, size/8, strokeColor=colors.transparent, fillColor=colors.white)) # highlight
        
        elif icon_type == "footprint":
            # Main pad
            g.add(Circle(size/2, size*0.3, size*0.25, strokeColor=color, fillColor=color))
            # Toes
            g.add(Circle(size*0.3, size*0.7, size*0.1, strokeColor=color, fillColor=color))
            g.add(Circle(size*0.5, size*0.8, size*0.1, strokeColor=color, fillColor=color))
            g.add(Circle(size*0.7, size*0.7, size*0.1, strokeColor=color, fillColor=color))
            
        elif icon_type == "bone":
            g.add(Rect(size*0.3, size*0.4, size*0.4, size*0.2, strokeColor=color, fillColor=colors.white, strokeWidth=1))
            g.add(Circle(size*0.25, size*0.4, size*0.15, strokeColor=color, fillColor=colors.white, strokeWidth=1))
            g.add(Circle(size*0.25, size*0.6, size*0.15, strokeColor=color, fillColor=colors.white, strokeWidth=1))
            g.add(Circle(size*0.75, size*0.4, size*0.15, strokeColor=color, fillColor=colors.white, strokeWidth=1))
            g.add(Circle(size*0.75, size*0.6, size*0.15, strokeColor=color, fillColor=colors.white, strokeWidth=1))

        elif icon_type == "planet":
            g.add(Circle(size/2, size/2, size*0.35, strokeColor=color, fillColor=colors.white, strokeWidth=1.5))
            # Ring
            g.add(Line(size*0.1, size*0.3, size*0.9, size*0.7, strokeColor=color, strokeWidth=2))
            
        elif icon_type == "rocket_simple":
            g.add(Polygon([size*0.3, size*0.2, size*0.5, size*0.9, size*0.7, size*0.2], strokeColor=color, fillColor=colors.white, strokeWidth=1.5))
            g.add(Circle(size*0.5, size*0.5, size*0.1, strokeColor=color, fillColor=colors.white, strokeWidth=1))
            g.add(Line(size*0.4, size*0.2, size*0.4, 0, strokeColor=colors.red, strokeWidth=1.5))
            g.add(Line(size*0.6, size*0.2, size*0.6, 0, strokeColor=colors.red, strokeWidth=1.5))

        elif icon_type == "fish":
            g.add(Polygon([size*0.2, size*0.5, size*0.8, size*0.8, size*0.8, size*0.2], strokeColor=color, fillColor=colors.white, strokeWidth=1.5))
            g.add(Circle(size*0.35, size*0.6, size*0.05, strokeColor=color, fillColor=color))
            # tail
            g.add(Polygon([size*0.8, size*0.2, size*0.95, size*0.5, size*0.8, size*0.8], strokeColor=color, fillColor=colors.white, strokeWidth=1.5))

        elif icon_type == "dino":
            # Simple dinosaur body
            g.add(Polygon([size*0.3, size*0.2, size*0.7, size*0.2, size*0.8, size*0.4, size*0.7, size*0.6, size*0.3, size*0.6], strokeColor=color, fillColor=colors.white, strokeWidth=1.5))
            # Head
            g.add(Circle(size*0.75, size*0.25, size*0.1, strokeColor=color, fillColor=colors.white, strokeWidth=1.5))
            # Eye
            g.add(Circle(size*0.77, size*0.25, size*0.03, strokeColor=color, fillColor=color))
            # Legs
            g.add(Line(size*0.35, size*0.2, size*0.35, 0, strokeColor=color, strokeWidth=2))
            g.add(Line(size*0.6, size*0.2, size*0.6, 0, strokeColor=color, strokeWidth=2))
            # Spikes on back
            g.add(Polygon([size*0.4, size*0.55, size*0.45, size*0.7, size*0.5, size*0.55], strokeColor=color, fillColor=colors.white, strokeWidth=1))
            g.add(Polygon([size*0.5, size*0.55, size*0.55, size*0.7, size*0.6, size*0.55], strokeColor=color, fillColor=colors.white, strokeWidth=1))

        elif icon_type == "rocket":
            # Body
            g.add(Polygon([size*0.3, size*0.3, size*0.5, size*0.9, size*0.7, size*0.3], strokeColor=color, fillColor=colors.white, strokeWidth=1.5))
            # Window
            g.add(Circle(size*0.5, size*0.5, size*0.1, strokeColor=color, fillColor=colors.white, strokeWidth=1.5))
            # Wings
            g.add(Polygon([size*0.3, size*0.5, size*0.15, size*0.65, size*0.3, size*0.6], strokeColor=color, fillColor=colors.white, strokeWidth=1))
            g.add(Polygon([size*0.7, size*0.5, size*0.85, size*0.65, size*0.7, size*0.6], strokeColor=color, fillColor=colors.white, strokeWidth=1))
            # Flames
            g.add(Line(size*0.4, size*0.1, size*0.4, 0, strokeColor=colors.orange, strokeWidth=2))
            g.add(Line(size*0.5, size*0.1, size*0.5, 0, strokeColor=colors.orange, strokeWidth=2))
            g.add(Line(size*0.6, size*0.1, size*0.6, 0, strokeColor=colors.orange, strokeWidth=2))

        elif icon_type == "cat":
            # Face
            g.add(Circle(size/2, size*0.4, size*0.3, strokeColor=color, fillColor=colors.white, strokeWidth=1.5))
            # Ears
            g.add(Polygon([size*0.2, size*0.5, size*0.25, size*0.8, size*0.35, size*0.55], strokeColor=color, fillColor=colors.white, strokeWidth=1.5))
            g.add(Polygon([size*0.8, size*0.5, size*0.75, size*0.8, size*0.65, size*0.55], strokeColor=color, fillColor=colors.white, strokeWidth=1.5))
            # Eyes
            g.add(Circle(size*0.4, size*0.4, size*0.05, strokeColor=color, fillColor=color))
            g.add(Circle(size*0.6, size*0.4, size*0.05, strokeColor=color, fillColor=color))
            # Nose
            g.add(Polygon([size*0.48, size*0.45, size*0.52, size*0.45, size*0.5, size*0.5], strokeColor=color, fillColor=colors.pink))
            # Whiskers
            for dx in [0.15, 0.25, 0.35]:
                g.add(Line(size*(0.5-dx), size*0.45, size*(0.5-dx-0.1), size*(0.45+0.05*dx/0.15), strokeColor=color, strokeWidth=0.8))
                g.add(Line(size*(0.5+dx), size*0.45, size*(0.5+dx+0.1), size*(0.45+0.05*dx/0.15), strokeColor=color, strokeWidth=0.8))

        elif icon_type == "math_plus":
            g.add(Line(size*0.2, size*0.5, size*0.8, size*0.5, strokeColor=color, strokeWidth=3))
            g.add(Line(size*0.5, size*0.2, size*0.5, size*0.8, strokeColor=color, strokeWidth=3))

        elif icon_type == "math_minus":
            g.add(Line(size*0.2, size*0.5, size*0.8, size*0.5, strokeColor=color, strokeWidth=3))

        elif icon_type == "math_equal":
            g.add(Line(size*0.2, size*0.4, size*0.8, size*0.4, strokeColor=color, strokeWidth=2))
            g.add(Line(size*0.2, size*0.6, size*0.8, size*0.6, strokeColor=color, strokeWidth=2))

        elif icon_type == "number":
            # Draw a simple number block
            g.add(Rect(size*0.2, size*0.2, size*0.6, size*0.6, strokeColor=color, fillColor=colors.white, strokeWidth=1.5))

        elif icon_type == "bubble":
            g.add(Circle(size/2, size/2, size*0.4, strokeColor=color, fillColor=colors.aliceblue, strokeWidth=1))
            g.add(Circle(size*0.65, size*0.65, size*0.1, strokeColor=colors.white, fillColor=colors.white))
            
        elif icon_type == "cat_simple":
            # Face
            g.add(Circle(size/2, size*0.4, size*0.3, strokeColor=color, fillColor=colors.white, strokeWidth=1.5))
            # Ears
            g.add(Polygon([size*0.2, size*0.5, size*0.3, size*0.9, size*0.4, size*0.6], strokeColor=color, fillColor=colors.white, strokeWidth=1.5))
            g.add(Polygon([size*0.8, size*0.5, size*0.7, size*0.9, size*0.6, size*0.6], strokeColor=color, fillColor=colors.white, strokeWidth=1.5))
            
        elif icon_type == "rabbit_simple":
            # Face
            g.add(Circle(size/2, size*0.3, size*0.25, strokeColor=color, fillColor=colors.white, strokeWidth=1.5))
            # Long Ears
            g.add(Polygon([size*0.3, size*0.5, size*0.3, size*0.95, size*0.45, size*0.5], strokeColor=color, fillColor=colors.white, strokeWidth=1.5))
            g.add(Polygon([size*0.7, size*0.5, size*0.7, size*0.95, size*0.55, size*0.5], strokeColor=color, fillColor=colors.white, strokeWidth=1.5))

        elif icon_type == "fox_simple":
            # Triangular face
            g.add(Polygon([size*0.2, size*0.8, size*0.5, size*0.2, size*0.8, size*0.8], strokeColor=color, fillColor=colors.white, strokeWidth=1.5))
            # Nose
            g.add(Circle(size*0.5, size*0.2, size*0.05, strokeColor=color, fillColor=color))
            
        elif icon_type == "hedgehog_simple":
            # Body half circle
            g.add(Polygon([size*0.2, size*0.3, size*0.5, size*0.7, size*0.8, size*0.3], strokeColor=color, fillColor=colors.white, strokeWidth=1.5))
            # Spikes
            g.add(Line(size*0.3, size*0.5, size*0.2, size*0.7, strokeColor=color, strokeWidth=1))
            g.add(Line(size*0.4, size*0.6, size*0.3, size*0.8, strokeColor=color, strokeWidth=1))
            g.add(Line(size*0.5, size*0.7, size*0.5, size*0.9, strokeColor=color, strokeWidth=1))
            g.add(Line(size*0.6, size*0.6, size*0.7, size*0.8, strokeColor=color, strokeWidth=1))
            g.add(Line(size*0.7, size*0.5, size*0.8, size*0.7, strokeColor=color, strokeWidth=1))

        elif icon_type == "book":
            g.add(Rect(size*0.2, size*0.2, size*0.3, size*0.6, strokeColor=color, fillColor=colors.white, strokeWidth=1.5))
            g.add(Rect(size*0.5, size*0.2, size*0.3, size*0.6, strokeColor=color, fillColor=colors.white, strokeWidth=1.5))
            g.add(Line(size*0.3, size*0.6, size*0.4, size*0.6, strokeColor=color, strokeWidth=1))
            g.add(Line(size*0.6, size*0.6, size*0.7, size*0.6, strokeColor=color, strokeWidth=1))

        elif icon_type == "castle_simple":
            g.add(Rect(size*0.2, size*0.1, size*0.6, size*0.4, strokeColor=color, fillColor=colors.white, strokeWidth=1.5))
            # Towers
            g.add(Rect(size*0.1, size*0.1, size*0.2, size*0.7, strokeColor=color, fillColor=colors.white, strokeWidth=1.5))
            g.add(Rect(size*0.7, size*0.1, size*0.2, size*0.7, strokeColor=color, fillColor=colors.white, strokeWidth=1.5))
            # Door
            g.add(Rect(size*0.4, size*0.1, size*0.2, size*0.2, strokeColor=color, fillColor=colors.white, strokeWidth=1))
            
        else:
            # Fallback to circle
            g.add(Circle(size/2, size/2, size*0.4, strokeColor=colors.red, fillColor=colors.transparent, strokeWidth=1.5))
            
        d.add(g)
        
    return d
