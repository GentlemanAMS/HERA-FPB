import serial
import time
ser = serial.Serial("/dev/ttyACM0", 115200)


green_function_start_address = bytearray(b'\x00\x00\x82\xd0')
blue_function_start_address  = bytearray(b'\x00\x00\x82\xd4')
red_function_start_address   = bytearray(b'\x00\x00\x82\x78') 
off_function_start_address   = bytearray(b'\x00\x00\x82\xfc')

call_function_1 = bytearray(b'\x00\x00\x83\xf8')
call_function_2 = bytearray(b'\x00\x00\x84\x08')
call_function_3 = bytearray(b'\x00\x00\x84\x18')

old_instruction_address = bytearray(b'\x00\x00\x83\xf8')
new_instruction_address = bytearray(b'\x00\x00\x82\xd0')
link = bytearray(b'\x01')
start = bytearray(b'\x55')

print("Version Update: \n")
print("Choose current function to update: ")
print("function 1: blue")
print("function 2: red")
print("function 3: switch off\n")
print("Replace which function: function 1 or 2 or 3")
func = input()

if func == '1':
    old_instruction_address = call_function_1
elif func == '2':
    old_instruction_address = call_function_2
elif func == '3':
    old_instruction_address = call_function_3

print("\n\nChoose which function:")
print("1: green")
print("2: blue")
print("3: red")
print("4: switch off")
func = input()

if func == '1':
    new_instruction_address = green_function_start_address
elif func == '2':
    new_instruction_address = blue_function_start_address
elif func == '3':
    new_instruction_address = red_function_start_address
elif func == '4':
    new_instruction_address = off_function_start_address



print("\nVersion Update starts:\n")

time.sleep(0.5)
ser.write(start)
time.sleep(0.1)
ser.write(old_instruction_address)
time.sleep(0.1)
ser.write(new_instruction_address)
time.sleep(0.1)
ser.write(link)
time.sleep(0.5)

print("Version Update completed\n")
