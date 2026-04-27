/*
 *  SysMacOSX.c
 *  AMOSLib
 *
 *  Created by Luis Pons on Thu Dec 12 2002.
 *  Copyright (c) 2002 __MyCompanyName__. All rights reserved.
 *
 */
   
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <math.h>
#include <assert.h>
#include <SDL.h>

#include "Sys.h"

#define ASSERT assert

// ---------------------------------------------------------------------------

static  SDL_Surface   *g_SDLSrf;
static  SYSINPUT       g_Input;
static  int            g_wBytesPerPixel;

// ---------------------------------------------------------------------------

#define SDL_SETTINGS  (SDL_INIT_VIDEO | SDL_INIT_AUDIO /*| SDL_INIT_NOPARACHUTE*/)

static void KeyReport ( int wKeyCode, int wPress);

// ---------------------------------------------------------------------------

int SysInit ()
{
	// Initialize the SDL library
	if ( SDL_Init ( SDL_SETTINGS) < 0)
    {
		printf ( "Couldn't initialize SDL: %s\n", SDL_GetError());
		return  0;
	}
    
    return 1;
}

// ---------------------------------------------------------------------------

SYSINPUT * SysGetInput ()
{
    SDL_Event ev;

    while ( SDL_PollEvent ( &ev)) 
    {
        switch ( ev.type) 
        {
            case SDL_MOUSEBUTTONDOWN:
                g_Input.bMouseKey = 1;
                break;

            case SDL_MOUSEBUTTONUP:
                g_Input.bMouseKey = 0;
                break;

            //case SDL_QUIT:
            //    break;
  
            case SDL_KEYDOWN:
                KeyReport (((SDL_KeyboardEvent *)&ev)->keysym.sym, 1);
                break;
        
            case SDL_KEYUP:			
                KeyReport (((SDL_KeyboardEvent *)&ev)->keysym.sym, 0);
                break;
  
            case SDL_MOUSEMOTION:
                g_Input.hXMouse = ((SDL_MouseMotionEvent *)&ev)->x;
                g_Input.hYMouse = ((SDL_MouseMotionEvent *)&ev)->y;
                break;
  
            default:
                break;
        }
    }
    
    return &g_Input;
}

// ---------------------------------------------------------------------------

void SysEnd ()
{
	SDL_Quit ();
}


// ---------------------------------------------------------------------------

//#define SDL_SCREEN_SETTINGS   (SDL_FULLSCREEN | SDL_HWSURFACE | SDL_DOUBLEBUF)
#define SDL_SCREEN_SETTINGS   0

int SysScreenOpen ( int wSizeX, int wSizeY, int wBits)
{
    SDL_PixelFormat *pFormat;
    SDL_Surface     *pSurface;
    if ( wBits == 15)
        wBits = 16;
    pSurface = SDL_SetVideoMode ( wSizeX, wSizeY, 
    wBits,
    SDL_SCREEN_SETTINGS);
    if ( pSurface == 0)
    {
        //printf("Couldn't set %dx%dx32 video mode: %s\n", wSizeX, wSizeY, SDL_GetError());
        return 0;
    }
    pFormat = pSurface->format;
    fprintf ( stderr, "Bpp %d, ShiftR %d, ShiftG %d, ShiftB %d\n", 
              pFormat->BitsPerPixel,
              pFormat->Rloss,
              pFormat->Gloss,
              pFormat->Bloss);
    g_wBytesPerPixel = pFormat->BitsPerPixel / 8;
    return 1;
}

int SysScreenOpenRGB888 ( int wSizeX, int wSizeY)
{
    return SysScreenOpen ( wSizeX, wSizeY, 32);
}

int SysScreenOpenRGB565 ( int wSizeX, int wSizeY)
{
    return SysScreenOpen ( wSizeX, wSizeY, 16);
}

int SysScreenOpenRGB555 ( int wSizeX, int wSizeY)
{
    return SysScreenOpen ( wSizeX, wSizeY, 15);
}
// ---------------------------------------------------------------------------

int SysGetScreenInfoAndLock ( int *pwWidth, int *pwHeight, void **ppPixels)
{
    g_SDLSrf = SDL_GetVideoSurface();
    if ( SDL_LockSurface ( g_SDLSrf) == 0)
    {
        *pwWidth  = g_SDLSrf->pitch / g_wBytesPerPixel;
        *pwHeight = g_SDLSrf->h;
        *ppPixels = (void *) g_SDLSrf->pixels;
    }
    else
        return 0;
    return 1;
}

// ---------------------------------------------------------------------------

void SysFlipScreenAndUnlock ()
{
    SDL_UnlockSurface ( g_SDLSrf);
    SDL_Flip          ( g_SDLSrf);
}


// ---------------------------------------------------------------------------
//  PRIVADO
// ---------------------------------------------------------------------------

static void KeyReport ( int wKeyCode, int wPress)
{
	int           wKeyPack = ( wKeyCode >> 5) & 0x3;
	int           wKeyBit  = wKeyCode & 0x1f;
	unsigned long uwBits  = 1 << wKeyBit;

	if ( wPress == 0)
		g_Input.puwKeyboard [ wKeyPack] &= (~uwBits);
	else
		g_Input.puwKeyboard [ wKeyPack] |= uwBits;
}
