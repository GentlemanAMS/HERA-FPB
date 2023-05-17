print("\nVersion Update: \n")




gpio_pin_write_addr = 0x89f8                     #GPIOPinWrite()

call_function_1_addr = 0x84c0
call_function_2_addr = 0x84d0
call_function_3_addr = 0x84e0






import json

try:
    with open("patch_maintainer.json", "r") as fp:
        updates_info = json.load(fp)

except:

    with open("patch_maintainer.json", "x") as fp:
        function1 = {
            "version_number" : 0,
            "old_version"    : "blue",
            "current_version": "blue"
        }
        function2 = {
            "version_number" : 0,
            "old_version"    : "blue",
            "current_version": "blue"
        }
        function3 = {
            "version_number" : 0,
            "old_version"    : "blue",
            "current_version": "blue"
        }
        functions = {
                "function_1" : function1, 
                "function_2" : function2, 
                "function_3" : function3,
                "patch_address" : 0x24000}
        json.dump(functions, fp, indent=4)

    with open("patch_maintainer.json", "r") as fp:    
        updates_info = json.load(fp)







print("Choose current function to update: 1, 2 or 3")
choice_func_to_update = input()
print("\n")

if choice_func_to_update == '1':
    if updates_info["function_1"]["version_number"] != 0:
        print("Function already updated")
        exit(0)
    function_to_be_updated = "function_1"


elif choice_func_to_update == '2':
    if updates_info["function_2"]["version_number"] != 0:
        print("Function 2 already updated")
        exit(0)
    function_to_be_updated = "function_2"

elif choice_func_to_update == '3':
    if updates_info["function_3"]["version_number"] != 0:
        print("Function 3 already updated")
        exit(0)
    function_to_be_updated = "function_3"


print("Enter which patch to be generated:")
print("1: green")
print("2: red")
print("3: blue")
print("4: switch off")

choice_new_func = input()

print("\n")
print("function version number   : ",updates_info[function_to_be_updated]["version_number"])
print("function older version    : ",updates_info[function_to_be_updated]["old_version"])

if choice_new_func == '1':
    new_updated_function = "green"
elif choice_new_func == '2':
    new_updated_function = "red"
elif choice_new_func == '3':
    new_updated_function = "blue"
elif choice_new_func == '4':
    new_updated_function = "switched_off"

print("function requested version: ",new_updated_function)




print("\n\nPatch Generation Starts\n")

from patch_generator import *
instr_addr          = updates_info["patch_address"]                        #Instruction where it starts

if choice_new_func == '1':
    patch = green_patch_generation(gpio_pin_write_addr, instr_addr)
elif choice_new_func == '2':
    patch = red_patch_generation(gpio_pin_write_addr, instr_addr)
elif choice_new_func == '3':
    patch = blue_patch_generation(gpio_pin_write_addr, instr_addr)
elif choice_new_func == '4':
    patch = off_patch_generation(gpio_pin_write_addr, instr_addr)



b1 = instr_addr & 0xFF
b2 = (instr_addr & 0xFF00) >> 8
b3 = (instr_addr & 0xFF0000) >> 16
b4 = (instr_addr & 0xFF000000) >> 24
new_instruction_address = bytearray([b4, b3, b2, b1])



if choice_func_to_update == '1':
    call_function_addr = call_function_1_addr
elif choice_func_to_update == '2':
    call_function_addr = call_function_2_addr
elif choice_func_to_update == '3':
    call_function_addr = call_function_3_addr

b1 = call_function_addr & 0xFF
b2 = (call_function_addr & 0xFF00) >> 8
b3 = (call_function_addr & 0xFF0000) >> 16
b4 = (call_function_addr & 0xFF000000) >> 24
old_instruction_address = bytearray([b4, b3, b2, b1])



link = bytearray(b'\x01')


import serial
import time
ser = serial.Serial("/dev/ttyACM0", 115200)

print("\n\nVersion Update starts:\n\n")

time.sleep(0.5)
ser.write(bytearray(b'\x55'))

time.sleep(0.1)
ser.write(old_instruction_address)

time.sleep(0.1)
ser.write(new_instruction_address)

time.sleep(0.1)
ser.write(link)

while(True):
    x = ser.read(1)
    if (x == b'\x44'):
        break

print("Sent Instruction Address")

ser.write(bytearray([len(patch)]))

while(True):
    x = ser.read(1)
    if (x == b'\x44'):
        break

print("Sent patch size", len(patch), "\n")

for i in range(len(patch)):
    ser.write(bytearray([patch[i]]))
    time.sleep(0.02)
    
    if (i % 4 == 3):
        while(True):
            x = ser.read(1)
            if (x == b'\x43'):
                break        
        print("Block: ", i>>2 , " uploaded")

print("Patch Update Completed")





updates_info[function_to_be_updated]["version_number"] = 1
updates_info[function_to_be_updated]["old_version"] = "blue"
updates_info[function_to_be_updated]["current_version"] = new_updated_function
updates_info["patch_address"] = updates_info["patch_address"] + 0xFFF 

with open("patch_maintainer.json", "w") as fp:
    json.dump(updates_info, fp, indent=4)

print("Patch Maintainer Updated")




