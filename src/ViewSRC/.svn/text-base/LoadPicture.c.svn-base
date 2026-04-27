/*
 *  LoadPicture.c
 *  AMOSLib
 *
 *  Created by Luis Pons on Sun Dec 01 2002.
 *  Copyright (c) 2002 __MyCompanyName__. All rights reserved.
 *
 */

#include <stdio.h>
#include <stdlib.h>
#include <assert.h>
#include <AMOSLib.h>

#include "Memory.h"
#include "Files.h"
#include "Screens.h"
#include "LoadPicture.h"

// Defines, structs
// -------------------------------------------------------------------------

enum
{
    PNM_GRAY,
    PNM_RGB,
};

typedef struct
{
    int			   wColorType;
    int            wWidth;
    int            wHeight;
    unsigned char *pPixelData;
} PBMSPECS;


// Defines for BMP 

typedef struct tagBITMAPFILEHEADER 
{
	short	bfType;        // must be 'BM' 
	int		bfSize;        // size of the whole .bmp file
	short	bfReserved1;   // must be 0
	short   bfReserved2;   // must be 0
	int		bfOffBits;     
} BITMAPFILEHEADER;  


typedef struct tagBITMAPINFOHEADER
{
	int		biSize;            // size of the structure
	long	biWidth;           // image width
	long	biHeight;          // image height
	short   biPlanes;          // bitplanes
	short   biBitCount;         // resolution 
	int		biCompression;     // compression
	int		biSizeImage;       // size of the image
	long	biXPelsPerMeter;   // pixels per meter X
	long	biYPelsPerMeter;   // pixels per meter Y
	int		biClrUsed;         // colors used
	int		biClrImportant;    // important colors
} BITMAPINFOHEADER;  


typedef struct tagRGBTriplet
{
	unsigned char red;
	unsigned char green;
	unsigned char blue;
} RGBTriplet;


#define BI_RGB 0;
#define BYTE unsigned char


// -------------------------------------------------------------------------

int ReadLine ( const char *pIn, char * pOut, int wMax)
{
    int i, iRec = 0;
	while (( pIn [ iRec] != 0xa) && ( pIn [ iRec] != 0x20) && (iRec < wMax))
		iRec++;
    if ( iRec == ( wMax - 1))
        return 0;
	
    for ( i=0; i<iRec; i++)
        pOut [ i] = pIn [ i];
    pOut [ i] = 0;
	
    return iRec + 1;
}

int SkipLine ( const char *pIn, int wMax)
{
    int iRec = 0;
	while (( pIn [ iRec] != 0xa) && (iRec < wMax))
		iRec++;
    if ( iRec == ( wMax - 1))
        return 0;
	
    return iRec + 1;
}

// -------------------------------------------------------------------------

int  ReadPBMSpecs ( unsigned char *pPBM, int wSize, PBMSPECS *pSpecs)
{
    int iRec, iLen;
    char pTemp [16];
	
	if (( pPBM [ 0] != 'P') || ( pPBM [ 1] != '6'))
	{
        if (( pPBM [ 0] != 'P') || ( pPBM [ 1] != '5'))
        {
            printf ("Not a valid PBM/PNM\n");
            return 0;
        }
        else
            pSpecs->wColorType = PNM_GRAY;        
	}
    else
        pSpecs->wColorType = PNM_RGB;
	
    iRec = 0;
    iLen = ReadLine ( &pPBM [ iRec], pTemp, 16); // skip Header
    if ( iLen == 0) {printf ("PNM format error\n"); return 0;}
    iRec += iLen;
    
    if ( pPBM [ iRec] == 0x23)
    {
        iLen = SkipLine ( &pPBM [ iRec], wSize - iRec); // Skip Comment
        if ( iLen == 0) {printf ("PNM format error\n"); return 0;}
        iRec += iLen;
    }
    
    iLen = ReadLine ( &pPBM [ iRec], pTemp, 16); // Width
    if ( iLen == 0) {printf ("PNM format error\n"); return 0;}
    pSpecs->wWidth = atoi( pTemp);
    iRec += iLen;
	
    iLen = ReadLine ( &pPBM [ iRec], pTemp, 16);  // Height
    if ( iLen == 0) {printf ("PNM format error\n"); return 0;}
    pSpecs->wHeight = atoi( pTemp);
    iRec += iLen;
	
    iLen = ReadLine ( &pPBM [ iRec], pTemp, 16);  // skip range
    if ( iLen == 0) {printf ("PNM format error\n"); return 0;}
    iRec += iLen;
	
    if (( pSpecs->wWidth == 0) || ( pSpecs->wHeight == 0))
    {
        printf ("Image size invalid (%d - %d)\n", 
				pSpecs->wWidth, pSpecs->wHeight);
        return 0;
    }
    
    if ( pSpecs->wColorType == PNM_RGB)
    {
        if ((iRec + (pSpecs->wWidth * pSpecs->wHeight * 3)) > wSize) 
        {
            printf ("Truncated Image!\n");
            return 0;
        }
    }
    
    pSpecs->pPixelData = &pPBM [ iRec];
	
    return 1;
}

// -------------------------------------------------------------------------
// PUBLICAS
// -------------------------------------------------------------------------

int  LoadPBMIn ( char *pName, int wGfx)
{
    assert(0);
    return 0;
}

// -------------------------------------------------------------------------

int  LoadPBM ( char *pName)
{
    int            wSize, wGfx, wGfxOut;
    unsigned char *pPBM;
    PBMSPECS       Specs;
    int            x, y, wValidWidth;
    unsigned long *pDst;
    unsigned char *pSrc = NULL;
    
    pPBM = (unsigned char *) BinLoad ( pName);
    if ( pPBM == 0)
        return 0;
    wSize = GetFileSize ( pName);
	
    if ( ReadPBMSpecs ( pPBM, wSize, &Specs) == 0)
    {
        Free ( pPBM);
        return 0;
    }
	
    wGfxOut     = GetScreen ();
    wValidWidth = ( Specs.wWidth + 3) & 0xfffffffc;
    wGfx = ScreenOpenNext ( wValidWidth, Specs.wHeight, RGB888);
    
    pSrc = Specs.pPixelData;
    pDst = GetScreenPixels ( wGfx);
    for ( y=0; y<Specs.wHeight; y++)
    {
        for ( x=0; x<Specs.wWidth; x++)
        {
            if ( Specs.wColorType == PNM_RGB)
            {
                *pDst++ = (((int)(pSrc[0]))<<16) | 
				(((int)(pSrc[1]))<<8)  |
				((int)(pSrc[2]));
                pSrc += 3;
            }
            else
            {
                int wPix = *pSrc++;
                *pDst++ = (wPix<<16) | (wPix<<8)  | wPix;
            }
        }
        pDst += ( wValidWidth - Specs.wWidth);
    }
	
    ScreenCopy ( wGfx, wGfxOut);
    ScreenCloseNum ( wGfx);
    Screen ( wGfxOut);
    Free ( pPBM);
    
    return 1;
}

// -------------------------------------------------------------------------

int  SavePBM   ( char *pName)
{
    int wErr, i;
    int wGfx    = GetScreen ();
    int wWidth  = GetScreenWidth ();
    int wHeight = GetScreenHeight ();
    int wGfxOut = ScreenOpenNext ( wWidth, wHeight, RGB888);
    long *pPixels = GetScreenPixels (); // ...de GfxOut
    char *pDst, *pPBM  = Reserve ( (wWidth*wHeight*3)+100, "PBM save");
	
    ScreenCopy ( wGfx, wGfxOut);
    
    pDst = pPBM;
    pDst += sprintf (pDst,"P6\n%d\n%d\n255\n",wWidth, wHeight);
    for ( i=0; i<(wWidth*wHeight); i++)
    {
        *pDst++ = pPixels [ i] >> 16;
        *pDst++ = pPixels [ i] >> 8;
        *pDst++ = pPixels [ i];
    }
    
    wErr = BinSave ( pName, pPBM, (int)pDst - (int)pPBM);
    ScreenCloseNum ( wGfxOut);
    Free ( pPBM);
	
    Screen ( wGfx);
    return wErr;
}

// -------------------------------------------------------------------------

int  SavePBMOf ( char *pName, int wGfx)
{
    int wErr;
    int wOldGfx = GetScreen ();
    Screen ( wGfx);
    wErr = SavePBM ( pName);
    Screen ( wOldGfx);
    return wErr;
}


// -------- 




