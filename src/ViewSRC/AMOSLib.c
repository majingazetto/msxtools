/*
 *  AMOSLib.c
 *  AMOSLib
 *
 *  Created by Luis Pons on Thu Dec 12 2002.
 *  Copyright (c) 2002 __MyCompanyName__. All rights reserved.
 *
 */

#include "SDL.h"
#include "AMOSLib.h"
#include "Sys.h"
#include "Screens.h"
#include "Files.h"
#include "Timer.h"
//#include "Sound/Sound.h"

// ---------------------------------------------------------------------------

int AMOSLibInit ()
{
    int blDone;
    blDone = SysInit ();
    if ( blDone == 1)
        ScreenInit ();
    if ( blDone == 1)
        FilesInit ();
    if ( blDone == 1)
        TimerInit ();
 //   if ( blDone == 1)
 //       blDone = Sound_Init ();
    return blDone;
}

// ---------------------------------------------------------------------------

void AMOSLibEnd ()
{
    //Sound_End ();
    SysEnd ();
}

// ---------------------------------------------------------------------------

// ---------------------------------------------------------------------------
