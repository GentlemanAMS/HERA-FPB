gpio_pin_write_addr = 0x0000890c                     #GPIOPinWrite()
instr_addr          = 0x00024000                        #Instruction where it starts

b1 = instr_addr & 0xFF
b2 = (instr_addr & 0xFF00) >> 8
b3 = (instr_addr & 0xFF0000) >> 16
b4 = (instr_addr & 0xFF000000) >> 24
new_instruction_address = bytearray([b4, b3, b2, b1])
print(new_instruction_address)


def calculate_b_instr(target_instr_addr, curr_instr_addr):
    offset = target_instr_addr - curr_instr_addr - 4
    
    offset_msb10 = (offset >> 12) & 0x3FF
    offset_lsb11 = (offset >> 1) & 0x07FF

    s =  ((offset & (1 << 24)) >> 24) & 0x01
    i1 = ((offset & (1 << 23)) >> 23) & 0x01
    i2 = ((offset & (1 << 22)) >> 22) & 0x01

    j1 = 0x01 & ((~i1) ^ s)
    j2 = 0x01 & ((~i2) ^ s)

    b_instr_msb16 = ((0x1E << 11) | (s << 10) | offset_msb10) & 0xFFFF
    b_instr_lsb16 = ((0x02 << 14) | (j1 << 13) | (0x01 << 12) | (j2 << 11) | offset_lsb11) & 0xFFFF

    b_instr = (b_instr_msb16 << 16) | b_instr_lsb16
    b_instr = ((b_instr & 0xFFFF0000) >> 16) | ((b_instr & 0x0000FFFF) << 16)
    
    b1 = b_instr & 0xFF
    b2 = (b_instr & 0xFF00) >> 8
    b3 = (b_instr & 0xFF0000) >> 16
    b4 = (b_instr & 0xFF000000) >> 24

    b_instr = bytearray([b1, b2, b3, b4])

    return b_instr




def calculate_bl_instr(target_instr_addr, curr_instr_addr):
    offset = target_instr_addr - curr_instr_addr - 4
    
    offset_msb10 = (offset >> 12) & 0x3FF
    offset_lsb11 = (offset >> 1) & 0x07FF

    s =  ((offset & (1 << 24)) >> 24) & 0x01
    i1 = ((offset & (1 << 23)) >> 23) & 0x01
    i2 = ((offset & (1 << 22)) >> 22) & 0x01

    j1 = 0x01 & ((~i1) ^ s)
    j2 = 0x01 & ((~i2) ^ s)

    b_instr_msb16 = ((0x1E << 11) | (s << 10) | offset_msb10) & 0xFFFF
    b_instr_lsb16 = ((0x02 << 14) | (j1 << 13) | (0x01 << 12) | (j2 << 11) | offset_lsb11) & 0xFFFF

    b_instr = (b_instr_msb16 << 16) | b_instr_lsb16
    b_instr = b_instr | 0x00004000
    b_instr = ((b_instr & 0xFFFF0000) >> 16) | ((b_instr & 0x0000FFFF) << 16)
    
    b1 = b_instr & 0xFF
    b2 = (b_instr & 0xFF00) >> 8
    b3 = (b_instr & 0xFF0000) >> 16
    b4 = (b_instr & 0xFF000000) >> 24

    b_instr = bytearray([b1, b2, b3, b4])

    return b_instr

    # 000082d0 10 b5           push       {r4,lr}
    # 000082d2 09 4c           ldr        r4,[DAT_000082f8]                                = 40025000h
    # 000082d4 00 22           movs       r2,#0x0
    # 000082d6 20 46           mov        r0,r4
    # 000082d8 02 21           movs       r1,#0x2
    # 000082da 00 f0 81 fa     bl         GPIOPinWrite                                     undefined GPIOPinWrite(int param
    # 000082de 20 46           mov        r0,r4
    # 000082e0 00 22           movs       r2,#0x0
    # 000082e2 04 21           movs       r1,#0x4
    # 000082e4 00 f0 7c fa     bl         GPIOPinWrite                                     undefined GPIOPinWrite(int param
    # 000082e8 08 22           movs       r2,#0x8
    # 000082ea 20 46           mov        r0,r4
    # 000082ec 11 46           mov        r1,r2
    # 000082ee bd e8 10 40     pop.w      {r4,lr}
    # 000082f2 00 f0 75 ba     b.w        GPIOPinWrite                                     undefined GPIOPinWrite(int param
    #                      -- Flow Override: CALL_RETURN (CALL_TERMINATOR)
    # 000082f6 00              align      align(1)
    # 000082f7 bf              ??         BFh
    #                      DAT_000082f8                                    XREF[1]:     turn_green_on:000082d2(R)  
    # 000082f8 00 50 02 40     undefined4 40025000h


print("Patch:")

# 000082d0 10 b5           push       {r4,lr}
patch = bytearray(b'\x10\xb5')
print(bytearray(b'\x10\xb5'))
instr_addr = instr_addr + 2

# 000082d2 09 4c           ldr        r4,[DAT_000082f8]                                = 40025000h
patch = patch + bytearray(b'\x09\x4c')
print(bytearray(b'\x09\x4c'))
instr_addr = instr_addr + 2

# 000082d4 00 22           movs       r2,#0x0
patch = patch + bytearray(b'\x00\x22')
print(bytearray(b'\x00\x22'))
instr_addr = instr_addr + 2

# 000082d6 20 46           mov        r0,r4
patch = patch + bytearray(b'\x20\x46')
print(bytearray(b'\x20\x46'))
instr_addr = instr_addr + 2

# 000082d8 02 21           movs       r1,#0x2
patch = patch + bytearray(b'\x02\x21')
print(bytearray(b'\x02\x21'))
instr_addr = instr_addr + 2

# 000082da 00 f0 81 fa     bl         GPIOPinWrite                                     undefined GPIOPinWrite(int param
patch = patch + calculate_bl_instr(gpio_pin_write_addr, instr_addr)
print(calculate_bl_instr(gpio_pin_write_addr, instr_addr))
instr_addr = instr_addr + 4

# 000082de 20 46           mov        r0,r4
patch = patch + bytearray(b'\x20\x46')
print(bytearray(b'\x20\x46'))
instr_addr = instr_addr + 2

# 000082e0 00 22           movs       r2,#0x0
patch = patch + bytearray(b'\x00\x22')
print(bytearray(b'\x00\x22'))
instr_addr = instr_addr + 2

# 000082e2 04 21           movs       r1,#0x4
patch = patch + bytearray(b'\x04\x21')
print(bytearray(b'\x04\x21'))
instr_addr = instr_addr + 2

# 000082e4 00 f0 7c fa     bl         GPIOPinWrite                                     undefined GPIOPinWrite(int param
patch = patch + calculate_bl_instr(gpio_pin_write_addr, instr_addr)
print(calculate_bl_instr(gpio_pin_write_addr, instr_addr))
instr_addr = instr_addr + 4

# 000082e8 08 22           movs       r2,#0x8
patch = patch + bytearray(b'\x08\x22')
print(bytearray(b'\x08\x22'))
instr_addr = instr_addr + 2

# 000082ea 20 46           mov        r0,r4
patch = patch + bytearray(b'\x20\x46')
print(bytearray(b'\x20\x46'))
instr_addr = instr_addr + 2

# 000082ec 11 46           mov        r1,r2
patch = patch + bytearray(b'\x11\x46')
print(bytearray(b'\x11\x46'))
instr_addr = instr_addr + 2

# 000082ee bd e8 10 40     pop.w      {r4,lr}
patch = patch + bytearray(b'\xbd\xe8\x10\x40')
print(bytearray(b'\xbd\xe8\x10\x40'))
instr_addr = instr_addr + 4

# 000082f2 00 f0 75 ba     b.w        GPIOPinWrite                                     undefined GPIOPinWrite(int param
patch = patch + calculate_b_instr(gpio_pin_write_addr, instr_addr)
print(calculate_b_instr(gpio_pin_write_addr, instr_addr))
instr_addr = instr_addr + 4


#                      -- Flow Override: CALL_RETURN (CALL_TERMINATOR)
# 000082f6 00              align      align(1)
patch = patch + bytearray(b'\x00')
print(bytearray(b'\x00'))
instr_addr = instr_addr + 1

# 000082f7 bf              ??         BFh
patch = patch + bytearray(b'\xbf')
print(bytearray(b'\xbf'))
instr_addr = instr_addr + 1

#                      DAT_000082f8                                    XREF[1]:     turn_green_on:000082d2(R)  
# 000082f8 00 50 02 40     undefined4 40025000h
patch = patch + bytearray(b'\x00\x50\x02\x40')
print(bytearray(b'\x00\x50\x02\x40'))
instr_addr = instr_addr + 4

padding = bytearray([0]*(4 - len(patch)%4))
patch = patch + padding
print(padding)

import serial
import time
ser = serial.Serial("/dev/ttyACM0", 115200)

print("Version Update: \n")
print("Choose current function to update: 1, 2 or 3")
func = input()

call_function_1 = bytearray(b'\x00\x00\x83\xd6')
call_function_2 = bytearray(b'\x00\x00\x83\xe6')
call_function_3 = bytearray(b'\x00\x00\x83\xf6')

if func == '1':
    old_instruction_address = call_function_1
elif func == '2':
    old_instruction_address = call_function_2
elif func == '3':
    old_instruction_address = call_function_3

link = bytearray(b'\x01')

print("\nVersion Update starts:\n")

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

print("Sent patch size", len(patch))

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

