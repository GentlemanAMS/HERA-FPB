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






def green_patch_generation(gpio_pin_write_addr, instr_addr):

        # 10 b5           push       {r4,lr}
        # 09 4c           ldr        r4,[DAT_000082f8]                                = 40025000h
        # 00 22           movs       r2,#0x0
        # 20 46           mov        r0,r4
        # 02 21           movs       r1,#0x2
        # 00 f0 81 fa     bl         GPIOPinWrite                                     undefined GPIOPinWrite(int param
        # 20 46           mov        r0,r4
        # 00 22           movs       r2,#0x0
        # 04 21           movs       r1,#0x4
        # 00 f0 7c fa     bl         GPIOPinWrite                                     undefined GPIOPinWrite(int param
        # 08 22           movs       r2,#0x8
        # 20 46           mov        r0,r4
        # 11 46           mov        r1,r2
        # bd e8 10 40     pop.w      {r4,lr}
        # 00 f0 75 ba     b.w        GPIOPinWrite                                     undefined GPIOPinWrite(int param
        #                      -- Flow Override: CALL_RETURN (CALL_TERMINATOR)
        # 00              align      align(1)
        # bf              ??         BFh
        #                      DAT_000082f8                                    XREF[1]:     turn_green_on:000082d2(R)  
        # 00 50 02 40     undefined4 40025000h


    # 10 b5           push       {r4,lr}
    patch = bytearray(b'\x10\xb5')
    instr_addr = instr_addr + 2

    # 09 4c           ldr        r4,[DAT_000082f8]                                = 40025000h
    patch = patch + bytearray(b'\x09\x4c')
    instr_addr = instr_addr + 2

    # 00 22           movs       r2,#0x0
    patch = patch + bytearray(b'\x00\x22')
    instr_addr = instr_addr + 2

    # 20 46           mov        r0,r4
    patch = patch + bytearray(b'\x20\x46')
    instr_addr = instr_addr + 2

    # 02 21           movs       r1,#0x2
    patch = patch + bytearray(b'\x02\x21')
    instr_addr = instr_addr + 2

    # 00 f0 81 fa     bl         GPIOPinWrite                                     undefined GPIOPinWrite(int param
    patch = patch + calculate_bl_instr(gpio_pin_write_addr, instr_addr)
    instr_addr = instr_addr + 4

    # 20 46           mov        r0,r4
    patch = patch + bytearray(b'\x20\x46')
    instr_addr = instr_addr + 2

    # 00 22           movs       r2,#0x0
    patch = patch + bytearray(b'\x00\x22')
    instr_addr = instr_addr + 2

    # 04 21           movs       r1,#0x4
    patch = patch + bytearray(b'\x04\x21')
    instr_addr = instr_addr + 2

    # 00 f0 7c fa     bl         GPIOPinWrite                                     undefined GPIOPinWrite(int param
    patch = patch + calculate_bl_instr(gpio_pin_write_addr, instr_addr)
    instr_addr = instr_addr + 4

    # 08 22           movs       r2,#0x8
    patch = patch + bytearray(b'\x08\x22')
    instr_addr = instr_addr + 2

    # 20 46           mov        r0,r4
    patch = patch + bytearray(b'\x20\x46')
    instr_addr = instr_addr + 2

    # 11 46           mov        r1,r2
    patch = patch + bytearray(b'\x11\x46')
    instr_addr = instr_addr + 2

    # bd e8 10 40     pop.w      {r4,lr}
    patch = patch + bytearray(b'\xbd\xe8\x10\x40')
    instr_addr = instr_addr + 4

    # 00 f0 75 ba     b.w        GPIOPinWrite                                     undefined GPIOPinWrite(int param
    patch = patch + calculate_b_instr(gpio_pin_write_addr, instr_addr)
    instr_addr = instr_addr + 4

    #                      -- Flow Override: CALL_RETURN (CALL_TERMINATOR)
    # 00              align      align(1)
    patch = patch + bytearray(b'\x00')
    instr_addr = instr_addr + 1

    # bf              ??         BFh
    patch = patch + bytearray(b'\xbf')
    instr_addr = instr_addr + 1

    #                      DAT_000082f8                                    XREF[1]:     turn_green_on:000082d2(R)  
    # 00 50 02 40     undefined4 40025000h
    patch = patch + bytearray(b'\x00\x50\x02\x40')
    instr_addr = instr_addr + 4

    padding = bytearray([0]*(4 - len(patch)%4))
    patch = patch + padding

    return patch









def blue_patch_generation(gpio_pin_write_addr, instr_addr):

        # 10 b5           push       {r4,lr}
        # 09 4c           ldr        r4,[DAT_000082bc]                                = 40025000h
        # 00 22           movs       r2,#0x0
        # 20 46           mov        r0,r4
        # 02 21           movs       r1,#0x2
        # 00 f0 77 fb     bl         GPIOPinWrite                                     undefined GPIOPinWrite(int param
        # 04 22           movs       r2,#0x4
        # 11 46           mov        r1,r2
        # 20 46           mov        r0,r4
        # 00 f0 72 fb     bl         GPIOPinWrite                                     undefined GPIOPinWrite(int param
        # 20 46           mov        r0,r4
        # 00 22           movs       r2,#0x0
        # bd e8 10 40     pop.w      {r4,lr}
        # 08 21           movs       r1,#0x8
        # 00 f0 6b bb     b.w        GPIOPinWrite                                     undefined GPIOPinWrite(int param
        #                      -- Flow Override: CALL_RETURN (CALL_TERMINATOR)
        # 00              align      align(1)
        # bf              ??         BFh
        #                      DAT_000082bc                                    XREF[1]:     turn_blue_on:00008296(R)  
        # 00 50 02 40     undefined4 40025000h



    # 10 b5           push       {r4,lr}
    patch = bytearray(b'\x10\xb5')
    instr_addr = instr_addr + 2

    # 09 4c           ldr        r4,[DAT_000082bc]                                = 40025000h
    patch = patch + bytearray(b'\x09\x4c')
    instr_addr = instr_addr + 2

    # 00 22           movs       r2,#0x0
    patch = patch + bytearray(b'\x00\x22')
    instr_addr = instr_addr + 2

    # 20 46           mov        r0,r4
    patch = patch + bytearray(b'\x20\x46')
    instr_addr = instr_addr + 2

    # 02 21           movs       r1,#0x2
    patch = patch + bytearray(b'\x02\x21')
    instr_addr = instr_addr + 2

    # 00 f0 77 fb     bl         GPIOPinWrite                                     undefined GPIOPinWrite(int param
    patch = patch + calculate_bl_instr(gpio_pin_write_addr, instr_addr)
    instr_addr = instr_addr + 4

    # 04 22           movs       r2,#0x4
    patch = patch + bytearray(b'\x04\x22')
    instr_addr = instr_addr + 2

    # 11 46           mov        r1,r2
    patch = patch + bytearray(b'\x11\x46')
    instr_addr = instr_addr + 2

    # 20 46           mov        r0,r4
    patch = patch + bytearray(b'\x20\x46')
    instr_addr = instr_addr + 2

    # 00 f0 72 fb     bl         GPIOPinWrite                                     undefined GPIOPinWrite(int param
    patch = patch + calculate_bl_instr(gpio_pin_write_addr, instr_addr)
    instr_addr = instr_addr + 4

    # 20 46           mov        r0,r4
    patch = patch + bytearray(b'\x20\x46')
    instr_addr = instr_addr + 2

    # 00 22           movs       r2,#0x0
    patch = patch + bytearray(b'\x00\x22')
    instr_addr = instr_addr + 2

    # bd e8 10 40     pop.w      {r4,lr}
    patch = patch + bytearray(b'\xbd\xe8\x10\x40')
    instr_addr = instr_addr + 4

    # 08 21           movs       r1,#0x8
    patch = patch + bytearray(b'\x08\x21')
    instr_addr = instr_addr + 2

    # 00 f0 6b bb     b.w        GPIOPinWrite                                     undefined GPIOPinWrite(int param
    patch = patch + calculate_b_instr(gpio_pin_write_addr, instr_addr)
    instr_addr = instr_addr + 4

    #                      -- Flow Override: CALL_RETURN (CALL_TERMINATOR)
    # 00              align      align(1)
    patch = patch + bytearray(b'\x00')
    instr_addr = instr_addr + 1

    # bf              ??         BFh
    patch = patch + bytearray(b'\xbf')
    instr_addr = instr_addr + 1

    #                      DAT_000082bc                                    XREF[1]:     turn_blue_on:00008296(R)  
    # 00 50 02 40     undefined4 40025000h
    patch = patch + bytearray(b'\x00\x50\x02\x40')
    instr_addr = instr_addr + 4

    padding = bytearray([0]*(4 - len(patch)%4))
    patch = patch + padding

    return patch










def red_patch_generation(gpio_pin_write_addr, instr_addr):

        # 10 b5           push       {r4,lr}
        # 09 4c           ldr        r4,[DAT_000082e8]                                = 40025000h
        # 02 22           movs       r2,#0x2
        # 11 46           mov        r1,r2
        # 20 46           mov        r0,r4
        # 00 f0 61 fb     bl         GPIOPinWrite                                     undefined GPIOPinWrite(int param
        # 20 46           mov        r0,r4
        # 00 22           movs       r2,#0x0
        # 04 21           movs       r1,#0x4
        # 00 f0 5c fb     bl         GPIOPinWrite                                     undefined GPIOPinWrite(int param
        # 20 46           mov        r0,r4
        # 00 22           movs       r2,#0x0
        # bd e8 10 40     pop.w      {r4,lr}
        # 08 21           movs       r1,#0x8
        # 00 f0 55 bb     b.w        GPIOPinWrite                                     undefined GPIOPinWrite(int param
        #                      -- Flow Override: CALL_RETURN (CALL_TERMINATOR)
        # 00              align      align(1)
        # bf              ??         BFh
        #                      DAT_000082e8                                    XREF[1]:     turn_red_on:000082c2(R)  
        # 00 50 02 40     undefined4 40025000h


    # 10 b5           push       {r4,lr}
    patch = bytearray(b'\x10\xb5')
    instr_addr = instr_addr + 2

    # 09 4c           ldr        r4,[DAT_000082f8]                                = 40025000h
    patch = patch + bytearray(b'\x09\x4c')
    instr_addr = instr_addr + 2

    # 02 22           movs       r2,#0x2
    patch = patch + bytearray(b'\x02\x22')
    instr_addr = instr_addr + 2

    # 11 46           mov        r1,r2
    patch = patch + bytearray(b'\x11\x46')
    instr_addr = instr_addr + 2

    # 20 46           mov        r0,r4
    patch = patch + bytearray(b'\x20\x46')
    instr_addr = instr_addr + 2

    # 00 f0 61 fb     bl         GPIOPinWrite                                     undefined GPIOPinWrite(int param
    patch = patch + calculate_bl_instr(gpio_pin_write_addr, instr_addr)
    instr_addr = instr_addr + 4

    # 20 46           mov        r0,r4
    patch = patch + bytearray(b'\x20\x46')
    instr_addr = instr_addr + 2

    # 00 22           movs       r2,#0x0
    patch = patch + bytearray(b'\x00\x22')
    instr_addr = instr_addr + 2

    # 04 21           movs       r1,#0x4
    patch = patch + bytearray(b'\x04\x21')
    instr_addr = instr_addr + 2

    # 00 f0 5c fb     bl         GPIOPinWrite                                     undefined GPIOPinWrite(int param
    patch = patch + calculate_bl_instr(gpio_pin_write_addr, instr_addr)
    instr_addr = instr_addr + 4

    # 20 46           mov        r0,r4
    patch = patch + bytearray(b'\x20\x46')
    instr_addr = instr_addr + 2

    # 00 22           movs       r2,#0x0
    patch = patch + bytearray(b'\x00\x22')
    instr_addr = instr_addr + 2

    # bd e8 10 40     pop.w      {r4,lr}
    patch = patch + bytearray(b'\xbd\xe8\x10\x40')
    instr_addr = instr_addr + 4

    # 08 21           movs       r1,#0x8
    patch = patch + bytearray(b'\x08\x21')
    instr_addr = instr_addr + 2

    # 00 f0 55 bb     b.w        GPIOPinWrite                                     undefined GPIOPinWrite(int param
    patch = patch + calculate_b_instr(gpio_pin_write_addr, instr_addr)
    instr_addr = instr_addr + 4

    #                      -- Flow Override: CALL_RETURN (CALL_TERMINATOR)
    # 00              align      align(1)
    patch = patch + bytearray(b'\x00')
    instr_addr = instr_addr + 1

    # bf              ??         BFh
    patch = patch + bytearray(b'\xbf')
    instr_addr = instr_addr + 1

    #                      DAT_000082f8                                    XREF[1]:     turn_green_on:000082d2(R)  
    # 00 50 02 40     undefined4 40025000h
    patch = patch + bytearray(b'\x00\x50\x02\x40')
    instr_addr = instr_addr + 4

    padding = bytearray([0]*(4 - len(patch)%4))
    patch = patch + padding

    return patch


















def off_patch_generation(gpio_pin_write_addr, instr_addr):

        # 10 b5           push       {r4,lr}
        # 09 4c           ldr        r4,[DAT_00008340]                                = 40025000h
        # 00 22           movs       r2,#0x0
        # 20 46           mov        r0,r4
        # 02 21           movs       r1,#0x2
        # 00 f0 35 fb     bl         GPIOPinWrite                                     undefined GPIOPinWrite(int param
        # 20 46           mov        r0,r4
        # 00 22           movs       r2,#0x0
        # 04 21           movs       r1,#0x4
        # 00 f0 30 fb     bl         GPIOPinWrite                                     undefined GPIOPinWrite(int param
        # 20 46           mov        r0,r4
        # 00 22           movs       r2,#0x0
        # bd e8 10 40     pop.w      {r4,lr}
        # 08 21           movs       r1,#0x8
        # 00 f0 29 bb     b.w        GPIOPinWrite                                     undefined GPIOPinWrite(int param
        #                      -- Flow Override: CALL_RETURN (CALL_TERMINATOR)
        # 00              align      align(1)
        # bf              ??         BFh
        #                      DAT_00008340                                    XREF[1]:     turn_all_off:0000831a(R)  
        # 00 50 02 40     undefined4 40025000h


    # 10 b5           push       {r4,lr}
    patch = bytearray(b'\x10\xb5')
    instr_addr = instr_addr + 2

    # 09 4c           ldr        r4,[DAT_000082f8]                                = 40025000h
    patch = patch + bytearray(b'\x09\x4c')
    instr_addr = instr_addr + 2

    # 00 22           movs       r2,#0x0
    patch = patch + bytearray(b'\x00\x22')
    instr_addr = instr_addr + 2

    # 20 46           mov        r0,r4
    patch = patch + bytearray(b'\x20\x46')
    instr_addr = instr_addr + 2

    # 02 21           movs       r1,#0x2
    patch = patch + bytearray(b'\x02\x21')
    instr_addr = instr_addr + 2

    # 00 f0 35 fb     bl         GPIOPinWrite                                     undefined GPIOPinWrite(int param
    patch = patch + calculate_bl_instr(gpio_pin_write_addr, instr_addr)
    instr_addr = instr_addr + 4

    # 20 46           mov        r0,r4
    patch = patch + bytearray(b'\x20\x46')
    instr_addr = instr_addr + 2

    # 00 22           movs       r2,#0x0
    patch = patch + bytearray(b'\x00\x22')
    instr_addr = instr_addr + 2

    # 04 21           movs       r1,#0x4
    patch = patch + bytearray(b'\x04\x21')
    instr_addr = instr_addr + 2

    # 00 f0 30 fb     bl         GPIOPinWrite                                     undefined GPIOPinWrite(int param
    patch = patch + calculate_bl_instr(gpio_pin_write_addr, instr_addr)
    instr_addr = instr_addr + 4

    # 20 46           mov        r0,r4
    patch = patch + bytearray(b'\x20\x46')
    instr_addr = instr_addr + 2

    # 00 22           movs       r2,#0x0
    patch = patch + bytearray(b'\x00\x22')
    instr_addr = instr_addr + 2

    # bd e8 10 40     pop.w      {r4,lr}
    patch = patch + bytearray(b'\xbd\xe8\x10\x40')
    instr_addr = instr_addr + 4

    # 08 21           movs       r1,#0x8
    patch = patch + bytearray(b'\x08\x21')
    instr_addr = instr_addr + 2

    # 00 f0 29 bb     b.w        GPIOPinWrite                                     undefined GPIOPinWrite(int param
    patch = patch + calculate_b_instr(gpio_pin_write_addr, instr_addr)
    instr_addr = instr_addr + 4

    #                      -- Flow Override: CALL_RETURN (CALL_TERMINATOR)
    # 00              align      align(1)
    patch = patch + bytearray(b'\x00')
    instr_addr = instr_addr + 1

    # bf              ??         BFh
    patch = patch + bytearray(b'\xbf')
    instr_addr = instr_addr + 1

    #                      DAT_000082f8                                    XREF[1]:     turn_green_on:000082d2(R)  
    # 00 50 02 40     undefined4 40025000h
    patch = patch + bytearray(b'\x00\x50\x02\x40')
    instr_addr = instr_addr + 4

    padding = bytearray([0]*(4 - len(patch)%4))
    patch = patch + padding

    return patch
