#ifndef PERMUTATIONS_H_
#define PERMUTATIONS_H_

#include <stdint.h>
#include "word.h"

#define ASCON_128_KEYBYTES 16
#define ASCON_128_RATE 8
#define ASCON_128_PA_ROUNDS 12
#define ASCON_128_PB_ROUNDS 6
#define ASCON_128_IV INITIALIZE_WORD(0x8021000008220000ull)


/*
Don't worry if you don't understand the code.
Even I don't. 
*/

/*
@Anyone who is checking the code.
The code was working functionally before.
I have added certain Check conditions inbetween 
no mistakes happens.

Everything under comment section 
'Checking for edge conditions'
is added. After adding the code has not been checked.

Once checked remove this comment line
*/

inline __attribute__((__always_inline__)) state_t ROUND(state_t s, word_t C) {

  state_t t;

  /* round constant */
  s.x2 = XOR(s.x2, C);

  /* s-box layer */
  s.x0 = XOR(s.x0, s.x4);
  s.x4 = XOR(s.x4, s.x3);
  s.x2 = XOR(s.x2, s.x1);
  t.x0 = XOR(s.x0, AND(NOT(s.x1), s.x2));
  t.x2 = XOR(s.x2, AND(NOT(s.x3), s.x4));
  t.x4 = XOR(s.x4, AND(NOT(s.x0), s.x1));
  t.x1 = XOR(s.x1, AND(NOT(s.x2), s.x3));
  t.x3 = XOR(s.x3, AND(NOT(s.x4), s.x0));
  t.x1 = XOR(t.x1, t.x0);
  t.x3 = XOR(t.x3, t.x2);
  t.x0 = XOR(t.x0, t.x4);

  /* linear layer */
  s.x2 = XOR(t.x2, ROTATE_WORD(t.x2, 6 - 1));
  s.x3 = XOR(t.x3, ROTATE_WORD(t.x3, 17 - 10));
  s.x4 = XOR(t.x4, ROTATE_WORD(t.x4, 41 - 7));
  s.x0 = XOR(t.x0, ROTATE_WORD(t.x0, 28 - 19));
  s.x1 = XOR(t.x1, ROTATE_WORD(t.x1, 61 - 39));
  s.x2 = XOR(t.x2, ROTATE_WORD(s.x2, 1));
  s.x3 = XOR(t.x3, ROTATE_WORD(s.x3, 10));
  s.x4 = XOR(t.x4, ROTATE_WORD(s.x4, 7));
  s.x0 = XOR(t.x0, ROTATE_WORD(s.x0, 19));
  s.x1 = XOR(t.x1, ROTATE_WORD(s.x1, 39));
  s.x2 = NOT(s.x2);

  return s;
}



const uint8_t constants[][2] = {{0xc, 0xc}, {0x9, 0xc}, {0xc, 0x9}, {0x9, 0x9},
                                {0x6, 0xc}, {0x3, 0xc}, {0x6, 0x9}, {0x3, 0x9},
                                {0xc, 0x6}, {0x9, 0x6}, {0xc, 0x3}, {0x9, 0x3}};

state_t PROUNDS(state_t s, int nr) 
{
  if (nr > 12) return s;                      //Checking for edge conditions
  
  for (uint8_t i = (12-nr); i < 12; i++)
  {
    uint64_t round_constant = ((uint64_t)constants[i][1] << 32) | ((uint64_t)constants[i][0]);
    s = ROUND(s, INITIALIZE_WORD(round_constant));
  }
  return s;
}

#endif

