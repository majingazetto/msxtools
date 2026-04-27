
#ifndef _MIXER_
#define _MIXER_

// Numero maximo de canales soportados
#define  MAX_CHANNELS            (4)

// Tamanyo de la tabla de compresion (se incluye un canal mas para el 
// efecto de reverberacion)
#define  MAX_COMP_TABLE_SIZE     ((MAX_CHANNELS+1)*256)

// Bits de la frecuencia
#define  DECIMALS_STEP           (10)
// Bits del volumen
#define  DECIMALS_VOL            (7)

// Rangos, restricciones, configs del Mixer
// ----------------------------------------
// - Samples   -> max. 2 MB
// - Steps     -> siempre positivo, nunca negativo
// - Steps     -> Deben ser inferiores a la longitud del sample
//                En caso de tener un LOOP, inferiores a la longitud del loop
// - Cnt       -> Debe estar DENTRO del sample
// - Volumenes -> No deben superar 128 (1.00...)

typedef long FIX10;
typedef long FIX16;
typedef long FIX8;
typedef long FIX7;

typedef struct
{
    char*   pSample;          // Direccion del sample
    long    wSampleLen;		  // Longitud del sample
    long    wSampleLoopStart; // Si wSampleLoopStart ==  wSampleLen -> NO LOOP
    FIX10	fxSampleCnt;      // Se actualiza (contador de posicion en el sample)
    FIX10   fxSampleStep;	  // Incremento para el contador de posicion
                              // (DECIMALS_STEP) Si es 0 -> CANAL OFF
    FIX7    fxVolumeL;		  // Rango 0-0x80 volumen del canal izquierdo
    FIX7    fxVolumeR;		  // Rango 0-0x80 volumen del canal derecho 
} CHANNEL_ARGS;

// -------------------------------------

void  	Mixer_Init           ( int wSamples);
void    Mixer_End            ();

void  	Mixer_SetFilter      ( FIX8 fxFilter);

void  	Mixer_SetChannel     ( int wChannel,
                             char *pSample, int wLen, int wLoopStart,
                             FIX10 fxPos, FIX10 fxStep,
                             FIX7 wVolLeft, FIX7 wVolRight);

void	Mixer_SetChannelVolume (int wChannel, FIX7 WVolLeft, FIX7 wVolRight);
void	Mixer_SetChannelStep   (int wChannel, FIX10 fxStep);
void	Mixer_SetChannelSample (int wChannel, char* pSample, int wLen, int wLoopStart);
void	Mixer_SetChannelNote   (int wChannel, FIX10 fxPos, FIX10 fxStep);

void  	Mixer_ShutChannel    ( int wChannel);

void  	Mixer_CopySetChannel ( CHANNEL_ARGS *pArgs, int wChannel);
void  	Mixer_CopyGetChannel ( CHANNEL_ARGS *pArgs, int wChannel);

void	Mixer_Process        ( PWORD pSound, WORD wCurrSmp);

// Servicio al configurer

//VOID	Mixer_Config    ( FPVOID pObj, UINT wKeys);
//VOID	Mixer_GetInfo   ( CFPVOID pObj, PSTRZ pOut, UINT uiMaxLen);

#endif //_MIXER_
