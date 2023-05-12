#ifndef UART_H
#define UART_H

#include <stdbool.h>
#include <stdint.h>

#include "inc/hw_memmap.h"

/**
 * @brief 
 * Sets up UART communication with PC
 */
void uart_hosttools_init(void);


/**
 * @brief 
 * Sets up UART communication with other board
 */
void uart_board_init(void);

/**
 * @brief 
 * Write 'buffer' of size 'buffer_length' bytes into UART on Port 'uart_port'
 * @param uart_port : UART1_BASE or UART0_BASE
 * @param buffer : values from array 'buffer' is transmitted
 * @param buffer_length : number of bytes to be transmitted
 */
void uart_write(uint32_t uart, uint8_t* buffer, uint32_t buffer_length);


/**
 * @brief 
 * Check if there are characters available to read from UART port 'uart_port'
 * @param uart_port : UART1_BASE or UART0_BASE
 * @return true : if characters are available
 * @return false : if characters are not available
 */
bool uart_read_avail(uint32_t uart_port);

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
int32_t uart_read(uint32_t uart_port, uint8_t* buffer, uint32_t buffer_length, uint32_t timeout);


#endif // UART_H