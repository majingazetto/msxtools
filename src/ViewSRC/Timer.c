/*
 *  Timer.c
 *  AMOSLib
 *
 *  Created by Luis Pons on Sun Dec 01 2002.
 *  Copyright (c) 2002 __MyCompanyName__. All rights reserved.
 *
 */

#include <sys/types.h>
#include <sys/time.h>
#include <sys/wait.h>
#include <unistd.h>
//#include <mach/mach_time.h>

#include <AMOSLib.h>

#include "Timer.h"

#define  MAX_TIMERS    (128)

static double GetNanoseconds ();

// Globales
// --------------------------------------------------------------------------------

static double  g_pfTimersBase [ MAX_TIMERS];


// --------------------------------------------------------------------------------
// PUBLICO
// --------------------------------------------------------------------------------

void TimerInit ()
{
    int i;
    
    for ( i=0; i<MAX_TIMERS; i++)
        g_pfTimersBase [ i] = 0;
}

// --------------------------------------------------------------------------------

void  ResetTimer ( int wTimer)
{
    if ( wTimer >= MAX_TIMERS)
        return;
    
    g_pfTimersBase [ wTimer] = GetNanoseconds ();
}

// --------------------------------------------------------------------------------

double  GetTimerCycles ( int wTimer)
{
    double fCurrent = GetNanoseconds ();
    if ( wTimer >= MAX_TIMERS)
        return 0;
    // Por implementar; de momento se coge 450 Mhz
    return ((( fCurrent - g_pfTimersBase [ wTimer]) / 1000000000.0) * 1420000000.0);
}

// --------------------------------------------------------------------------------

double  GetTimerSeconds ( int wTimer)
{
    double fCurrent = GetNanoseconds ();
    if ( wTimer >= MAX_TIMERS)
        return 0;
    return (( fCurrent - g_pfTimersBase [ wTimer]) / 1000000000.0);
}

// --------------------------------------------------------------------------------
//  PRIVADO
// --------------------------------------------------------------------------------

static double clk2ns ( double clk)
{
//    mach_timebase_info_data_t mtb;
//    mach_timebase_info ( &mtb);
//    return (clk / (double)mtb.denom) * (double)mtb.numer;

    return (double) 0;
}

// --------------------------------------------------------------------------------

static double GetNanoseconds ()
{
    return (double) 0;
  //  return clk2ns (( double) mach_absolute_time());
}


