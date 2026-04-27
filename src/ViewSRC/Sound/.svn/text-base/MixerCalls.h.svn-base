
#ifndef _MIXER_CALLS_
#define _MIXER_CALLS_

typedef struct
{
    long    *pSoundBuffer;    // Puntero al buffer de audio final, 65536 samples stereo
    long     wCurrSmp;         // Posicion actual dentro de ese buffer
    long     wNumSamples;	   // Numero de samples a renderizar

    long     wChannels;		   // Numero de canales (no se usa)
    FIX8     fxReverb;		   // Nivel de reverberacion (0=desconectado) 
    long     wReverbDistance;
    FIX8	 fxFilter;		   // Filtro paso bajo, 0 = no deja pasar nada
                               // 0x100 = deja pasar todo (desconectado)
    unsigned long	*pMultiplyTable;
    CHANNEL_ARGS	Channel [MAX_CHANNELS];
} MIXER_ARGS;
typedef MIXER_ARGS * PMIXER_ARGS;

void  SysMixer_Init     ( PMIXER_ARGS pArgs);


void  SysMixer_Process  ( PMIXER_ARGS pArgs);

#endif //_MIXER_CALLS_
