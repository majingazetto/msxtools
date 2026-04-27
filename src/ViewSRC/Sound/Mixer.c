
#include <Common.h>
#include <Sound.h>
//#include <Sys.h>
//#include <SysDefs.h>
//#include <Configurer.h>
//#include <Input.h>
//#include <Str.h>
//#include <Chunky.h>
#include "../AMOSLib.h"

#include  "Mixer.h"
#include  "MixerCalls.h"
//#include  "Compressor.h"

// Defines y structs
// ------------------------------------------------------------------------

#define MIXER_IN_C
//#define INTERPOLACION_LINEAL_C
//#define REBERVERACION_CRUZADA_C

// Globales
// ------------------------------------------------------------------------

 MIXER_ARGS   g_MixerArgs;
static int          g_wSoundClock = 0;

// Prototipos
// ------------------------------------------------------------------------

void  Mixer_DrawTable  ( UINT uiRed, UINT uiGreen, UINT uiBlue);

// Mixer de N canales
// ------------------------------------------------------------------------

void  Mixer_Init  ( int wSamples)
{
    int i;

    g_MixerArgs.wNumSamples     = wSamples;
    g_MixerArgs.wChannels       = MAX_CHANNELS;
    g_MixerArgs.fxReverb        = 0x0;
    g_MixerArgs.wReverbDistance = 2000; // Medio buffer
    g_MixerArgs.fxFilter        = 0x100;

    for ( i=0; i<MAX_CHANNELS; i++)
        Mixer_ShutChannel ( i);

    SysMixer_Init ( &g_MixerArgs);

    //Configurer_Add ( 0, &Mixer_Config, &Mixer_GetInfo);
}

// ------------------------------------------------------------------------

void Mixer_End ()
{
}

// ------------------------------------------------------------------------

void  Mixer_SetFilter ( FIX8 fxFilter)
{
    ASSERT(fxFilter <= 0x100);
    g_MixerArgs.fxFilter = fxFilter;
}

// ------------------------------------------------------------------------

void  Mixer_SetChannel  ( int wChannel,
                          char *pSample, int wLen, int wLoopStart,
                          FIX10 fxPos, FIX10 fxStep,
                          FIX7 wVolLeft, FIX7 wVolRight)
{
    ASSERT((wChannel >= 0) && (wChannel < MAX_CHANNELS));

    g_MixerArgs.Channel [ wChannel].pSample          = pSample; 
    g_MixerArgs.Channel [ wChannel].wSampleLen       = wLen;	
    g_MixerArgs.Channel [ wChannel].wSampleLoopStart = wLoopStart; 
    g_MixerArgs.Channel [ wChannel].fxSampleCnt      = fxPos;
    g_MixerArgs.Channel [ wChannel].fxSampleStep     = fxStep; 
    g_MixerArgs.Channel [ wChannel].fxVolumeL        = wVolLeft; 
    g_MixerArgs.Channel [ wChannel].fxVolumeR        = wVolRight; 
}

// ------------------------------------------------------------------------

void  Mixer_ShutChannel  ( int wChannel)
{
    ASSERT((wChannel >= 0) && (wChannel < MAX_CHANNELS));
    g_MixerArgs.Channel [ wChannel].fxSampleStep = 0;
}

// ------------------------------------------------------------------------

void  Mixer_CopySetChannel ( CHANNEL_ARGS *pArgs, int wChannel)
{
    ASSERT((wChannel >= 0) && (wChannel < MAX_CHANNELS));
    g_MixerArgs.Channel [ wChannel] = *pArgs;
}

// ------------------------------------------------------------------------

void  Mixer_CopyGetChannel ( CHANNEL_ARGS *pArgs, int wChannel)
{
    ASSERT((wChannel >= 0) && (wChannel < MAX_CHANNELS));
    *pArgs = g_MixerArgs.Channel [ wChannel];
}

// ------------------------------------------------------------------------

void Mixer_SetChannelVolume ( int wChannel,FIX7 fxVolLeft,FIX7 fxVolRight)
{
    ASSERT((wChannel >= 0) && (wChannel < MAX_CHANNELS));
    g_MixerArgs.Channel [ wChannel].fxVolumeL        = fxVolLeft; 
    g_MixerArgs.Channel [ wChannel].fxVolumeR        = fxVolRight; 
}


void Mixer_SetChannelStep ( int wChannel,FIX10 fxStep)
{
    ASSERT((wChannel >= 0) && (wChannel < MAX_CHANNELS));
	g_MixerArgs.Channel [ wChannel].fxSampleStep     = fxStep; 
}

void Mixer_SetChannelSample ( int wChannel, char* pSample,int wLen,int wLoopStart)
{
    ASSERT((wChannel >= 0) && (wChannel < MAX_CHANNELS));
	g_MixerArgs.Channel [ wChannel].pSample          = pSample; 
    g_MixerArgs.Channel [ wChannel].wSampleLen       = wLen;	
    g_MixerArgs.Channel [ wChannel].wSampleLoopStart = wLoopStart; 
}

void Mixer_SetChannelNote ( int wChannel,FIX10 fxPos,FIX10 fxStep)
{
    ASSERT((wChannel >= 0) && (wChannel < MAX_CHANNELS));
    g_MixerArgs.Channel [ wChannel].fxSampleCnt  = fxPos;
    g_MixerArgs.Channel [ wChannel].fxSampleStep = fxStep; 
}

// ------------------------------------------------------------------------

void  Mixer_Process ( PWORD pSound, WORD wCurrSmp)
{
    g_wSoundClock++;
    g_MixerArgs.pSoundBuffer = pSound;
    g_MixerArgs.wCurrSmp     = wCurrSmp;
    SysMixer_Process ( &g_MixerArgs);
}

// ------------------------------------------------------------------------

void   ResetSoundClock ()
{
    g_wSoundClock = 0;
}

// ------------------------------------------------------------------------
int    GetSoundClock   ()
{
    return  g_wSoundClock;
}

// --------------------------------------------------------------------------
/*
VOID Mixer_Config ( FPVOID pObj, UINT wKeys)
{
    WORD i;
    BOOL blChangeComp = FALSE;
    
    if (( Mixer_bFlasher & 3) != 0)
        return;

    if ( Input_KeyPressed(KEY_UP))
    {
        Mixer_bConfigOpt--;
        if ( Mixer_bConfigOpt < 0)
            Mixer_bConfigOpt = 0;
    }
    if ( Input_KeyPressed(KEY_DOWN))
        Mixer_bConfigOpt++;
    Mixer_bConfigOpt %= 3;

    // ---

    switch ( Mixer_bConfigOpt)
    {
        case 0:
            if ( Input_KeyPressed(KEY_LEFT))
                g_MixerArgs.fxFilter = 0x80;
            if ( Input_KeyPressed(KEY_RIGHT))
                g_MixerArgs.fxFilter = 0x100;
            break;
        case 1:
        case 2:
            if ( Mixer_bConfigOpt == 1)
                i = Mixer_fxDivInit;
            else
                i = Mixer_fxDivEnd;

            if ( Input_KeyPressed(KEY_LEFT))
                i -= 4, blChangeComp = TRUE;
            if ( Input_KeyPressed(KEY_RIGHT))
                i += 4, blChangeComp = TRUE;
            if ( i < 0)
                i = 0;

            if ( Mixer_bConfigOpt == 1)
                Mixer_fxDivInit = i;
            else
                Mixer_fxDivEnd = i;
            
            break;
    }
    
    
    if ( blChangeComp == TRUE)
    {
        Mixer_SetCompress ( Mixer_fxDivInit, Mixer_fxDivEnd);
        Mixer_blCompressDraw = TRUE;
    }
}

// --------------------------------------------------------------------------

VOID Mixer_GetInfo (CFPVOID pObj, PSTRZ pOut, UINT uiMaxLen)
{
    WORD wFreq, i,j, k;
    wFreq = Sound_GetFrequency ();
    wFreq = (g_MixerArgs.fxFilter == 0x100) ? wFreq : wFreq>>1;
    i = g_MixerArgs.fxFilter;
    j = Mixer_fxDivInit;
    k = Mixer_fxDivEnd;
    if (( Mixer_bConfigOpt == 0) && (( Mixer_bFlasher & 1)== 0))
        i = 0x100;
    if (( Mixer_bConfigOpt == 1) && (( Mixer_bFlasher & 1)== 0))
        j = 0;
    if (( Mixer_bConfigOpt == 2) && (( Mixer_bFlasher & 1)== 0))
        k = 0;
    Str_SNPrintF( pOut, uiMaxLen, 
                  "CPU %d%% \nFreq. %d hz. \nFilter: %d \nStart div: 0x%3x \nEnd div: 0x%3x\n",
                  Sys_GetSoundCost (),
                  wFreq,
                  ((i == 0x100) ? 0 : 1), 
                  j, 
                  k);

    //if ( Mixer_blCompressDraw == TRUE)
    {
        Mixer_DrawTable ( 255, 255, 255);
        Mixer_blCompressDraw = FALSE;
    } 
    
    Mixer_bFlasher++;
}

// --------------------------------------------------------------------------

void Mixer_DrawTable (UINT uiRed, UINT uiGreen, UINT uiBlue)
{
    int i, wColor, wHeight, wModulo;
    signed char *pComp;
    unsigned char *pChunky;

    wColor  = Chunky_FindNearest ( uiRed, uiGreen, uiBlue);
    wHeight = Chunky_Height ();
    wModulo = Chunky_Stride ();
    pChunky = Chunky_Buffer ();
    pComp = g_MixerArgs.pCompressTable;
    for ( i=0; i < 120; i++)
    {
        int y;
        short *p;
        y = pComp [i*4];
        if ( y < 0)
            y = 0;
        if ( y > 127)
            y = 127;
        p = (short *)(int)(pChunky + ((wHeight - 1 - y) * wModulo) + (i*2));
        *p = wColor;
    }
}
*/
