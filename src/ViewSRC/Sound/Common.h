/* Todos los .c deben incluir este fichero ANTES que ningun otro */

#define _FROM_COMMON_H_
#include <assert.h>
#include "CTypes.h"
#undef _FROM_COMMON_H_

#if defined(NDEBUG)
#define ASSERT(exp)
#else
extern void __Assert () __attribute__ ((noreturn)); 
#define ASSERT(expression) assert(#expression)
#endif // defined(NDEBUG)


