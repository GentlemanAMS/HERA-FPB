#ifndef TIME_H
#define TIME_H

#define PART_TM4C1233H6PM

#include <stdbool.h>
#include <stdint.h>

#include "driverlib/pin_map.h"
#include "inc/hw_memmap.h"
#include "inc/hw_types.h"

/**
 * @brief Set the processor clock object
 * 
 * Sets Processor clock
 * Configuration:
 * Precision Internal Oscillator
 * Use PLL: PLL runs at 400 MHz - Default divider: 2 - so 200 MHz
 * PLL Divider: 2.5 - so 80 MHz
 */
void set_processor_clock(void);


/**
 * @brief 
 * Configuration of SysTick. This registers the interrupt and starts the counter
 */
void start_time(void);

/**
 * @brief 
 * returns microseconds since the start of the execution
 * @return uint32_t microseconds
 */
uint32_t micros(void);

/**
 * @brief 
 * returns milliseconds since the start of the execution
 * @return uint32_t milliseconds
 */
uint32_t millis(void);

/**
 * @brief 
 * SysTick Interrupt Handler. Whenever counter reaches zero, increment milliseconds variable
 */
void SysTickIntHandler(void);


#endif