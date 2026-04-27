/*
 *  Memory.c
 *  AMOSLib
 *
 *  Created by Luis Pons on Sat Nov 30 2002.
 *  Copyright (c) 2002 __MyCompanyName__. All rights reserved.
 *
 */

#include <stdlib.h>
#include <assert.h>

#include <AMOSLib.h>

#include "Memory.h"

#define ALLOCATE_MARK  (0x01234567)

static long g_wTotalAlloc = 0;

// -------------------------------------------------------------------------

void * Reserve ( int wSize, const char *pReference)
{
    long   wRSize;	
    long * pAddr;
    wRSize = wSize + 16;
    pAddr = malloc ( wRSize);
    g_wTotalAlloc += wRSize;
    pAddr [0] = (long)pAddr;	 // Store a Header to free the allocation
    pAddr [1] = (long)wRSize;
    pAddr [2] = (long)pReference;  // Descriptive string
    pAddr [3] = (long)ALLOCATE_MARK;
    return pAddr + 4;
}

// -------------------------------------------------------------------------

void * ReserveAsFast ( int wSize, const char *pReference, 
                       int wAlignBits, int wPrefetchSize)
{
    long * pAddr, *pAddrAlign;
    unsigned long wAddr, wRSize;
    wRSize = ( wSize + 16) + ( 1 << wAlignBits) + (wPrefetchSize);
    
    pAddr = NULL;
    pAddr = malloc ( wRSize);
    if (!pAddr) {
        printf ("ERROR! Error allocating memory\n");
        exit (0);
    }

    g_wTotalAlloc += wRSize;
    wAddr = ( unsigned long) pAddr;
    wAddr += 16; // Header
    wAddr = (( wAddr + ((1 << wAlignBits) - 1)) >> wAlignBits) << wAlignBits;
    pAddrAlign = ( long *) wAddr;
    pAddrAlign [-4] = (long) pAddr;	// Store a Header to free the alloc
    pAddrAlign [-3] = (long) wRSize; // Descriptive string
    pAddrAlign [-2] = (long) pReference; // Descriptive string
    pAddrAlign [-1] = (long) ALLOCATE_MARK;
    
    return (void *) pAddrAlign;
}

// -------------------------------------------------------------------------

void  Free ( void *pAddr)
{
    unsigned long *pHead = ( long *) pAddr;
    
    if (pHead [ -1] != ALLOCATE_MARK)
        printf ("Invalid free! (%x)\n", (unsigned int)pAddr);
    else
    {
        g_wTotalAlloc -= pHead [ -3];
        free ((void *) pHead [ -4]);
    }
}

// -------------------------------------------------------------------------

int  GetAllocated  ()
{
    return g_wTotalAlloc;
}


