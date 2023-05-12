#ifndef ASCON_H_
#define ASCON_H_

#include <stdint.h>

#include "word.h"
#include "permutations.h"

#define ASCON_AEAD_RATE 8        //Block size of ASCON
#define CRYPTO_ABYTES 16         //Authenticated Tag size


/*
Initialize ASCON Cipher with nonce stored in array 'n' and key in 'k'
*/
inline __attribute__((__always_inline__)) state_t ascon_aeadinit(const uint8_t* n, const uint8_t* k){

  word_t nonce_ls8b = LOAD(n, 8);
  word_t nonce_ms8b = LOAD(n + 8, 8);

  key_type key = KEY_INIT();
  key.ls8b = LOAD(k,8);
  key.ms8b = LOAD(k+8,8);
  
  state_t s = STATE_INIT();
  s.x0 = ASCON_128_IV;
  s.x1 = key.ls8b;
  s.x2 = key.ms8b;
  s.x3 = nonce_ls8b;
  s.x4 = nonce_ms8b;

  s = PROUNDS(s, 12);

  s.x3 = XOR(s.x3, key.ls8b);
  s.x4 = XOR(s.x4, key.ms8b);

  return s;
}


/*
Starting with Associated data
*/
inline __attribute__((__always_inline__)) state_t ascon_adata(state_t s, const uint8_t* ad, uint32_t adlen) {

 if (adlen) {

    while (adlen >= ASCON_AEAD_RATE) {
      s.x0 = XOR(s.x0, LOAD(ad, 8));
      s = PROUNDS(s, 6);
      ad += ASCON_AEAD_RATE;
      adlen -= ASCON_AEAD_RATE;
    }

    s.x0 = XOR(s.x0, PAD(adlen));
    if (adlen) 
      s.x0 = XOR(s.x0, LOAD(ad, adlen));
    s = PROUNDS(s, 6);
  }
  
  return s;
}

/*
Encrypting plain text
*/
inline __attribute__((__always_inline__)) state_t ascon_encrypt(state_t s, uint8_t* c, const uint8_t* pt, uint32_t mlen) 
{

  while (mlen >= ASCON_AEAD_RATE) {
    s.x0 = XOR(s.x0, LOAD(pt, 8));
    STORE(c, s.x0, 8);
    PROUNDS(s, 6);
    pt += ASCON_AEAD_RATE;
    c += ASCON_AEAD_RATE;
    mlen -= ASCON_AEAD_RATE;
  }

  s.x0 = XOR(s.x0, PAD(mlen));
  if (mlen) {
    s.x0 = XOR(s.x0, LOAD(pt, mlen));
    STORE(c, s.x0, mlen);
  }

  return s;

}

/*
Decrypting cipher text
*/
inline __attribute__((__always_inline__)) state_t ascon_decrypt(state_t s, uint8_t* m, const uint8_t* c, uint32_t clen) 
{

  while (clen >= ASCON_AEAD_RATE) {
    
    s.x0 = XOR(s.x0, LOAD(c, 8));
    STORE(m, s.x0, 8);
    s.x0 = LOAD(c, 8);
    PROUNDS(s, 6);

    m += ASCON_AEAD_RATE;
    c += ASCON_AEAD_RATE;
    clen -= ASCON_AEAD_RATE;
  }

  s.x0 = XOR(s.x0, PAD(clen));

  if (clen) {
    s.x0 = XOR(s.x0, LOAD(c, clen));
    STORE(m, s.x0, clen);
    s.x0 = CLEAR(s.x0, clen);
    s.x0 = XOR(s.x0, LOAD(c, clen));
  }

  return s;
}


/*
Calculating Authentication tag
*/
inline __attribute__((__always_inline__)) state_t ascon_final(state_t s, const uint8_t* k)
{
  key_type key = KEY_INIT();
  key.ls8b = LOAD(k,8);
  key.ms8b = LOAD(k+8,8);

  s.x1 = XOR(s.x1, key.ls8b);
  s.x2 = XOR(s.x2, key.ms8b);

  s = PROUNDS(s, 12);
  s.x3 = XOR(s.x3, key.ls8b);
  s.x4 = XOR(s.x4, key.ms8b);
  return s;
}





/*
ASCON AEAD Encryption

OUTPUTS
Cipher text will be stored in array 'c'
Cipher text lelngth will be stored in the memory location pointed by the pointer 'clen'

INPUTS
Plain text: array 'm'
Plain text length: 'mlen'
Associated data: array 'ad'
Associated data length: 'adlen'
Nonce: array 'npub'
Key: array 'k'
*/
int crypto_aead_encrypt(uint8_t* c, uint32_t* clen,
                        const uint8_t* m, uint32_t mlen,
                        const uint8_t* ad, uint32_t adlen,
                        const uint8_t* npub, const uint8_t* k) {

  state_t s;
  *clen = mlen + CRYPTO_ABYTES;
  /* perform ascon computation */
  s = ascon_aeadinit(npub, k);
  s = ascon_adata(s, ad, adlen);
  s = ascon_encrypt(s, c, m, mlen);
  s = ascon_final(s, k);
  /* set tag */
  STOREBYTES(c + mlen, s.x3, 8);
  STOREBYTES(c + mlen + 8, s.x4, 8);
  return 0;
}



/*
ASCON AEAD Decryption

OUTPUTS
Plain text will be stored in array 'm'
Plain text lelngth will be stored in the memory location pointed by the pointer 'cmlen'

INPUTS
Cipher text: array 'c'
Cipher text length: 'clen'
Associated data: array 'ad'
Associated data length: 'adlen'
Nonce: array 'npub'
Key: array 'k'
*/
int crypto_aead_decrypt(uint8_t* m, uint32_t* mlen,
                        const uint8_t* c, uint32_t clen, 
                        const uint8_t* ad, uint32_t adlen, 
                        const uint8_t* npub, const uint8_t* k) {
  state_t s;

  if (clen < CRYPTO_ABYTES) return -1;

  *mlen = clen = clen - CRYPTO_ABYTES;
  /* perform ascon computation */
  s = ascon_aeadinit(npub, k);
  s = ascon_adata(s, ad, adlen);
  s = ascon_decrypt(s, m, c, clen);
  s = ascon_final(s, k);
  /* verify tag (should be constant time, check compiler output) */
  s.x3 = XOR(s.x3, LOADBYTES(c + clen, 8));
  s.x4 = XOR(s.x4, LOADBYTES(c + clen + 8, 8));
  return NOTZERO(s.x3, s.x4);
}





#endif /* ASCON_H */
