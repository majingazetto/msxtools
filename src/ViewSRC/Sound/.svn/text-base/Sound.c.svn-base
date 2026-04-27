/*
 *  Sound.c
 *  PlayerBase
 *
 *  Created by Luis Pons on Sat Jul 06 2002.
 *  Copyright (c) 2002 __MyCompanyName__. All rights reserved.
 *
 */

#include <stdio.h>
#include <stdlib.h>

#include "Sys.h"
#include "Common.h"

#include "Sound.h"
#include "ModPlayer.h"
#include "Mixer.h"

//#include <Sys.h>
//#include <SysDefs.h>

// -------------------------------------------------------------------------

void  SoundCallBack  (PWORD pSound, WORD wCurrSmp);

// -------------------------------------------------------------------------
// Publicas
// -------------------------------------------------------------------------

int Sound_Init  ()
{
    int rc = Sys_SoundInit ((PVOID) &SoundCallBack, 44100);
    fprintf(stderr,"Sound initialized at %d hz\n", Sound_GetFrequency());
    Mixer_Init  ( Sound_GetSamplesToMix ());
    TLOTB_InitPlayer ();	
    Sound_Start ();

    return rc;
}

// -------------------------------------------------------------------------

void Sound_End ()
{
    TLOTB_FinishPlayer ();
    Sound_Stop ();
    Sys_SoundEnd ();
    fprintf(stderr,"Sound terminated\n");
}

// -------------------------------------------------------------------------

void Sound_Start  ()
{
    Sys_SoundStart ();
}

// -------------------------------------------------------------------------

void Sound_Stop ()
{
    Sys_SoundStop ();
}

// -------------------------------------------------------------------------

int Sound_GetSamplesToMix ()
{
    return Sys_GetSamplesToMix ();
}

// -------------------------------------------------------------------------

int Sound_GetFrequency ()
{
    return Sys_GetFrequency ();
}

// -------------------------------------------------------------------------

void  SoundCallBack  ( PWORD pSound, WORD wCurrSmp)
{
    ControlChannels    ();

    //Sfx_AsyncService   (); // Sound effects
    Mixer_Process ( pSound, wCurrSmp);
}

// -------------------------------------------------------------------------

void Sound_CalcFrequencies ( long *pSound, int wCurrSmp, float *pFreqs)
{
/*
    int i;
    long wSamp = (wSampL + wSampR) >> 1;

    int wSamp 
    for ( i=wCurrSmp - wNumSamples; i<wCurrSmp; i++)
    {
        long wSampL = pSound [ i & 0xffff] >> 16;
        long wSampR = ( pSound [ i & 0xffff] << 16) >> 16;
        long wSamp = (wSampL + wSampR) >> 1;
    }
*/
}

