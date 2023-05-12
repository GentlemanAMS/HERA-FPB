/*****************************************************************
 * To run this file:
 * gcc package_feature.c
 * ./a.out 21 21 52 54 34 65 32 213 54 65 235 75 232 55 76 2 45 32
 * 
 * Input:
 * First two inputs are CARID and FEATUREID
 * Next 16 inputs are key bytes
 * Note: these numbers must be unsigned and lesser than 255
 * 
 * Output:
 * Writes encrypted message in the file FILENAME
 * Returns -1 if the operation fails anywhere in the process
 ***************************************************************/


#include <stdio.h>
#include <stdlib.h>

#include <stdint.h>
#include <stdbool.h>
#include <time.h>  

#include "ascon.h"

#define CARIDLEN 1
#define FEATUREIDLEN 1
#define KEYLEN 16
#define NONCELEN 16
#define RANDOMLEN 4
#define MESSAGELEN (CARIDLEN + FEATUREIDLEN + RANDOMLEN)
#define AUTHENTICATION_TAG_LEN 16
#define CIPHERTEXTLEN (MESSAGELEN + AUTHENTICATION_TAG_LEN)
#define SENDLEN (NONCELEN + CIPHERTEXTLEN)


int main(int argc, char ** argv)
{
    uint8_t key[KEYLEN];
    uint8_t nonce[NONCELEN];
    uint8_t message[MESSAGELEN];
    uint8_t cipher_text[CIPHERTEXTLEN];
    uint8_t message_send[SENDLEN];


    //Geting inputs through commandline and check whether inputs are valid or not

    if (argc != (1 + CARIDLEN + FEATUREIDLEN + KEYLEN))
        return 0;

    char* carid_str = argv[1];
    char* featureid_str = argv[2];

    char* key_str[KEYLEN];
    for (uint8_t i = 0; i < KEYLEN; i++)
        key_str[i] = argv[3+i];
    
    char* stopstring;
    int result;
    result = strtol(carid_str, &stopstring, 10);
    if (*stopstring != '\0' || result > 255 || result < 0){
        return -1; 
    }
    uint8_t carid = (uint8_t) result;

    result = strtol(featureid_str, &stopstring, 10);
    if (*stopstring != '\0'  || result > 255 || result < 0){
        return -1; 
    }
    uint8_t featureid = (uint8_t) result;
    
    for (uint8_t i = 0; i < KEYLEN; i++)
    {    
        result = strtol(key_str[i], &stopstring, 10);
        if (*stopstring != '\0' || result > 255 || result < 0){
            return -1; 
        }
        key[i] = (uint8_t) result;
    }
    //Generate the message to be encrypted
    //message: {carid, featureid, random_byte, random_byte, random_byte, random_byte}

    time_t t;
    srand((uint32_t)time(&t));

    for (uint8_t i = 0; i < NONCELEN; i++)
        nonce[i] = (uint8_t)rand();

    message[0] = carid;
    message[1] = featureid;
    message[2] = (uint8_t)rand();
    message[3] = (uint8_t)rand();    
    message[4] = (uint8_t)rand();
    message[5] = (uint8_t)rand();
    
    //Encrypt using ASCON

    uint32_t clen;
    uint8_t* associated_data_temp;
    crypto_aead_encrypt(cipher_text, &clen, message, MESSAGELEN, associated_data_temp, 0, nonce, key);
    if (clen != CIPHERTEXTLEN){
        return -1;
    }
    
    //Generate the cyptic message: {nonce, ciphertext}

    for(uint8_t i = 0; i < NONCELEN; i++)
        message_send[i] = nonce[i];
    
    for(uint8_t i = 0; i < CIPHERTEXTLEN; i++)
        message_send[NONCELEN + i] = cipher_text[i];

    //Store the message in the binary file
    for(int i=0; i<SENDLEN; i++){
        printf("%c", message_send[i]);
    }
    return 0;
}
