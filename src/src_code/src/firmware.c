#include <stdbool.h>
#include <stdint.h>
#define PART_TM4C123GH6PM 1

#include "inc/hw_ints.h"
#include "inc/hw_gpio.h"
#include "inc/hw_memmap.h"

#include "driverlib/gpio.h"
#include "driverlib/pin_map.h"
#include "driverlib/sysctl.h"
#include "driverlib/flash.h"
#include "driverlib/eeprom.h"

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

#define REMAP_TABLE_ADDR (0x20007000UL)

#define HWREG(x) (*((volatile uint32_t *)(x)))

#define FLASH_REMAP_TABLE 0x3fc00
#define FLASH_COMP_TABLE 0x3fd00
#define FLASH_NO_OF_COUNTERS 0x3fb00
#define EEPROM_NO_OF_COUNTERS 0x100

volatile uint32_t old_instruction_address;
volatile uint32_t new_instruction_address;
volatile uint8_t link;


/**
 * @brief 
 * Enables FPB Control register
 * Documentation: https://developer.arm.com/documentation/ddi0403/d/Debug-Architecture/ARMv7-M-Debug/Flash-Patch-and-Breakpoint-unit/FlashPatch-Control-Register--FP-CTRL?lang=en
 */
void enable_fpb_control_register(){
    HWREG(FPB_CTRL_REGISTER) |= 0x03;
}

/**
 * @brief Set the fpb remap table address 
 * Documentation: https://developer.arm.com/documentation/ddi0403/d/Debug-Architecture/ARMv7-M-Debug/Flash-Patch-and-Breakpoint-unit/FlashPatch-Remap-register--FP-REMAP?lang=en
 */
void set_fpb_remap_table_address(){
    HWREG(FPB_REMAP_REGISTER) = REMAP_TABLE_ADDR;
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

    uint32_t comparator_value = old_instr_addr | 0x01; 

    if(comparator_index == 0)      HWREG(FPB_COMP0) = comparator_value;
    else if(comparator_index == 1) HWREG(FPB_COMP1) = comparator_value;
    else if(comparator_index == 2) HWREG(FPB_COMP2) = comparator_value;
    else if(comparator_index == 3) HWREG(FPB_COMP3) = comparator_value;
    else if(comparator_index == 4) HWREG(FPB_COMP4) = comparator_value;
    else if(comparator_index == 5) HWREG(FPB_COMP5) = comparator_value;

    //Updating FPB_COMPs in SRAM and FLASH
    FlashProgram(&comparator_value, FLASH_COMP_TABLE+4*comparator_index, 4);

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
    return bl_instr;
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

    if (link == true){ 
        remap_instr = calculate_branch_link_instruction(old_instr_addr, new_instr_addr);
    }
    else {
        remap_instr = calculate_branch_instruction(old_instr_addr, new_instr_addr);
    }

    remap_instr = LITTLE_ENDIAN(remap_instr);

    // If aligned no issues
    if(old_instr_addr % 4 == 0){
        
        write_fpb_comp_register(comp_index, old_instr_addr);
        
        //Updating remap table in SRAM and FLASH
        *((uint32_t *)(REMAP_TABLE_ADDR + 4*comp_index)) = remap_instr;
        FlashProgram(&remap_instr, FLASH_REMAP_TABLE+4*comp_index, 4);

        uint32_t counter;
        EEPROMRead(&counter, EEPROM_NO_OF_COUNTERS, 4);
        counter = counter + 1;
        EEPROMProgram(&counter, EEPROM_NO_OF_COUNTERS, 4);
    }

    // Half-aligned : pain in the arse
    // Multiple comparators must be used
    else{
        uint32_t old_instr[2];
        old_instr[0] = *((uint32_t *)(old_instr_addr & 0xFFFFFFFC));
        old_instr[1] = *((uint32_t *)(old_instr_addr & 0xFFFFFFFC) + 4);

        write_fpb_comp_register(comp_index, old_instr_addr & 0xFFFFFFFC);
        write_fpb_comp_register(comp_index+1, (old_instr_addr & 0xFFFFFFFC) + 4);

        uint32_t instr1 = (((remap_instr & 0x0000FFFF) << 16) | (old_instr[0] & 0x0000FFFF));
        uint32_t instr2 = ((old_instr[1] & 0xFFFF0000) | ((remap_instr & 0xFFFF0000) >> 16));

        //Updating remap table in SRAM and FLASH
        *((uint32_t *)(REMAP_TABLE_ADDR + 4*comp_index)) = instr1; 
        *((uint32_t *)(REMAP_TABLE_ADDR + 4*(comp_index+1))) = instr2;
        FlashProgram(&instr1, FLASH_REMAP_TABLE+4*comp_index, 4);
        FlashProgram(&instr2, FLASH_REMAP_TABLE+4*comp_index+4, 4);

        uint32_t counter;
        EEPROMRead(&counter, EEPROM_NO_OF_COUNTERS, 4);
        counter = counter + 2;
        EEPROMProgram(&counter, EEPROM_NO_OF_COUNTERS, 4);
    }
    return;
}


void hera_fpb_setup(){
    enable_fpb_control_register();
    set_fpb_remap_table_address();
    uint32_t counter;
    EEPROMRead(&counter, EEPROM_NO_OF_COUNTERS, 4);
    hera_remap_instr(old_instruction_address, new_instruction_address, counter, link);
}


void turn_blue_on()
{
    GPIOPinWrite(GPIO_PORTF_BASE, GPIO_PIN_1, 0); // r
    GPIOPinWrite(GPIO_PORTF_BASE, GPIO_PIN_2, GPIO_PIN_2); // b
    GPIOPinWrite(GPIO_PORTF_BASE, GPIO_PIN_3, 0); // g
}


/**
void turn_red_on()
{
    GPIOPinWrite(GPIO_PORTF_BASE, GPIO_PIN_1, GPIO_PIN_1); // r
    GPIOPinWrite(GPIO_PORTF_BASE, GPIO_PIN_2, 0); // b
    GPIOPinWrite(GPIO_PORTF_BASE, GPIO_PIN_3, 0); // g
}

void turn_green_on()
{
    GPIOPinWrite(GPIO_PORTF_BASE, GPIO_PIN_1, 0); // r
    GPIOPinWrite(GPIO_PORTF_BASE, GPIO_PIN_2, 0); // b
    GPIOPinWrite(GPIO_PORTF_BASE, GPIO_PIN_3, GPIO_PIN_3); // g
}

void turn_switch_off()
{
    GPIOPinWrite(GPIO_PORTF_BASE, GPIO_PIN_1, 0); // r
    GPIOPinWrite(GPIO_PORTF_BASE, GPIO_PIN_2, 0); // b
    GPIOPinWrite(GPIO_PORTF_BASE, GPIO_PIN_3, 0); // g
}
 */



/************
 * Functionality 
 ***********/
void setup()
{
    SysCtlPeripheralEnable(SYSCTL_PERIPH_GPIOF);

/******************************************/
    SysCtlPeripheralEnable(SYSCTL_PERIPH_EEPROM0);
    EEPROMInit();

    uint32_t counter;
    EEPROMRead(&counter, EEPROM_NO_OF_COUNTERS, 4);
    counter = counter & 0xFF;
    if (counter > 6) counter = 0;
    EEPROMProgram(&counter, EEPROM_NO_OF_COUNTERS, 4);

    for (uint8_t i = 0; i < counter; i++){
        HWREG(FPB_CTRL_REGISTER) |= 0x03;
        HWREG(FPB_REMAP_REGISTER) = REMAP_TABLE_ADDR;
        *((uint32_t *)(REMAP_TABLE_ADDR + 4*i)) = *((uint32_t *)(FLASH_REMAP_TABLE + 4*i));
    }

    if (counter >= 1)       HWREG(FPB_COMP0) = *((uint32_t *)(FLASH_COMP_TABLE + 0));
    if (counter >= 2)       HWREG(FPB_COMP1) = *((uint32_t *)(FLASH_COMP_TABLE + 4)); 
    if (counter >= 3)       HWREG(FPB_COMP2) = *((uint32_t *)(FLASH_COMP_TABLE + 8));
    if (counter >= 4)       HWREG(FPB_COMP3) = *((uint32_t *)(FLASH_COMP_TABLE + 12)); 
    if (counter >= 5)       HWREG(FPB_COMP4) = *((uint32_t *)(FLASH_COMP_TABLE + 16));
    if (counter == 6)       HWREG(FPB_COMP5) = *((uint32_t *)(FLASH_COMP_TABLE + 20)); 
/******************************************/

    uart_init();
}

volatile int delay;
#define DELAY 0xFFFFF
volatile bool always_true = true;


uint8_t patch[256];
void loop()
{
        
    if(uart_read_avail(UART0_BASE)){

        uint8_t start_byte;
        while(true){
            uart_read(UART0_BASE, &start_byte, 1);
            if (start_byte == 0x55)
                break;
        }

        uint8_t data[4];
        uart_read(UART0_BASE, data, 4);
        old_instruction_address = data[0];
        old_instruction_address = (old_instruction_address << 8) | data[1];
        old_instruction_address = (old_instruction_address << 8) | data[2];
        old_instruction_address = (old_instruction_address << 8) | data[3];

        uart_read(UART0_BASE, data, 4);
        new_instruction_address = data[0];
        new_instruction_address = (new_instruction_address << 8) | data[1];
        new_instruction_address = (new_instruction_address << 8) | data[2];
        new_instruction_address = (new_instruction_address << 8) | data[3];

        FlashErase(new_instruction_address);

        uart_read(UART0_BASE, &link, 1);

        uint8_t send_length = 0x44;
        uart_write(UART0_BASE, &send_length, 1);

        uint8_t patch_length;
        uart_read(UART0_BASE, &patch_length, 1);

        uint8_t send_patch = 0x44;
        uart_write(UART0_BASE, &send_patch, 1);            

        for (uint32_t i = 0; i < patch_length; i=i+4){
            
            uart_read(UART0_BASE, patch+i, 4);

            uint8_t send_feedback = 0x43;
            uart_write(UART0_BASE, &send_feedback, 1);
            
            int done = FlashProgram(patch+i, new_instruction_address + i, 4);
            if (done == -1) GPIOPinWrite(GPIO_PORTF_BASE, GPIO_PIN_1, GPIO_PIN_1);
        }
        
        hera_fpb_setup();
    }

    turn_blue_on();
    for (delay = 0; delay < DELAY; delay++);
    
    turn_blue_on();
    for (delay = 0; delay < DELAY; delay++);
    
    turn_blue_on();
    for (delay = 0; delay < DELAY; delay++);
}


int main(void){
    setup();
    while(always_true)
        loop();
    turn_blue_on();
}