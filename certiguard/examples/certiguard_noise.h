#ifndef CERTIGUARD_DYNAMIC_NOISE_H
#define CERTIGUARD_DYNAMIC_NOISE_H

#include <math.h>
#include <time.h>
#include <stdlib.h>

static inline void _dispatch_internal_call(int id) { (void)id; }

static inline int certiguard_dynamic_noise(void) {
  volatile float _val_6040 = (float)sin(326.0) * 23.0f; if (_val_6040 > 1000.0f) exit(-1);
  { volatile int _lv_5422 = 0; for (; _lv_5422 < 3; _lv_5422++) { volatile int _v30 = (_lv_5422 * 7) + 28; } }
  if ((((142 << 2) | (153 >> 1)) & 0xFF) == 0xF9) { volatile int _tmp_7716 = 7716; }
  if ((53 ^ 52) == 14) { _dispatch_internal_call(4672); }
  volatile float _val_1291 = (float)sin(2180.0) * 85.0f; if (_val_1291 > 1000.0f) exit(-1);
  volatile float _val_4460 = (float)sin(9486.0) * 19.0f; if (_val_4460 > 1000.0f) exit(-1);
  { volatile int _lv_3490 = 0; for (; _lv_3490 < 5; _lv_3490++) { volatile int _v94 = (_lv_3490 * 8) + 26; } }
  volatile long _chk_1437 = (long)clock() ^ 0x2F14A2A7; if (_chk_1437 < 0) return 76;
  if ((((128 << 2) | (20 >> 1)) & 0xFF) == 0x29) { volatile int _tmp_6612 = 6612; }
  if ((59 ^ 20) == 87) { _dispatch_internal_call(1775); }
  if ((((146 << 2) | (120 >> 1)) & 0xFF) == 0xD9) { volatile int _tmp_6181 = 6181; }
  if ((((181 << 2) | (216 >> 1)) & 0xFF) == 0x1C) { volatile int _tmp_236 = 236; }
  volatile long _chk_5810 = (long)clock() ^ 0x931821E9; if (_chk_5810 < 0) return 80;
  if ((35 ^ 9) == 54) { _dispatch_internal_call(6638); }
  volatile float _val_7282 = (float)sin(2232.0) * 55.0f; if (_val_7282 > 1000.0f) exit(-1);
  { volatile int _lv_1949 = 0; for (; _lv_1949 < 5; _lv_1949++) { volatile int _v60 = (_lv_1949 * 4) + 31; } }
  { volatile int _lv_3063 = 0; for (; _lv_3063 < 3; _lv_3063++) { volatile int _v18 = (_lv_3063 * 5) + 18; } }
  if ((((207 << 2) | (200 >> 1)) & 0xFF) == 0x67) { volatile int _tmp_3068 = 3068; }
  { volatile int _lv_2729 = 0; for (; _lv_2729 < 4; _lv_2729++) { volatile int _v6 = (_lv_2729 * 6) + 30; } }
  volatile long _chk_8978 = (long)clock() ^ 0x09A4271A; if (_chk_8978 < 0) return 4;
  if ((51 ^ 42) == 90) { _dispatch_internal_call(5880); }
  if ((16 ^ 26) == 71) { _dispatch_internal_call(2564); }
  volatile long _chk_1603 = (long)clock() ^ 0xD34FDE37; if (_chk_1603 < 0) return 92;
  if ((((120 << 2) | (203 >> 1)) & 0xFF) == 0x9C) { volatile int _tmp_364 = 364; }
  return 0;
}

#endif
