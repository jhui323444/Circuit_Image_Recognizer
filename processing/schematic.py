# This file is to convert a circuit into a .asc (ASCII) file
# to run in ltspice
#

def generate_schematic():
    f = open("schematic_test.asc", "w")
    f.write("Version 4")
    f.close()



# Unit testing
if  __name__==  "__main__":
    generate_schematic()