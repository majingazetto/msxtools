/*
 *  Input.c
 *  AMOSLib
 *
 *  Created by Luis Pons on Thu Dec 12 2002.
 *  Copyright (c) 2002 __MyCompanyName__. All rights reserved.
 *
 */

#include <AMOSLib.h>

#include "Sys.h"
#include "Input.h"

// ---------------------------------------------------------------------------

int  MouseKey  ()
{
    SYSINPUT *pInput;
    pInput = SysGetInput ();
    return pInput->bMouseKey;
}

// ---------------------------------------------------------------------------

int GetMouseX ()
{
    SYSINPUT *pInput;
    pInput = SysGetInput ();
    return pInput->hXMouse;
}

int GetMouseY ()
{
    SYSINPUT *pInput;
    pInput = SysGetInput ();
    return pInput->hYMouse;
}

// ---------------------------------------------------------------------------

int IsKeyPressed ( int wKeyCode)
{
    SYSINPUT     *pInput;
	int           wKeyPack = ( wKeyCode >> 5) & 0x3;
	int           wKeyBit  = wKeyCode & 0x1f;
	unsigned long uwBits  = 1 << wKeyBit;

    pInput = SysGetInput ();
 
	if (( pInput->puwKeyboard [ wKeyPack] & uwBits) != 0)
        return 1;
    else 
        return 0;
}

// ---------------------------------------------------------------------------
