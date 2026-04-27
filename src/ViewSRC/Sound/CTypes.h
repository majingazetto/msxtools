#if !defined(_FROM_COMMON_H_)
#error Este fichero solo debe incluirse desde Common.h
#endif


/* ---------------------------------------------------------- */
/* Tipos propios                                              */
/*                                                            */
/* ---------------------------------------------------------- */

#ifndef _BM_TYPES_
#define _BM_TYPES_

#ifndef FALSE
#define FALSE  (0)
#endif
#ifndef TRUE
#define TRUE   (1)
#endif

#ifndef NULL
#define NULL   (0)
#endif

// TIPOS


typedef signed char    BYTE;		// bVar
typedef unsigned char  UBYTE;		// ubVar
typedef signed short   HALF;		// hVar
typedef unsigned short UHALF;		// uhVar
typedef signed long    WORD;		// wVar
typedef unsigned long  UWORD;		// uwVar
typedef signed int     INT;		// iVar
typedef unsigned int   UINT;		// uiVar
typedef char           STRZ;		// szVar
typedef void           VOID;		// Var
typedef signed char    SHORTBOOL;	// blVar
typedef signed int     BOOL;		// blVar
typedef float          FLOAT;		// fVar
typedef double         DOUBLE;		// dVar
typedef signed long    FIXED24_8;	// fx
typedef unsigned long  UFIXED24_8;	// ufx
typedef signed long    FIXED16_16;	// fx
typedef unsigned long  UFIXED16_16;	// ufx
typedef signed long    FIXED8_24;	// fx
typedef unsigned long  UFIXED8_24;	// ufx

// PUNTEROS
// puntero a RABANO:                  PRABANO
// puntero a RABANO constante:        CPRABANO
// puntero a RABANO fijo:             FPRABANO
// puntero a RABANO fijo y constante: CFPRABANO

#define DEFPTRS(a) \
typedef a * P##a; \
typedef const a * CP##a; \
typedef a * const FP##a; \
typedef const a * const CFP##a

DEFPTRS(STRZ);
DEFPTRS(BYTE);
DEFPTRS(UBYTE);
DEFPTRS(HALF);
DEFPTRS(UHALF);
DEFPTRS(WORD);
DEFPTRS(UWORD);
DEFPTRS(INT);
DEFPTRS(UINT);
DEFPTRS(VOID);
DEFPTRS(SHORTBOOL);
DEFPTRS(BOOL);
DEFPTRS(FLOAT);
DEFPTRS(DOUBLE);
DEFPTRS(FIXED24_8);
DEFPTRS(UFIXED24_8);
DEFPTRS(FIXED16_16);
DEFPTRS(UFIXED16_16);
DEFPTRS(FIXED8_24);
DEFPTRS(UFIXED8_24);


// PUNTEROS A FUNCION
// ------------------

//  Variable
//WORD (*pGDBCommand)(WORD, WORD, WORD);
//pGDBCommand = miFunc;

// Tipo
//typedef WORD   (* PGDB_COMMAND) ( WORD wCommand, WORD wArg0, WORD wArg1);
// Se usa...
//PGDB_COMMAND pGDBCommand;
//pGDBCommand = miFunc;
//x = pGDBCommand ( 1,2,3);


// TABULADORES
// -----------

// 4 chars

// INDENTADO
// -----------

//  if ( kk)
//  {
//    printf();
//  }
//  else
//    printf();
    
// ESTRUCTURA
// ----------

// Usar mayusculas para los nombres
//@MELON
//{
//  WORD wMelones;
//  HALF hCostePorMelon;
//};

// MACROS
// ------

//#define ABS(x)  (((x)<0)? -(x) : (x))

// preferible a las macros:
// static inline float fAbs ( float x) { return ((x<0)? -x : x)};

// FUNCIONES
// ---------

// Modulo.c

// Publicas

//VOID Modulo_Init ();
//VOID Modulo_End  ();
// ...y se incluyen en el Modulo.h

// Privadas

// ...Al gusto, PERO con "static" delante
// Se declaran prototipos al principio de Modulo.c

// DATOS
// -----

// - Globales publica:

//   WORD Modulo_wContadorBalas;
//   y en el Modulo.h
//   extern WORD Modulo_wContadorBalas;
    
// - Globales privadas (modulo):

//   static WORD g_wContadorBalas;

// ASSERTS
// -------
//
// ASSERT(a >= 0 && "A es negativo");

#endif // _BM_TYPES_
