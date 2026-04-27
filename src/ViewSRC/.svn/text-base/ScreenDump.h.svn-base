/*
 *  ScreenDump.h
 *  AMOSLib
 *
 *  Created by Luis Pons on Fri Dec 13 2002.
 *  Copyright (c) 2002 __MyCompanyName__. All rights reserved.
 *
 */

#ifndef _SCREEN_DUMP_H_
#define _SCREEN_DUMP_H_

enum
{
    OUT_NO,
    OUT_RGB888,
    OUT_RGB565,
    OUT_RGB555,    
};

typedef struct
{
    void *pSrcAddress;
    int   wSrcWidth;
    int   wSrcHeight;
    int   wSrcTags;
    //
    void *pDstAddress;
    int   wDstColorMode;
    int   wDstWidth;
    int   wDstHeight;
} SCREENDUMP_ARGS;

void  ScreenDump ( SCREENDUMP_ARGS *pArgs);

#endif // _SCREEN_DUMP_H_

