#include <stdbool.h>
#include <stdint.h>
#define PART_TM4C123GH6PM 1

#include "inc/hw_ints.h"
#include "inc/hw_gpio.h"
#include "inc/hw_memmap.h"

#include "driverlib/gpio.h"
#include "driverlib/pin_map.h"
#include "driverlib/sysctl.h"

#include "uart.h"
#include "time.h"

#define FPB_CTRL_REGISTER   0xE0002000UL
#define FPB_REMAP_REGISTER  0xE0002004UL
#define FPB_COMP0           0xE0002008UL
#define FPB_COMP1           0xE000200CUL
#define FPB_COMP2           0xE0002010UL
#define FPB_COMP3           0xE0002014UL
#define FPB_COMP4           0xE0002018UL
#define FPB_COMP5           0xE000201CUL
#define FPB_COMP6           0xE0002020UL
#define FPB_COMP7           0xE0002024UL

#define HWREG(x) (*((volatile uint32_t *)(x)))


uint32_t remap_table[8];

/**
 * @brief 
 * Enables FPB Control register
 * Documentation: https://developer.arm.com/documentation/ddi0403/d/Debug-Architecture/ARMv7-M-Debug/Flash-Patch-and-Breakpoint-unit/FlashPatch-Control-Register--FP-CTRL?lang=en
 */
void enable_fpb_control_register(){
    HWREG(FPB_CTRL_REGISTER) = 0x03UL;
}

/**
 * @brief Set the fpb remap table address 
 * Documentation: https://developer.arm.com/documentation/ddi0403/d/Debug-Architecture/ARMv7-M-Debug/Flash-Patch-and-Breakpoint-unit/FlashPatch-Remap-register--FP-REMAP?lang=en
 */
void set_fpb_remap_table_address(){
    HWREG(FPB_REMAP_REGISTER) = remap_table;
}

/**
 * @brief 
 * Writes FPB comparator register
 * Documentation: https://developer.arm.com/documentation/ddi0403/d/Debug-Architecture/ARMv7-M-Debug/Flash-Patch-and-Breakpoint-unit/FlashPatch-Comparator-register--FP-COMPn?lang=en
 * @param comparator_index : value between 0 to 7 indicating COMPx
 * @param old_instr_addr : instruction address to be remapped
 */
void write_fpb_comp_register(
    uint8_t comparator_index,
    uint32_t old_instr_addr
){
    if(comparator_index == 0)      HWREG(FPB_COMP0) = old_instr_addr | 0x01;
    else if(comparator_index == 1) HWREG(FPB_COMP1) = old_instr_addr | 0x01;
    else if(comparator_index == 2) HWREG(FPB_COMP2) = old_instr_addr | 0x01;
    else if(comparator_index == 3) HWREG(FPB_COMP3) = old_instr_addr | 0x01;
    else if(comparator_index == 4) HWREG(FPB_COMP4) = old_instr_addr | 0x01;
    else if(comparator_index == 5) HWREG(FPB_COMP5) = old_instr_addr | 0x01;
    else if(comparator_index == 6) HWREG(FPB_COMP6) = old_instr_addr | 0x01;
    else if(comparator_index == 7) HWREG(FPB_COMP7) = old_instr_addr | 0x01;
}


/**
 * @brief Encoding branch instruction
 * Find offset, encode into an unconditional branch instruction
 * 
 * As per documentation provided in:
 * Encoding T4
 * https://developer.arm.com/documentation/ddi0406/c/Application-Level-Architecture/Instruction-Details/Alphabetical-list-of-instructions/B?lang=en
 * https://developer.arm.com/documentation/ddi0406/c/Application-Level-Architecture/Thumb-Instruction-Set-Encoding/32-bit-Thumb-instruction-encoding/Branches-and-miscellaneous-control?lang=en
 * 
 * @param curr_instr_addr : current instruction
 * @param target_instr_addr : instruction to jump
 * @return uint32_t : instruction
 */

uint32_t calculate_branch_instruction(
    uint32_t curr_instr_addr,
    uint32_t target_instr_addr)
{

    uint32_t offset = target_instr_addr - curr_instr_addr - 4;
    
    uint32_t offset_msb10 = (offset >> 12) & 0x3FF;
    uint32_t offset_lsb11 = (offset >> 1) & 0x07FF;

    uint32_t s = (offset & (1 << 24)) >> 24;
    uint32_t i1 = (offset & (1 << 23)) >> 23;
    uint32_t i2 = (offset & (1 << 22)) >> 22;

    uint32_t j1 = 0x01 & ((~i1) ^ s);
    uint32_t j2 = 0x01 & ((~i2) ^ s);


    uint32_t b_instr_msb16 = ((0x1E << 11) | (s << 10) | offset_msb10) & 0xFFFF; 
    uint32_t b_instr_lsb16 = ((0x02 << 14) | (j1 << 13) | (0x01 << 12) | (j2 << 11) | offset_lsb11) & 0xFFFF;

    uint32_t b_instr = ((uint32_t)b_instr_msb16 << 16) | b_instr_lsb16;

    return b_instr;
}

/**
 * @brief Encoding branch instruction
 * Find offset, encode into an unconditional branch and link instruction
 * 
 * As per documentation provided in:
 * Encoding T1
 * https://developer.arm.com/documentation/ddi0406/c/Application-Level-Architecture/Instruction-Details/Alphabetical-list-of-instructions/B?lang=en
 * https://developer.arm.com/documentation/ddi0406/c/Application-Level-Architecture/Instruction-Details/Alphabetical-list-of-instructions/BL--BLX--immediate-?lang=en
 * 
 * @param curr_instr_addr : current instruction
 * @param target_instr_addr : instruction to jump
 * @return uint32_t : instruction
 */
uint32_t calculate_branch_link_instruction(
    uint32_t curr_instr_addr,
    uint32_t target_instr_addr
)
{
    uint32_t b_instr = calculate_branch_instruction(curr_instr_addr, target_instr_addr);
    //14th bit is set as per documentation
    uint32_t bl_instr = b_instr | 0x00004000;
}


#define LITTLE_ENDIAN(x) ((x & 0xFFFF0000) >> 16) | ((x & 0x0000FFFF) << 16)


void hera_remap_instr(
    uint32_t old_instr_addr,
    uint32_t new_instr_addr,
    uint32_t comp_index,
    bool link
)
{
    
    uint32_t remap_instr;

    if (link == true) remap_instr = calculate_branch_link_instruction(old_instr_addr, new_instr_addr);
    else remap_instr = calculate_branch_instruction(old_instr_addr, new_instr_addr);
    
    // If aligned no issues
    if(old_instr_addr % 4 == 0){
        write_fpb_comp_register(comp_index, old_instr_addr);
        remap_table[comp_index] = LITTLE_ENDIAN(remap_instr);
    }

    // Half-aligned : pain in the arse
    // Multiple comparators must be used
    else{
        uint32_t old_instr[2];
        old_instr[0] = *((uint32_t *)(old_instr_addr & 0xFFFFFFFC));
        old_instr[1] = *((uint32_t *)(old_instr_addr & 0xFFFFFFFC) + 4);

        write_fpb_comp_register(comp_index, old_instr_addr & 0xFFFFFFFC);
        write_fpb_comp_register(comp_index+1, (old_instr_addr & 0xFFFFFFFC) + 4);

        remap_table[comp_index] = ((LITTLE_ENDIAN(remap_instr) & 0x0000FFFF) << 16) | (old_instr[0] & 0x0000FFFF);
        remap_table[comp_index + 1] = (old_instr[1] & 0xFFFF0000) | ((LITTLE_ENDIAN(remap_instr) & 0xFFFF0000) >> 16);
    }

    return;
}


#define INSTR_ADDRESS 0x000081a0
#define NEW_INSTR_ADDRESS 0x000081db

void hera_fpb_setup(){
    enable_fpb_control_register();
    set_fpb_remap_table_address();
    hera_remap_instr(INSTR_ADDRESS, NEW_INSTR_ADDRESS, 0, false);
}



void turn_red_on()
{
    // Change LED color: green
    GPIOPinWrite(GPIO_PORTF_BASE, GPIO_PIN_1, GPIO_PIN_1); // r
    GPIOPinWrite(GPIO_PORTF_BASE, GPIO_PIN_2, 0); // b
    GPIOPinWrite(GPIO_PORTF_BASE, GPIO_PIN_3, 0); // g

    volatile bool always_true = true;
    while(always_true);
}

void turn_blue_on()
{
    // Change LED color: green
    GPIOPinWrite(GPIO_PORTF_BASE, GPIO_PIN_1, 0); // r
    GPIOPinWrite(GPIO_PORTF_BASE, GPIO_PIN_2, GPIO_PIN_2); // b
    GPIOPinWrite(GPIO_PORTF_BASE, GPIO_PIN_3, 0); // g

    volatile bool always_true = true;
    while(always_true);
}

/********************************
 * Functionality 
 *******************************/
void setup()
{
    SysCtlPeripheralEnable(SYSCTL_PERIPH_GPIOF);
    hera_fpb_setup();
    turn_red_on();

    volatile bool always_true = true;
    while(always_true);
}

void loop()
{
    volatile bool always_true = true;
    while(always_true);

    // Writing this code - although it is never reached - compiler optimizes this away completely. 
    // So chumma writing this
    turn_blue_on();    
}


int main(void){
    setup();
    while(true)
        loop();
}
