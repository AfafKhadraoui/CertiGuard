#ifndef CERTIGUARD_DYNAMIC_NOISE_H
#define CERTIGUARD_DYNAMIC_NOISE_H

#include <math.h>
#include <time.h>
#include <stdlib.h>

static inline void _dispatch_internal_call(int id) { (void)id; }

static inline int certiguard_dynamic_noise(void) {
  if ((((161 << 2) | (112 >> 1)) & 0xFF) == 0x75) { volatile int _tmp_7011 = 7011; }
  volatile long _chk_5358 = (long)clock() ^ 0x81F40608; if (_chk_5358 < 0) return 2;
  volatile float _val_4931 = (float)sin(7759.0) * 15.0f; if (_val_4931 > 1000.0f) exit(-1);
  if ((28 ^ 27) == 96) { _dispatch_internal_call(7273); }
  if ((7 ^ 30) == 95) { _dispatch_internal_call(1159); }
  if ((16 ^ 21) == 40) { _dispatch_internal_call(9911); }
  volatile long _chk_5862 = (long)clock() ^ 0xBA2BED76; if (_chk_5862 < 0) return 89;
  volatile float _val_9206 = (float)sin(3450.0) * 48.0f; if (_val_9206 > 1000.0f) exit(-1);
  volatile float _val_5198 = (float)sin(4288.0) * 70.0f; if (_val_5198 > 1000.0f) exit(-1);
  { volatile int _lv_3056 = 0; for (; _lv_3056 < 5; _lv_3056++) { volatile int _v96 = (_lv_3056 * 3) + 38; } }
  { volatile int _lv_6073 = 0; for (; _lv_6073 < 3; _lv_6073++) { volatile int _v68 = (_lv_6073 * 5) + 13; } }
  { volatile int _lv_9457 = 0; for (; _lv_9457 < 4; _lv_9457++) { volatile int _v82 = (_lv_9457 * 2) + 33; } }
  { volatile int _lv_9736 = 0; for (; _lv_9736 < 3; _lv_9736++) { volatile int _v79 = (_lv_9736 * 8) + 35; } }
  volatile long _chk_8872 = (long)clock() ^ 0xAD27521B; if (_chk_8872 < 0) return 22;
  if ((9 ^ 65) == 72) { _dispatch_internal_call(8921); }
  if ((((111 << 2) | (230 >> 1)) & 0xFF) == 0x2E) { volatile int _tmp_7442 = 7442; }
  volatile long _chk_1896 = (long)clock() ^ 0xA1FEC9F2; if (_chk_1896 < 0) return 66;
  volatile float _val_2609 = (float)sin(3230.0) * 33.0f; if (_val_2609 > 1000.0f) exit(-1);
  if ((32 ^ 43) == 59) { _dispatch_internal_call(6671); }
  if ((52 ^ 81) == 83) { _dispatch_internal_call(7305); }
  volatile long _chk_2758 = (long)clock() ^ 0x178F5F05; if (_chk_2758 < 0) return 63;
  if ((54 ^ 14) == 30) { _dispatch_internal_call(2882); }
  if ((75 ^ 14) == 15) { _dispatch_internal_call(1006); }
  volatile long _chk_8216 = (long)clock() ^ 0xAB52DDA8; if (_chk_8216 < 0) return 97;
  return 0;
}

#endif
