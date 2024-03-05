# This file is to convert a circuit into a .asc (ASCII) file
# to run in ltspice
#

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

def match_points(line, matched_lines, coord1, coord2, count, mode):
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

def identify_component(results, horizontal, vertical):
    if results is None:
        raise Exception ("Error. No components found.")

    components_h = {}
    components_v = {}
    line_fixes = {}
    for r in results:
        for count, x in enumerate(r.boxes.xyxy):
            match_line_to_component(x, horizontal, components_h, count, 0)
            match_line_to_component(x, vertical, components_v, count, 1)

        for count, x in enumerate(r.boxes.cls):
            if count in components_h:
                components_h.setdefault(count, []).extend([int(x.item())])
            elif count in components_v:
                components_v.setdefault(count, []).extend([int(x.item())])

        for count, x in enumerate(r.boxes.xyxy):
            adjust_line_length(components_h, line_fixes, count, 0)
            adjust_line_length(components_v, line_fixes, count, 1)
    return components_h, components_v, horizontal, vertical, line_fixes

def get_comp_name(id):
    if id == 5:
        return "FLAG"
    elif id == 7:
        return "voltage"
    elif id == 8:
        return "Misc\\signal"
    elif id == 9:
        return "Misc\\battery"
    elif id == 10:
        return "res"
    elif id == 11:
        return "SpecialFunctions\\varistor"
    elif id == 13:
        return "cap"
    elif id == 14:
        return "polcap"
    elif id == 15:
        return "ind"
    elif id == 17:
        return "diode"
    elif id == 18:
        return "LED"
    elif id == 19:
        return "TVSdiode"
    elif id == 20:
        return "zener"
    elif id == 21:
        return "Misc\\DIAC"
    elif id == 22:
        return "Misc\\TRIAC"
    elif id == 23:
        return "Misc\\SCR"
    # Add something to determine NMOS PMOS?
    elif id == 25:
        return "nmos4"
    elif id == 32:
        return "Misc\\NE555"
    else:
        print("DNE")
        #raise Exception("Component name not found.")


def generate_schematic(height, width, c_h, c_v, fixes):
    f = open("schematic_test.asc", "w")
    f.write("Version 4\n")
    f.write(f'SHEET 1 {height} {width}\n')


    # For component direction, check lines
    for v in c_v.values():

        if get_comp_name(v[-1]) == "FLAG":
            f.write(f'WIRE {v[0][0]} {v[0][1]} {v[0][2]} {v[0][3]}\n')
        else:
            f.write(f'WIRE {v[0][0]} {v[0][1]} {v[0][2]} {v[0][3]}\n')
            f.write(f'WIRE {v[3][0]} {v[3][1]} {v[3][2]} {v[3][3]}\n')
    
    
    for v in c_h.values():

        if get_comp_name(v[-1]) == "FLAG":
            f.write(f'WIRE {v[0][0]} {v[0][1]} {v[0][2]} {v[0][3]}\n')
        else:
            f.write(f'WIRE {v[0][0]} {v[0][1]} {v[0][2]} {v[0][3]}\n')
            f.write(f'WIRE {v[3][0]} {v[3][1]} {v[3][2]} {v[3][3]}\n')
    
    for v in fixes.values():
        f.write(f'WIRE {v[0]} {v[1]} {v[2]} {v[3]}\n')

    f.close()



# Unit testing
if  __name__==  "__main__":
    generate_schematic()