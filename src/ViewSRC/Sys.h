/*
 *  Sys.h
 *  AMOSLib
 *
 *  Created by Luis Pons on Thu Dec 12 2002.
 *  Copyright (c) 2002 __MyCompanyName__. All rights reserved.
 *
 */

#ifndef _SYS_H_
#define _SYS_H_

typedef struct
{
    unsigned long puwKeyboard [8];
    char  bMouseKey;
    short hXMouse;
    short hYMouse;

} SYSINPUT;

int   SysInit ();
void  SysEnd  ();

SYSINPUT * SysGetInput       ();

int  SysScreenOpenRGB888     ( int wSizeX, int wSizeY);
int  SysScreenOpenRGB565     ( int wSizeX, int wSizeY);
int  SysScreenOpenRGB555     ( int wSizeX, int wSizeY);

int  SysGetScreenInfoAndLock ( int *pwWidth, int *pwHeight, void **ppPixels);
void SysFlipScreenAndUnlock  ();

typedef void  (* PAUDIO_CALLBACK)  (long *pSound, long wCurrSmp);

int Sys_SoundInit       (void *pAudioCall, int uiFrequency);
void Sys_SoundEnd       ();
void Sys_SoundStart     ();
void Sys_SoundStop      ();
int Sys_GetSamplesToMix ();
int Sys_GetFrequency    ();
int Sys_GetSoundCost    ();


#endif // _SYS_H

