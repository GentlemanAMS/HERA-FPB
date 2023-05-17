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

tia = 0x8904
cia = 0x82b6
print(calculate_b_instr(tia, cia))
