#include <stdbool.h>
#include <stdint.h>

#include "driverlib/systick.h"
#include "driverlib/sysctl.h"
#include "driverlib/interrupt.h"
#include "time.h"

static volatile uint32_t milliseconds = 0;

#define SYSTICK_FREQUENCY 1000UL


/**
 * @brief Set the processor clock object
 * 
 * Sets Processor clock
 * Configuration:
 * Precision Internal Oscillator
 * Use PLL: PLL runs at 400 MHz - Default divider: 2 - so 200 MHz
 * PLL Divider: 2.5 - so 80 MHz
 */
void set_processor_clock(void){
    SysCtlClockSet(SYSCTL_SYSDIV_2_5 | SYSCTL_USE_PLL | SYSCTL_OSC_INT);
}

/**
 * @brief 
 * Configuration of SysTick. This registers the interrupt and starts the counter
 */
void start_time(void){

    //SysCtlClockGet() should return 80 Mhz: 80,000,000 Hz
    //Interrupt should occur every millsecond: 80,000 cycles per millisecond
    SysTickPeriodSet(SysCtlClockGet() / SYSTICK_FREQUENCY);

    //Interrupt registered. When SysTick counter reaches 0, it causes an interrupt
    SysTickIntRegister(SysTickIntHandler);

    //Enable Master Interrupt
    IntMasterEnable();

    //Enable SysTick Interrupt
    SysTickIntEnable();
    
    //Counter starts now
    SysTickEnable();

}

/**
 * @brief 
 * SysTick Interrupt Handler. Whenever counter reaches zero, increment milliseconds variable
 */
void SysTickIntHandler(void){
    milliseconds++;
}


/**
 * @brief 
 * returns microseconds since the start of the execution
 * @return uint32_t microseconds
 */
uint32_t micros(void){
    return (milliseconds * 1000) + ((((SysCtlClockGet() / SYSTICK_FREQUENCY) - SysTickValueGet()) * 1000) / (SysCtlClockGet() / SYSTICK_FREQUENCY)); 
}


/**
 * @brief 
 * returns milliseconds since the start of the execution
 * @return uint32_t milliseconds
 */
uint32_t millis(void){
    return milliseconds;
}
