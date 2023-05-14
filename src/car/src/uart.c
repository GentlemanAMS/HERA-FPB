#define PART_TM4C123GH6PM 1

#include <stdbool.h>
#include <stdint.h>
#include <string.h>

#include "driverlib/gpio.h"
#include "driverlib/pin_map.h"
#include "driverlib/sysctl.h"
#include "driverlib/uart.h"

#include "inc/hw_memmap.h"
#include "inc/hw_types.h"
#include "inc/hw_uart.h"


#include "uart.h"
#include "time.h"

#define BAUD_RATE_TOBOARD 115200              //Baud rate for interaction between boards
#define BAUD_RATE_TOPC 115200                 //Baud rate for interaction between board and PC


/**
 * @brief 
 * Sets up UART communication with PC
 */
void uart_init(void){

    //Enable UART0 Peripheral
    SysCtlPeripheralEnable(SYSCTL_PERIPH_UART0);
    while(!SysCtlPeripheralReady(SYSCTL_PERIPH_UART0));

    //Enable GPIOA Peripheral
    SysCtlPeripheralEnable(SYSCTL_PERIPH_GPIOA);
    while(!SysCtlPeripheralReady(SYSCTL_PERIPH_GPIOA));

    //Configure GPIO pins for RX and TX
    GPIOPinConfigure(GPIO_PA0_U0RX);
    GPIOPinConfigure(GPIO_PA1_U0TX);

    //Configure GPIO and set them up to UART0
    GPIOPinTypeUART(GPIO_PORTA_BASE, GPIO_PIN_0 | GPIO_PIN_1);

    //UART Clock source is system clock
    UARTClockSourceSet(UART0_BASE, UART_CLOCK_SYSTEM);
    
    //Set UART Baud rate
    UARTConfigSetExpClk(UART0_BASE, SysCtlClockGet(), BAUD_RATE_TOPC, UART_CONFIG_WLEN_8 | UART_CONFIG_PAR_NONE | UART_CONFIG_STOP_ONE);
    
    //Enable UART
    UARTEnable(UART0_BASE);
}



/**
 * @brief 
 * Write 'buffer' of size 'buffer_length' bytes into UART on Port 'uart_port'
 * @param uart_port : UART1_BASE or UART0_BASE
 * @param buffer : values from array 'buffer' is transmitted
 * @param buffer_length : number of bytes to be transmitted
 */
void uart_write(uint32_t uart_port, uint8_t* buffer, uint32_t buffer_length)
{
    uint32_t i;
    for (i = 0; i < buffer_length; i++)
        UARTCharPut(uart_port, buffer[i]);
}


/**
 * @brief 
 * Check if there are characters available to read from UART port 'uart_port'
 * @param uart_port : UART1_BASE or UART0_BASE
 * @return true : if characters are available
 * @return false : if characters are not available
 */
bool uart_read_avail(uint32_t uart_port)
{
    return UARTCharsAvail(uart_port);
}


/**
 * @brief 
 * Try to read 'buffer_length' characters into 'buffer' from UART port 'uart_port' within 'timeout' milliseconds
 * If expected message length is read then return 0, else return -1
 * @param uart_port : UART1_BASE or UART0_BASE
 * @param buffer : received bytes is filled into this buffer
 * @param buffer_length : number of bytes expected to be received
 * @param timeout : time before which all bytes must be received
 * @return int32_t : -1 if expected bytes are not received - 0 when received
 */
int32_t uart_read(uint32_t uart_port, uint8_t* buffer, uint32_t buffer_length, uint32_t timeout)
{
    uint32_t bytes_read = 0;
    uint32_t start_read_time = millis();

    while((millis() < start_read_time + timeout) && bytes_read < buffer_length){
        if (!UARTCharsAvail(uart_port)) continue;
        buffer[bytes_read] = (uint8_t)UARTCharGet(uart_port);
        bytes_read++;
    }
    if (bytes_read == buffer_length) return 0;
    else return -1;
}


