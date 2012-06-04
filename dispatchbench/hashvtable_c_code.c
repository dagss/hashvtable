#include <xmmintrin.h>
#include <stdint.h>

#define likely(x)   __builtin_expect(!!(x), 1)
#define unlikely(x) __builtin_expect(!!(x), 0)


typedef struct {
  uint64_t id;
  void *funcptr;
} entry_t;

typedef union {
  struct {
    uint64_t x, y;
  };
  __m128i v;
} u64_v2;

uint64_t the_id;
uint64_t h;


typedef struct {
  __m128i masks, shifts;
  uint64_t m1;
  uint64_t m2;
  uint64_t r1;
  uint64_t r2;
  uint64_t r3;
  entry_t funcs[64];
} table_t;


double table_lookup_first_element(double value, table_t *table, uint64_t k) {
  double (*func)(double);
  if (unlikely(table->funcs[0].id != the_id)) return 0;
  func = table->funcs[0].funcptr;
  return func(value);
}

double zero_table_lookup(double value, table_t *table, uint64_t k) {
  uint64_t slot = h & table->m1;
  double (*func)(double);
  if (unlikely(table->funcs[slot].id != the_id)) return 0;
  func = table->funcs[slot].funcptr;
  return func(value);
}

double one_table_lookup(double value, table_t *table, uint64_t k) {
  uint64_t slot = (h >> table->r1) & table->m1;
  double (*func)(double);
  if (unlikely(table->funcs[slot].id != the_id)) return 0;
  func = table->funcs[slot].funcptr;
  return func(value);
}

double two_table_lookup(double value, table_t *table, uint64_t k) {
  uint64_t slot = ((h >> table->r1) ^ (h >> table->r2)) & table->m1;
  double (*func)(double);
  if (unlikely(table->funcs[slot].id != the_id)) return 0;
  func = table->funcs[slot].funcptr;
  return func(value);
}

double three_table_lookup(double value, table_t *table, uint64_t k) {
  uint64_t slot = ((h >> table->r1) ^ (h >> table->r2) ^ (h >> table->r3)) & table->m1;
  double (*func)(double);
  if (unlikely(table->funcs[slot].id != the_id)) return 0;
  func = table->funcs[slot].funcptr;
  return func(value);
}

double twohalf_table_lookup(double value, table_t *table, uint64_t k) {
  uint64_t slot = ((h >> table->r1) ^ (h >> table->r2) ^ h) & table->m1;
  double (*func)(double);
  if (unlikely(table->funcs[slot].id != the_id)) return 0;
  func = table->funcs[slot].funcptr;
  return func(value);
}

double doublemask(double value, table_t *table, uint64_t k) {
  uint64_t slot = (((h >> table->r1) & table->m1) ^ 
                   ((h >> table->r2) & table->m2));
  double (*func)(double);
  if (unlikely(table->funcs[slot].id != the_id)) return 0;
  func = table->funcs[slot].funcptr;
  return func(value);
}

double doublemask2(double value, table_t *table, uint64_t k) {
  uint64_t slot = (((h >> table->r1) & table->m1) ^ 
                   ((h & table->m2) >> table->r2));
  double (*func)(double);
  if (unlikely(table->funcs[slot].id != the_id)) return 0;
  func = table->funcs[slot].funcptr;
  return func(value);
}

double doublemask_sse(double value, table_t *table, uint64_t k) {
  u64_v2 x;
  __m128i hvec, hvec_shuf, maskvec, shiftvec;

  x.x = x.y = h;
  hvec = x.v;

  shiftvec = _mm_load_si128(&table->shifts);
  maskvec = _mm_load_si128(&table->masks);

  hvec = _mm_srl_epi64(hvec, shiftvec);
  hvec = _mm_and_si128(hvec, maskvec);
  hvec_shuf = _mm_unpackhi_epi64(hvec, hvec);
  hvec = _mm_xor_si128(hvec, hvec_shuf);


  double (*func)(double);
  func = table->funcs[((u64_v2)(hvec)).x].funcptr;
  return func(value);
}

