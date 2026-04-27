
#include "Common.h"
#include "Sound.h"
//#include <Sys.h>
//#include <SysDefs.h>

#include "Mixer.h"
#include "MixerCalls.h"

#define INTERPOLACION_LINEAL_C
#define REBERVERACION_CRUZADA_C

// Globales
// ------------------------------------------------------------------------

// Mixer
// ------------------------------------------------------------------------

void  SysMixer_Init   ( PMIXER_ARGS pArgs)
{

}

// ------------------------------------------------------------------------

void  SysMixer_MixOneChannel ( CHANNEL_ARGS *pChan, long *pSound, int wCurrSmp, int wNumSamples)
{
    long  j;
    char *pSample = pChan->pSample;
    long   fxVolumeL = pChan->fxVolumeL;
    long   fxVolumeR = pChan->fxVolumeR;
    long   wSampleLen = pChan->wSampleLen;
    long   wSampleLoopStart = pChan->wSampleLoopStart;
    long   fxSampleCnt  = pChan->fxSampleCnt;
    long   fxSampleStep = pChan->fxSampleStep;

    for ( j=wCurrSmp; j < (wCurrSmp+wNumSamples); j++)
    {
        long  wAcuL, wAcuR;
        wAcuL = pSound [ j & 0xffff] >> 16;
        wAcuR = ( pSound [ j & 0xffff] << 16) >> 16;

        if ( fxSampleStep > 0)
        {
            long wSamp;
#ifdef INTERPOLACION_LINEAL_C
            wSamp  = pSample [( fxSampleCnt >> DECIMALS_STEP) + 1];
            wSamp  = wSamp - pSample [ fxSampleCnt >> DECIMALS_STEP];
            wSamp  = (wSamp * ( fxSampleCnt & ((1 << DECIMALS_STEP) - 1))) >> DECIMALS_STEP;
            wSamp += pSample [ fxSampleCnt >> DECIMALS_STEP];
#else
            wSamp = pSample [ fxSampleCnt >> DECIMALS_STEP];
#endif
            wAcuL += (( wSamp * fxVolumeL) >> 2);
            wAcuR += (( wSamp * fxVolumeR) >> 2);
            fxSampleCnt += fxSampleStep;
            if (( fxSampleCnt >> DECIMALS_STEP) >= wSampleLen)
            {
                if ( wSampleLen == wSampleLoopStart)
                    fxSampleStep = 0;  // No hay LOOP; Desconectar canal
                else
                    fxSampleCnt -= (wSampleLen - wSampleLoopStart) << DECIMALS_STEP;
            }
        }

        pSound [ j & 0xffff] = (wAcuL << 16) | ( wAcuR & 0xffff);
    }

    pChan->fxSampleCnt  = fxSampleCnt;
    pChan->fxSampleStep = fxSampleStep;
}

// ------------------------------------------------------------------------

void  SysMixer_Process ( PMIXER_ARGS pMixerArgs)
{
    long  i, j, wNumSamples;
    long  wAcuL, wAcuR;
    long *pSound;
    int   wCurrSmp;
    
    wNumSamples = pMixerArgs->wNumSamples;
    pSound      = pMixerArgs->pSoundBuffer;
    wCurrSmp    = pMixerArgs->wCurrSmp;
    
    // PREVIO
    if ( pMixerArgs->fxReverb > 0)
    {
        long fxReverb = pMixerArgs->fxReverb;
        for ( i=wCurrSmp - pMixerArgs->wReverbDistance; 
              i<(wCurrSmp - pMixerArgs->wReverbDistance + wNumSamples); i++)
        {
            long wSampL = pSound [ i & 0xffff] >> 16;
            long wSampR = ( pSound [ i & 0xffff] << 16) >> 16;
#ifdef REBERVERACION_CRUZADA_C
            wAcuR = ( wSampL * fxReverb) >> DECIMALS_VOL;
            wAcuL = ( wSampR * fxReverb) >> DECIMALS_VOL;
#else
            wAcuL = ( wSampL * fxReverb) >> DECIMALS_VOL;
            wAcuR = ( wSampR * fxReverb) >> DECIMALS_VOL;
#endif
            pSound [ i & 0xffff] = (wAcuL << 16) | ( wAcuR & 0xffff);
        }
    }
    else
    {
        for ( i=wCurrSmp; i<(wCurrSmp+wNumSamples); i++)
            pSound [ i & 0xffff] = 0;
    }

    // MEZCLA
    for ( j = 0; j < pMixerArgs->wChannels; j++)
        SysMixer_MixOneChannel ( &pMixerArgs->Channel[j], pSound, wCurrSmp, wNumSamples);

    // FILTRO
    if ( pMixerArgs->fxFilter != 0x100)
    {
        long  fxFilter = pMixerArgs->fxFilter;
        long  wAcuLOld = pSound [( wCurrSmp - 1) & 0xffff] >> 16;
        long  wAcuROld = ( pSound [(wCurrSmp - 1) & 0xffff] << 16) >> 16;
        for ( i=wCurrSmp; i < (wCurrSmp+wNumSamples); i++)
        {
            long  wAcuL, wAcuR;
            wAcuL = pSound [ i & 0xffff] >> 16;
            wAcuR = ( pSound [ i & 0xffff] << 16) >> 16;
            wAcuL = wAcuLOld + (((wAcuL - wAcuLOld) * fxFilter) >> 8);
            wAcuR = wAcuROld + (((wAcuR - wAcuROld) * fxFilter) >> 8);
            pSound [ i & 0xffff] = (wAcuL << 16) | ( wAcuR & 0xffff);
            wAcuLOld = wAcuL;
            wAcuROld = wAcuR;
        }
    }
}

