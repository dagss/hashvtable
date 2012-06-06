#define D_COUNT 64

typedef struct {
  uint64_t id, id2, id3;
  void *funcptr;
} entry_t;

typedef struct {
  //  __m128i masks, shifts;
  uint64_t m1;
  uint64_t m2;
  uint64_t r1;
  uint64_t r2;
  uint64_t r3;
  uint16_t d[D_COUNT];
  entry_t fallback;
  entry_t funcs[64];
} table_t;
