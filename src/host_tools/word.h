#ifndef WORD_H_
#define WORD_H_

#include <stdint.h>




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


#define U64BIG(x)                          \
  (((0x00000000000000FFULL & (x)) << 56) | \
   ((0x000000000000FF00ULL & (x)) << 40) | \
   ((0x0000000000FF0000ULL & (x)) << 24) | \
   ((0x00000000FF000000ULL & (x)) << 8) |  \
   ((0x000000FF00000000ULL & (x)) >> 8) |  \
   ((0x0000FF0000000000ULL & (x)) >> 24) | \
   ((0x00FF000000000000ULL & (x)) >> 40) | \
   ((0xFF00000000000000ULL & (x)) >> 56))
#define U32BIG(x)                                           \
  (((0x000000FF & (x)) << 24) | ((0x0000FF00 & (x)) << 8) | \
   ((0x00FF0000 & (x)) >> 8) | ((0xFF000000 & (x)) >> 24))
#define U16BIG(x) (((0x00FF & (x)) << 8) | ((0xFF00 & (x)) >> 8))




typedef struct {
    uint32_t ms4b;   
    uint32_t ls4b;
} word_t;

typedef struct{
  word_t ls8b;
  word_t ms8b;
} key_type;

typedef struct{
  word_t x0;
  word_t x1;
  word_t x2;
  word_t x3;
  word_t x4;
} state_t;






















inline __attribute__((__always_inline__)) uint32_t ROTATE32(uint32_t input, int n){
    
    uint32_t result;
    
    if (n < 0) return input;          //Checking for edge conditions
    
    result = (n == 0) ? input : (input >> n) | (input << (32-n)); 
    return result;
}

inline __attribute__((__always_inline__)) word_t ROTATE_WORD(word_t input, int n){
   
    word_t result;

    if (n <= 0) return input;         //Checking for edge conditions
    
    result.ls4b = (n % 2) ? ROTATE32(input.ms4b, (n - 1)/2) : ROTATE32(input.ls4b, n/2);
    result.ms4b = (n % 2) ? ROTATE32(input.ls4b, (n + 1)/2) : ROTATE32(input.ms4b, n/2);
    return result;
}

inline __attribute__((__always_inline__)) word_t INITIALIZE_WORD(uint64_t input){
    word_t result;
    result.ms4b = (uint32_t)(input >> 32);
    result.ls4b = (uint32_t)(input & 0xFFFFFFFF);
    return result;
}











inline __attribute__((__always_inline__)) uint64_t UINT64_T(word_t input){
    uint64_t result;
    result = ((uint64_t)(input.ms4b) << 32) | ((uint64_t) input.ls4b);
    return result;
}

/***************************************************
This section of code seems like a blackbox
No idea what it means or how it works
Need to figure out what it does
>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
***************************************************/

inline __attribute__((__always_inline__)) uint32_t DEINTERLEAVE_UINT32(uint32_t x) {
  uint32_t t;
  t = (x ^ (x >> 1)) & 0x22222222, x ^= t ^ (t << 1);
  t = (x ^ (x >> 2)) & 0x0C0C0C0C, x ^= t ^ (t << 2);
  t = (x ^ (x >> 4)) & 0x00F000F0, x ^= t ^ (t << 4);
  t = (x ^ (x >> 8)) & 0x0000FF00, x ^= t ^ (t << 8);
  return x;
}

inline __attribute__((__always_inline__)) uint32_t INTERLEAVE_UINT32(uint32_t x) {
  uint32_t t;
  t = (x ^ (x >> 8)) & 0x0000FF00, x ^= t ^ (t << 8);
  t = (x ^ (x >> 4)) & 0x00F000F0, x ^= t ^ (t << 4);
  t = (x ^ (x >> 2)) & 0x0C0C0C0C, x ^= t ^ (t << 2);
  t = (x ^ (x >> 1)) & 0x22222222, x ^= t ^ (t << 1);
  return x;
}

inline __attribute__((__always_inline__)) uint64_t DEINTERLEAVE32(uint64_t in) {
  uint32_t hi = in >> 32;
  uint32_t lo = in;
  uint32_t r0, r1;
  lo = DEINTERLEAVE_UINT32(lo);
  hi = DEINTERLEAVE_UINT32(hi);
  r0 = (lo & 0x0000FFFF) | (hi << 16);
  r1 = (lo >> 16) | (hi & 0xFFFF0000);
  return (uint64_t)r1 << 32 | r0;
}

inline __attribute__((__always_inline__)) uint64_t INTERLEAVE32(uint64_t in) {
  uint32_t r0 = in;
  uint32_t r1 = in >> 32;
  uint32_t lo = (r0 & 0x0000FFFF) | (r1 << 16);
  uint32_t hi = (r0 >> 16) | (r1 & 0xFFFF0000);
  lo = INTERLEAVE_UINT32(lo);
  hi = INTERLEAVE_UINT32(hi);
  return (uint64_t)hi << 32 | lo;
}


inline __attribute__((__always_inline__)) word_t U64TOWORD(uint64_t input) { 
    word_t result;
    result = INITIALIZE_WORD(DEINTERLEAVE32(input));
    return result;
}


inline __attribute__((__always_inline__)) uint64_t WORDTOU64(word_t w) { 
    return INTERLEAVE32(UINT64_T(w)); 
}


/***************************************************
<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
This section of code seems like a blackbox
No idea what it means or how it works
Need to figure out what it does
***************************************************/






inline __attribute__((__always_inline__)) word_t NOT(word_t input) {
  word_t result;
  result.ls4b = ~input.ls4b;
  result.ms4b = ~input.ms4b;
  return result;
}

inline __attribute__((__always_inline__)) word_t XOR(word_t input_a, word_t input_b) {
  word_t result;
  result.ls4b = input_a.ls4b ^ input_b.ls4b;
  result.ms4b = input_a.ms4b ^ input_b.ms4b;
  return result;
}

inline __attribute__((__always_inline__)) word_t AND(word_t input_a, word_t input_b) {
  word_t result;
  result.ms4b = input_a.ms4b & input_b.ms4b;
  result.ls4b = input_a.ls4b & input_b.ls4b;
  return result;
}






inline __attribute__((__always_inline__)) int NOTZERO(word_t input_a, word_t input_b) {
  uint32_t result = input_a.ls4b | input_a.ms4b | input_b.ls4b | input_b.ms4b;
  result |= result >> 16;
  result |= result >> 8;
  return ((((int)(result & 0xff) - 1) >> 8) & 1) - 1;
}

inline __attribute__((__always_inline__)) word_t PAD(int i) {

  if (i < 0) return INITIALIZE_WORD(0);         //Checking for edge conditions
  if (i > 7) return INITIALIZE_WORD(0);         //Checking for edge conditions
  
  return INITIALIZE_WORD((uint64_t)(0x8ul << (28 - 4 * i)) << 32);
}


inline __attribute__((__always_inline__)) word_t CLEAR(word_t input, int n) {
  
  //Checking for edge conditions
  if (n <= 0)
    return input;
  if (n > 8)
    return input;

  word_t result;
  uint32_t mask = 0x0fffffff >> (n * 4 - 4);
  result.ls4b = input.ls4b & mask;
  result.ms4b = input.ms4b & mask;
  return result;
}

inline __attribute__((__always_inline__)) uint64_t MASK(int n) {

  //Checking for edge conditions
  if (n < 0)
    return 0;
  if (n > 8)
    return 0;

  return ~0ull >> (64 - 8 * n);
}

inline __attribute__((__always_inline__)) word_t LOAD(const uint8_t* bytes, int n) {
  uint64_t x = *(uint64_t*)bytes & MASK(n);
  return U64TOWORD(U64BIG(x));
}


inline __attribute__((__always_inline__)) void STORE(uint8_t* bytes, word_t w, int n) {
  uint64_t x = WORDTOU64(w);
  *(uint64_t*)bytes &= ~MASK(n);
  *(uint64_t*)bytes |= U64BIG(x);
}

inline __attribute__((__always_inline__)) word_t LOADBYTES(const uint8_t* bytes, int n) {
  uint64_t x = 0;
  for (int i = 0; i < n; ++i) ((uint8_t*)&x)[7 - i] = bytes[i];
  return U64TOWORD(x);
}



inline __attribute__((__always_inline__)) void STOREBYTES(uint8_t* bytes, word_t w, int n) {
  uint64_t x = WORDTOU64(w);

  //Checking for edge conditions
  if (n > 8)
    return;

  for (int i = 0; i < n; ++i) bytes[i] = ((uint8_t*)&x)[7 - i];
}


















inline __attribute__((__always_inline__)) key_type KEY_INIT(){
  key_type key;
  key.ls8b = INITIALIZE_WORD(0);
  key.ms8b = INITIALIZE_WORD(0);
  return key;
}

inline __attribute__((__always_inline__)) state_t STATE_INIT(){
  state_t s;
  s.x0 = INITIALIZE_WORD(0);
  s.x1 = INITIALIZE_WORD(0);
  s.x2 = INITIALIZE_WORD(0);
  s.x3 = INITIALIZE_WORD(0);
  s.x4 = INITIALIZE_WORD(0);
  return s;
}









#endif /* WORD_H_ */
