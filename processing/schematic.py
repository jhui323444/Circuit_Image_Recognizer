

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


def match_points(line, matched_lines, coord1, coord2, count, mode):

    if abs(line[mode] - coord1) <= 20:
        matched_lines.setdefault(count, []).extend([line, line[mode], mode])

    if abs(line[mode] - coord2) <= 20:
        matched_lines.setdefault(count, []).extend([line, line[mode], mode])

    if abs(line[mode + 2] - coord1) <= 20:
        matched_lines.setdefault(count, []).extend([line, \
                                                    line[mode + 2], mode + 2])

    if abs(line[mode + 2] - coord2) <= 20:
        matched_lines.setdefault(count, []).extend([line, \
                                                    line[mode + 2], mode + 2])



def adjust_line_length(components, line_fixes, count, mode):

    if count in components:
        cur_comp = components[count]
        if len(cur_comp) > 4:
            dif = cur_comp[1] - cur_comp[4]
            first = cur_comp[2]
            fix = 80
            

            # Capacitors have length of 64 units
            if cur_comp[-1] == 13 or cur_comp[-1] == 14 or \
               cur_comp[-1] == 17 or cur_comp[-1] == 18 or \
               cur_comp[-1] == 18 or cur_comp[-1] == 19 or \
               cur_comp[-1] == 20 or cur_comp[-1] == 9 or \
               cur_comp[-1] == 21 or cur_comp[-1] == 22 or \
               cur_comp[-1] == 23: 

                fix = 64

            if cur_comp[-1] == 26:
                fix = 96

            cur_comp[0][first] = cur_comp[4] + fix \
                            if dif > 0 else cur_comp[4] - fix
            cur_comp[1] = cur_comp[0][first]

            
            # add to new dict with fixing lines        
            if mode == 0 and cur_comp[0][1] != cur_comp[3][1]:
                y1, y2 = cur_comp[0][1], cur_comp[3][1]
                x = cur_comp[1]
                line_fixes[count] = [x, y1, x, y2]

            if mode == 1 and cur_comp[0][0] != cur_comp[3][0]:
                x1, x2 = cur_comp[0][0], cur_comp[3][0]
                y = cur_comp[1]
                line_fixes[count] = [x1, y, x2, y]

def identify_component(results, horizontal, vertical):
    if results is None:
        raise Exception ("Error. No components found.")
    
    components_h = {}
    components_v = {}
    matched = []
    other = []
    line_fixes = {}
    for r in results:
        for count, x in enumerate(r.boxes.xyxy):
            match_line_to_component(x, horizontal, components_h, count, 0)
            match_line_to_component(x, vertical, components_v, count, 1)
        print(components_h)
        print(components_v)
        for key in list(components_h.keys()):
            if key in components_v and \
                len(components_h[key]) < len(components_v[key]):

                components_v.setdefault(key, []).extend(components_h.get(key))
                del components_h[key]
            elif key in components_v:
                components_h.setdefault(key, []).extend(components_v.get(key))
                del components_v[key]
        
        for count, x in enumerate(r.boxes.cls):
            if count in components_h:
                components_h.setdefault(count, []).extend([int(x.item())])
            if count in components_v:
                components_v.setdefault(count, []).extend([int(x.item())])

        
        # print(components_h)
        # print(components_v)
        # Find all matched wires
        for value in components_h.values():
            index = 0
            while index < len(value):
                matched.append(value[index])
                index += 3
        for value in components_v.values():
            index = 0
            while index < len(value):
                matched.append(value[index])
                index += 3
        
        # Find wires not connected to components
        for line in horizontal.values():
            if line in matched:
                continue
            other.append(line)
        for line in vertical.values():
            if line in matched:
                continue
            other.append(line)
        for count, x in enumerate(r.boxes.xyxy):
            adjust_line_length(components_h, line_fixes, count, 0)
            adjust_line_length(components_v, line_fixes, count, 1)
    return components_h, components_v, horizontal, vertical, \
        other, line_fixes

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
    elif id == 26:
        return "nmos4"
    elif id == 32:
        return "Misc\\NE555"
    else:
        return "Component Not Found"
        #raise Exception("Component name not found.")

def get_inst_name(id, cnt):
    inst_name = {7: "V",
                 8: "V",
                 9: "V",
                 10: "R",
                 11: "A",
                 13: "C",
                 14: "C",
                 15: "L",
                 17: "D",
                 18: "D",
                 19: "D",
                 20: "D",
                 21: "U",
                 22: "U",
                 23: "U",
                 26: "M",
                 32: "U"}
    
    name = inst_name.get(id, "X")
    cnt[ord(name) - 65] += 1
    return name, cnt[ord(name) - 65]  



def generate_schematic(height, width, c_h, c_v, other, fixes, results):
    f = open("schematic.asc", "w")
    f.write("Version 4\n")
    f.write(f'SHEET 1 {height} {width}\n')
    
    component_check = []
    # Need to write in wires first
    for v in c_v.values():
        name =  get_comp_name(v[-1])
        # if get_comp_name(v[-1]) == "FLAG":
        #     f.write(f'WIRE {v[0][0]} {v[0][1]} {v[0][2]} {v[0][3]}\n')
        if get_comp_name(v[-1]) == "transistor.fet":
            f.write(f'WIRE {v[7][0]} {v[5][1]} {v[5][2]} {v[5][3]}\n')
            f.write(f'WIRE {v[3][0]} {v[3][1]} {v[3][2]} {v[3][3]}\n')

        elif len(v) > 4:
            f.write(f'WIRE {v[3][0]} {v[3][1]} {v[3][2]} {v[3][3]}\n')
        f.write(f'WIRE {v[0][0]} {v[0][1]} {v[0][2]} {v[0][3]}\n')
    
    for v in c_h.values():
        print(v[-1])
        name = get_comp_name(v[-1])
        if name == "transistor.fet":
            f.write(f'WIRE {v[3][0]} {v[3][1]} {v[3][2]} {v[3][3]}\n')
            f.write(f'WIRE {v[7][0]} {v[7][1]} {v[7][2]} {v[7][3]}\n')

        elif len(v) > 4:
            f.write(f'WIRE {v[3][0]} {v[3][1]} {v[3][2]} {v[3][3]}\n')
    
        f.write(f'WIRE {v[0][0]} {v[0][1]} {v[0][2]} {v[0][3]}\n')
    

    for v in other:
        f.write(f'WIRE {v[0]} {v[1]} {v[2]} {v[3]}\n')

    for v in fixes.values():
        f.write(f'WIRE {v[0]} {v[1]} {v[2]} {v[3]}\n')


    # Then write all grounds in circuit
    for v in c_v.values():
        if get_comp_name(v[-1]) == "FLAG":
            f.write(f'FLAG {v[0][0]} {v[1]} 0\n')
    for v in c_h.values():
        if get_comp_name(v[-1]) == "FLAG":
            f.write(f'FLAG {v[1]} {v[0][1]} 0\n')


    # Finally, write all components
    instance_cnt = 26*[0]
    not_found = [0]
    for key, v in c_v.items():
        comp = get_comp_name(v[-1])

        if comp == "FLAG": continue
        if comp == "Component Not Found": 
            not_found[0] += 1
            continue
        x = v[0][0]
        #y = -1
        name, cnt = get_inst_name(v[-1], instance_cnt)
        fix_coords = fixes.get(key)

        if fix_coords is not None:
            if fix_coords[1] == v[1] or fix_coords[1] == v[4]:
                y = fix_coords[2]
            else:
                y = fix_coords[0]
        # Check for smaller y value to start component
                
        if len(v) < 5:
            y = v[1]
        elif v[1] < v[4]:
            y = v[1]
        else:
            y = v[4]

        if name == "V": 
            x += 16
            component_check.append(name + str(cnt))
        elif name == "C" or name == "D": 
            y += 16
            component_check.append(name + str(cnt))
        elif comp == "nmos4":
            x -= 32
            y += 16
            component_check.append(name + str(cnt))
            
        f.write(f'SYMBOL {comp} {x - 16} {y - 16} R0\n')
        f.write(f'SYMATTR InstName {name}{cnt}\n')
        
    for key, v in c_h.items():
        comp = get_comp_name(v[-1])

        if comp == "FLAG": continue
        if comp == "Component Not Found": continue
        y = v[0][1]
        #x = -1
        name, cnt = get_inst_name(v[-1], instance_cnt)
        fix_coords = fixes.get(key)

        if fix_coords is not None:
            if fix_coords[0] == v[1] or fix_coords[0] == v[4]:
                y = fix_coords[3]
            else:
                y = fix_coords[1]
        
        if len(v) < 5:
            x = v[1]
        elif v[1] < v[4]:
            x = v[4] 
        else:
            x = v[1]    
            
        if name == "C" or name == "D":
            x -= 16
            component_check.append(name + str(cnt))
        elif name == "V":
            y += 16
            component_check.append(name + str(cnt))
        elif comp == "nmos4":
            y -= 32
            x -= 16
            component_check.append(name + str(cnt))

        f.write(f'SYMBOL {comp} {x + 16} {y - 16} R90\n')

        f.write(f'WINDOW 0 0 32 VBottom 2\n')
        f.write(f'WINDOW 3 32 32 VTop 2\n')
        
        f.write(f'SYMATTR InstName {name}{cnt}\n')
    
    unmatched = {}
    for r in results:
        for count, box in enumerate(r.boxes.xyxy):
            if count in c_h or count in c_v:
                continue
        
            x1, y1 = round(box[0].item()), round(box[1].item())

        
            x1 = int(x1) - (int(x1) % 4)
            y1 = int(y1) - (int(y1) % 4)


            unmatched[count] = [x1, y1]

        for count, cls in enumerate(r.boxes.cls):
            comp = get_comp_name(int(cls.item()))
            if count in unmatched and comp != "Component Not Found":
                name, name_cnt = get_inst_name(int(cls.item()), instance_cnt)
                coords = unmatched.get(count)
                
                f.write(f'SYMBOL {comp} {coords[0] - 16} {coords[1] - 16} R0\n')
                f.write(f'SYMATTR InstName {name}{name_cnt}\n')

    print(unmatched)
    
        
        

    print("Verify direction of these components: ")
    print(component_check)
    print(f'{not_found[0]} unidentified components in LTSpice. Please verify.')
    f.close()


# Unit testing
if  __name__==  "__main__":
    generate_schematic()
