# This file is to convert a circuit into a .asc (ASCII) file
# to run in ltspice
#

# TO Do
# Check component box
#   - Identify component
#       - Need to have some sort of list with correct string
#         name for components in LTSpice
#   - Check closest line endpoints
#   - Take one line endpoint, adjust to correct ltspice size
#   - Write component coords into new dictionary/array?
#      - Some sort of storage
#
# Generate schematic
#   - Write header into schematic file, add dimensions of circuit
#   - Write wires into ASCII file
#   - Write components into file

from ultralytics import YOLO

# Input is dictionary of horizontal or vertical lines

# matched_lines needs: x1,y1,x2,y2 of found line(s) and what component
# closest to bounding box
def match_line_to_component(coords, lines, matched_lines, count, mode):
    x1, y1, x2, y2 = round(coords[0].item()), round(coords[1].item()), \
                     round(coords[2].item()), round(coords[3].item())
    
    for line in lines.values():
        # horizontal lines (same y, different x)
        if mode == 0:
            # if y coord within range of bounding box and
            # if either x coordinate close enough to bounding box
            if line[1] <= y2 and line[1] >= y1:
                match_points(line, matched_lines, x1, \
                             x2, count, 0)
        if mode == 1:
            if line[0] <= x2 and line[0] >= x1:
                match_points(line, matched_lines, y1, \
                             y2, count, 1)

## mode = 0, 

def match_points(line, matched_lines,coord1, coord2, count, mode):
    if abs(line[mode] - coord1) <= 30:
        matched_lines.setdefault(count, []).extend([line, line[mode], mode])
    elif abs(line[mode] - coord2) <= 30:
        matched_lines.setdefault(count, []).extend([line, line[mode], mode])

    elif abs(line[mode + 2] - coord1) <= 30:
        matched_lines.setdefault(count, []).extend([line, \
                                                    line[mode + 2], mode + 2])
    elif abs(line[mode + 2] - coord2) <= 30:
        matched_lines.setdefault(count, []).extend([line, \
                                                    line[mode + 2], mode + 2])


def identify_component(results, horizontal, vertical):
    components_h = {}
    components_v = {}
    line_fixes = {}
    for r in results:
        for count, x in enumerate(r.boxes.xyxy):
            match_line_to_component(x, horizontal, components_h, count, 0)
            match_line_to_component(x, vertical, components_v, count, 1)

        for count, x in enumerate(r.boxes.cls):
            if count in components_h:
                components_h.setdefault(count, []).extend([x.item()])
            elif count in components_v:
                components_v.setdefault(count, []).extend([x.item()])

        for count, x in enumerate(r.boxes.xyxy):
            adjust_line_length(components_h, line_fixes, count, 0)
            adjust_line_length(components_v, line_fixes, count, 1)
    return components_h, components_v, horizontal, vertical, line_fixes

def adjust_line_length(components, line_fixes, count, mode):

    if count in components:
        if int(components[count][-1]) !=  5:
            dif = components[count][1] - components[count][4]
            first = components[count][2]

            components[count][0][first] = components[count][4] + 80 \
                            if dif > 0 else components[count][4] - 80
            components[count][1] = components[count][0][first]

            
            # add to new dict with fixing lines        
            if mode == 0 and components[count][0][1] != components[count][3][1]:
                y1, y2 = components[count][0][1], components[count][3][1]
                x = components[count][1]
                line_fixes[count] = [x, y1, x, y2]
                 
            if mode == 1 and components[count][0][0] != components[count][3][0]:
                x1, x2 = components[count][0][0], components[count][3][0]
                y = components[count][1]
                line_fixes[count] = [x1, y, x2, y]
def generate_schematic(height, width):
    f = open("schematic_test.asc", "w")
    f.write("Version 4")
    f.write(f'SHEET 1 {height} {width}')
    f.close()



# Unit testing
if  __name__==  "__main__":
    generate_schematic()