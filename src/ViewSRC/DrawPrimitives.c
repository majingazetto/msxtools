/*
 *  DrawPrimitives.c
 *  AMOSLib
 *
 *  Created by Luis Pons on Sun Dec 01 2002.
 *  Copyright (c) 2002 __MyCompanyName__. All rights reserved.
 *
 */

#include <math.h>

#include <AMOSLib.h>

#include "DrawPrimitives.h"

extern int g_wColor;
static int g_wDrawMode   = DRAW_SOLID;

static void ValidSegmentX ( int *pwXi, int *pwXf);
static void ValidSegmentY ( int *pwYi, int *pwYf);

// ---------------------------------------------------------------------------

void  SetDrawMode ( int wMode)
{
    if (( wMode >= 0) && ( wMode <= DRAW_XOR))
        g_wDrawMode = wMode;
}

// ---------------------------------------------------------------------------

void Cls  ( int uwColor)
{
    int  i;
    int   wPix    = GetScreenPixelSize ();
    int   wWidth  = GetScreenWidth     ();
    int   wHeight = GetScreenHeight    ();
    int  *pTrg    = (int *) GetScreenPixels    ();
    if  ( wPix == 2)
        uwColor = (uwColor & 0xffff) | ( uwColor << 16);
    for ( i=0; i<((wWidth*wHeight*wPix)/4); i++)
       *pTrg++ = uwColor;
}

// ---------------------------------------------------------------------------

void  Plot   ( int wX, int wY, unsigned int uwColor)
{
    short *pP2;
    long  *pP4;
    long   wBack;

    int   wPix    = GetScreenPixelSize ();
    int   wWidth  = GetScreenWidth     ();
    int   wHeight = GetScreenHeight    ();
    void *pTrg    = GetScreenPixels    ();
    
    if (( wX < 0) || ( wY < 0))
        return;
    if (( wX > (wWidth-1)) || ( wY > (wHeight-1)))
        return;

    pP2 = (short *)pTrg;
    pP4 = (long *)pTrg;
    switch ( wPix)
    {
        case 2:
            wBack = pP2 [ wY * wWidth + wX];
            break;
        case 4:
            wBack = pP4 [ wY * wWidth + wX];
            break;
    }

    switch ( g_wDrawMode)
    {
        case DRAW_SOLID:
            break;
        case DRAW_NEGATIVE:
            uwColor = ~wBack;
            break;
        case DRAW_XOR:
            uwColor = uwColor ^ wBack;
            break;
    }

    switch ( wPix)
    {
        case 2:
            pP2 [ wY * wWidth + wX] = uwColor;
            break;
        case 4:
            pP4 [ wY * wWidth + wX] = uwColor;
            break;
    }
}

// ---------------------------------------------------------------------------

int   Pick   ( int wX, int wY)
{
    short *pP2;
    long  *pP4;
    long   wBack;

    int   wPix    = GetScreenPixelSize ();
    int   wWidth  = GetScreenWidth     ();
    int   wHeight = GetScreenHeight    ();
    void *pTrg    = GetScreenPixels    ();
    
    if (( wX < 0) || ( wY < 0))
        return 0;
    if (( wX > (wWidth-1)) || ( wY > (wHeight-1)))
        return 0;

    pP2 = (short *)pTrg;
    pP4 = (long *)pTrg;
    switch ( wPix)
    {
        case 2:
            wBack = pP2 [ wY * wWidth + wX];
            break;
        case 4:
            wBack = pP4 [ wY * wWidth + wX];
            break;
    }
    switch ( wPix)
    {
        case 2:
            return pP2 [ wY * wWidth + wX];
            break;
        case 4:
            return pP4 [ wY * wWidth + wX];
            break;
    }
}

// ---------------------------------------------------------------------------

void  Circle ( int wX, int wY, int wRad)
{
    int   wXi, wYi, wXf, wYf;
    int   wCut;
    float fLocal;
    float fRad2;
    if ( wRad < 1)
        wRad = 1;
    fRad2 = (float)(wRad * wRad);
    wCut = (int)((float)wRad * 0.707106781187);
    wXi = wX - wCut;
    wXf = wX + wCut;
    ValidSegmentX ( &wXi, &wXf);
    fLocal = (float)(wXi - wX);
    for ( ; wXi <= wXf; wXi++)
    {
        int wCorr =  sqrt(fRad2 - (fLocal * fLocal));
        Plot ( wXi, wY - wCorr, g_wColor);
        Plot ( wXi, wY + wCorr, g_wColor);
        fLocal++;
    }

    wYi = wY - wCut;
    wYf = wY + wCut;
    ValidSegmentY ( &wYi, &wYf);
    fLocal = (float)(wYi - wY);
    for ( ; wYi <= wYf; wYi++)
    {
        int wCorr =  sqrt(fRad2 - (fLocal * fLocal));
        Plot ( wX - wCorr, wYi, g_wColor);
        Plot ( wX + wCorr, wYi, g_wColor);
        fLocal++;
    }
}

// ---------------------------------------------------------------------------

void ValidSegmentX ( int *pwXi, int *pwXf)
{
    int wWidth  = GetScreenWidth  ();
    if ( *pwXi < 0)
        *pwXi = 0;
    if ( *pwXf >= wWidth)
        *pwXf = wWidth - 1;
    if ( *pwXi > *pwXf)
        *pwXf = *pwXi;
}

void ValidSegmentY ( int *pwYi, int *pwYf)
{
    int wHeight  = GetScreenHeight  ();
    if ( *pwYi < 0)
        *pwYi = 0;
    if ( *pwYf >= wHeight)
        *pwYf = wHeight - 1;
    if ( *pwYi > *pwYf)
        *pwYf = *pwYi;
}

// ---------------------------------------------------------------------------

void Line (int Ax, int Ay, int Bx, int By)
{
	int Xincr, Yincr;
	int dX = abs(Bx-Ax);	// store the change in X and Y of the line endpoints
	int dY = abs(By-Ay);
	
	if (Ax > Bx) { Xincr=-1; } else { Xincr=1; }	// which direction in X?
	if (Ay > By) { Yincr=-1; } else { Yincr=1; }	// which direction in Y?
	
	if (dX >= dY)	// if X is the independent variable
	{           
		int dPr 	= dY<<1;          // amount to increment decision if right is chosen
		int dPru 	= dPr - (dX<<1);   // amount to increment decision if up is chosen
		int P 		= dPr - dX;       // decision variable start value

		for (; dX>=0; dX--)       // process each point in the line one at a time
		{
            Plot ( Ax, Ay, g_wColor);
			if (P > 0)               // is the pixel going right AND up?
			{ 
				Ax+=Xincr;	       // increment independent variable
				Ay+=Yincr;         // increment dependent variable
				P+=dPru;           // increment decision (for up)
			}
			else                     // is the pixel just going right?
			{
				Ax+=Xincr;         // increment independent variable
				P+=dPr;            // increment decision (for right)
			}
		}		
	}
	else              // if Y is the independent variable
	{
		int dPr 	= dX<<1;        // amount to increment decision if right is chosen
		int dPru 	= dPr - (dY<<1);  // amount to increment decision if up is chosen
		int P 		= dPr - dY;     // decision variable start value

		for (; dY>=0; dY--)         // process each point in the line one at a time
		{
            Plot ( Ax, Ay, g_wColor);
			if (P > 0)               // is the pixel going up AND right?
			{ 
				Ax+=Xincr;         // increment dependent variable
				Ay+=Yincr;         // increment independent variable
				P+=dPru;           // increment decision (for up)
			}
			else                     // is the pixel just going up?
			{
				Ay+=Yincr;         // increment independent variable
				P+=dPr;            // increment decision (for right)
			}
		}		
	}		
}


