/*
 *  AMOSLib.h
 *  AMOSLib
 *
 *  Created by Luis Pons on Sun Nov 24 2002.
 *  Copyright (c) 2002 __MyCompanyName__. All rights reserved.
 *
 */

#ifndef _AMOSLIB_H_
#define _AMOSLIB_H_

// General
// ---------------------------------------------------------------------------

int  AMOSLibInit ();
void AMOSLibEnd  ();

// Memory
// ---------------------------------------------------------------------------

void * Reserve       ( int wSize, const char *pReference);
void * ReserveAsFast ( int wSize, const char *pReference,
        int wAlignBits, int wPrefetchSize);
void   Free          ( void *pAddr);
int    GetAllocated  ();

#define DEFAULT_ALIGN     (6)   // 64 bytes
#define DEFAULT_PREFETCH  (256) // Area for secure prefetch   

// Files
// ---------------------------------------------------------------------------

void   SetDir      ( char *pDir);    // Set default working directory
void * BinLoad     ( char *pName);   // Load binary in fast reserve
void * BinLoadIn   ( char *pName, void *pAddr);  // Load binary address
int    BinSave     ( char *pName, void * pAddr, long wSize);  // Save binary
int    GetFileSize ( char *pName);
int    FileExist   ( char *pName);

// Input
// ---------------------------------------------------------------------------

int  MouseKey     ();
int  IsKeyPressed ( int wKeyCode);
int  GetMouseX    ();
int  GetMouseY    ();

// Timers
// ---------------------------------------------------------------------------

void    ResetTimer      ( int wTimer);
double  GetTimerCycles  ( int wTimer);
double  GetTimerSeconds ( int wTimer);


// Print
// ---------------------------------------------------------------------------

enum
{
    PRINTMODE_PLAIN,
    PRINTMODE_SHADOW,
    PRINTMODE_INVALID
};

void Locate  ( int wX, int wY);
void Ink     ( int wColor);
void Print   ( char * pszFormat, ...);
void PrintAt ( char *psCadena, int iX, int iY, int nColor);
void SetPrintMode ( int wMode);

// Screens
// ---------------------------------------------------------------------------

int   ScreenOpen      ( int wWidth, int wHeight, int wTags);
int   ScreenOpenNum   ( int wNum, int wWidth, int wHeight, int wTags);
int   ScreenOpenNext  ( int wWidth, int wHeight, int wTags);

void  ScreenClose     ();
void  ScreenCloseNum  ( int wNum);

void  ScreenSwap      ();
void  ScreenCopy      ( int wNumSrc, int wNumDst);

void  Screen             ( int wNum);
int   GetScreen          ();
int   GetScreenWidth     ();
int   GetScreenHeight    ();
void *GetScreenPixels    ();
int   GetScreenPixelSize ();

void *GetScreenPixelsNum ( int wNum);

// Screen Tags
// ---------------------------------------------------------------------------

#define MAX_SCREENS (32)

enum
{
    RGB555,
    RGB565,
    HSL637,
    YUV754,
    //
    RGB888,
    YUV888,
    HSL888,
    //
    LAST_COLOR_MODE
};

// Draw Primitives
// ---------------------------------------------------------------------------

enum
{
    DRAW_SOLID,
    DRAW_NEGATIVE,
    DRAW_XOR,
};

void  SetDrawMode ( int wMode);

void  Plot   ( int wX, int wY, unsigned int uwColor);
int   Pick   ( int wX, int wY);
void  Circle ( int wX, int wY, int wRad);
void  Line   ( int wX0, int wY0, int wX1, int wY1);

void  Cls    ( int uwColor);

// Load Picture
// ---------------------------------------------------------------------------

int  LoadPBM   ( char *pName);
int  LoadPBMIn ( char *pName, int wGfx);

int  SavePBM   ( char *pName);
int  SavePBMOf ( char *pName, int wGfx);

// Sound
// ---------------------------------------------------------------------------

void            ResetSoundClock ();
int             GetSoundClock   ();


#endif

