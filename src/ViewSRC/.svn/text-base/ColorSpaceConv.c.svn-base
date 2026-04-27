/*
 *  ColorSpaceConv.c
 *  AMOSLib
 *
 *  Created by Luis Pons on Sat Nov 30 2002.
 *  Copyright (c) 2002 __MyCompanyName__. All rights reserved.
 *
 */

#include <assert.h>
#include <stdlib.h>

#include <AMOSLib.h>

#include "ColorSpaceConv.h"

// ----------------------------------------------------------------------------

typedef void *  (*READ_PIXEL)    ( void *pIn, int *pwR, int *pwG, int *pwB);
typedef void *  (*WRITE_PIXEL)   ( int wR, int wG, int wB, void *pOut);

typedef struct
{
    READ_PIXEL  pRead;
    WRITE_PIXEL pWrite;
    int         wModeTag;
    int         wPixelSize;
} COLOR_TRANSFORM;

void * ReadYUV888  ( void * pIn, int *pwR, int *pwG, int *pwB);
void * WriteYUV888 ( int wR, int wG, int wB, void *pOut);
void * ReadHSL637  ( void * pIn, int *pwR, int *pwG, int *pwB);
void * WriteHSL637 ( int wR, int wG, int wB, void *pOut);
void * ReadHSL888  ( void * pIn, int *pwR, int *pwG, int *pwB);
void * WriteHSL888 ( int wR, int wG, int wB, void *pOut);
void * ReadRGB888  ( void * pIn, int *pwR, int *pwG, int *pwB);
void * WriteRGB888 ( int wR, int wG, int wB, void *pOut);
void * ReadRGB565  ( void * pIn, int *pwR, int *pwG, int *pwB);
void * WriteRGB565 ( int wR, int wG, int wB, void *pOut);
void * ReadRGB555  ( void * pIn, int *pwR, int *pwG, int *pwB);
void * WriteRGB555 ( int wR, int wG, int wB, void *pOut);
void * ReadYUV754 ( void * pIn, int *pwR, int *pwG, int *pwB);
void * WriteYUV754 ( int wR, int wG, int wB, void *pOut);

COLOR_TRANSFORM g_pColorTrans [] =
{
{&ReadRGB555 , &WriteRGB555 , RGB555, 2},
{&ReadRGB565 , &WriteRGB565 , RGB565, 2},
{&ReadHSL637 , &WriteHSL637 , HSL637, 2},
{&ReadYUV754 , &WriteYUV754 , YUV754, 2},
//
{&ReadRGB888 , &WriteRGB888 , RGB888, 4},
{&ReadYUV888 , &WriteYUV888 , YUV888, 4},
{&ReadHSL888 , &WriteHSL888 , HSL888, 4},
};

// --------------------------------------------------------------------------

void ColorTransform ( void *pSrc, int wColorModeSrc,
                      void *pDst, int wColorModeDst,
                      int wPixels)
{
    int i;
    READ_PIXEL  pRead;
    WRITE_PIXEL pWrite;
    if ( wColorModeSrc != wColorModeDst)
    {
        pRead  = g_pColorTrans [ wColorModeSrc].pRead;
        pWrite = g_pColorTrans [ wColorModeDst].pWrite;
        assert(wColorModeSrc == g_pColorTrans [ wColorModeSrc].wModeTag);
        assert(wColorModeDst == g_pColorTrans [ wColorModeDst].wModeTag);
        for ( i=0; i < wPixels; i++)
        {
            int wR, wG, wB;
            pSrc = pRead  ( pSrc, &wR, &wG, &wB);
            pDst = pWrite ( wR, wG, wB,pDst);
        }
    }
    else
        memcpy ( pDst, pSrc, 
                 wPixels * g_pColorTrans [ wColorModeSrc].wPixelSize);    
}

// --------------------------------------------------------------------------

int  GetColorModePixelSize ( int wColorMode)
{
    return g_pColorTrans [ wColorMode].wPixelSize;
}

// --------------------------------------------------------------------------

static int Clamp8 ( int w8)
{
    if ( w8 < 0)
        return 0;
    if ( w8 > 255)
        return 255;
    return w8;
}

// --------------------------------------------------------------------------

void * ReadYUV754 ( void * pIn, int *pwR, int *pwG, int *pwB)
{
    float pfYUV[3], pfRGB[3];
    unsigned int wPixel = *(unsigned short *) pIn;
    pfYUV [ 0] = ((float)(wPixel >> 9)) / 127.0;
    pfYUV [ 1] = ((float)((wPixel >> 4) & 0x1f)) / 31.0;
    pfYUV [ 2] = ((float)(wPixel & 0xf)) / 15.0;
    YUV2RGB ( pfYUV, pfRGB);
    *pwR = Clamp8 ((int)(pfRGB[0] * 255.0));
    *pwG = Clamp8 ((int)(pfRGB[1] * 255.0));
    *pwB = Clamp8 ((int)(pfRGB[2] * 255.0));
    return (void *)((( int) pIn) + 2);
}

void * WriteYUV754 ( int wR, int wG, int wB, void *pOut)
{
    float pfYUV[3], pfRGB[3];
    int wY, wU, wV;
    pfRGB[0] = ((float) wR) / 255.0;
    pfRGB[1] = ((float) wG) / 255.0;
    pfRGB[2] = ((float) wB) / 255.0;
    RGB2YUV ( pfRGB, pfYUV);
    wY = Clamp8((int)(pfYUV [0] * 255.0));
    wU = Clamp8((int)(pfYUV [1] * 255.0));
    wV = Clamp8((int)(pfYUV [2] * 255.0));
    wY >>= 1;
    wU >>= 3;
    wV >>= 4;
    *(unsigned long *) pOut = (wY << 9) | (wU << 4) | wV;
    return (void *)((( int) pOut) + 2);
}

// --------------------------------------------------------------------------

void * ReadYUV888 ( void * pIn, int *pwR, int *pwG, int *pwB)
{
    float pfYUV[3], pfRGB[3];
    unsigned int wPixel = *(unsigned long *) pIn;
    pfYUV [ 0] = ((float)((wPixel >> 16) & 0xff)) / 255.0;
    pfYUV [ 1] = ((float)((wPixel >> 8) & 0xff)) / 255.0;
    pfYUV [ 2] = ((float)(wPixel & 0xff)) / 255.0;
    YUV2RGB ( pfYUV, pfRGB);
    *pwR = Clamp8 ((int)(pfRGB[0] * 255.0));
    *pwG = Clamp8 ((int)(pfRGB[1] * 255.0));
    *pwB = Clamp8 ((int)(pfRGB[2] * 255.0));
    return (void *)((( int) pIn) + 4);
}

void * WriteYUV888 ( int wR, int wG, int wB, void *pOut)
{
    float pfYUV[3], pfRGB[3];
    int wY, wU, wV;
    pfRGB[0] = ((float) wR) / 255.0;
    pfRGB[1] = ((float) wG) / 255.0;
    pfRGB[2] = ((float) wB) / 255.0;
    RGB2YUV ( pfRGB, pfYUV);
    wY = Clamp8((int)(pfYUV [0] * 255.0));
    wU = Clamp8((int)(pfYUV [1] * 255.0));
    wV = Clamp8((int)(pfYUV [2] * 255.0)); 
    *(unsigned long *) pOut = (wY << 16) | (wU << 8) | wV;
    return (void *)((( int) pOut) + 4);
}

// --------------------------------------------------------------------------

void * ReadHSL637 ( void * pIn, int *pwR, int *pwG, int *pwB)
{
    float pfHLS[3], pfRGB[3];
    unsigned int wPixel = *(unsigned short *) pIn;
    pfHLS [ 0] = ((float)((wPixel >> 10) & 0x3f)) / 63.0;
    pfHLS [ 1] = ((float)(wPixel & 0x7f)) / 127.0;
    pfHLS [ 2] = ((float)((wPixel >> 7) & 0x7)) / 8.0;
    HLS2RGB ( pfHLS, pfRGB);
    *pwR = Clamp8 ((int)(pfRGB[0] * 255.0));
    *pwG = Clamp8 ((int)(pfRGB[1] * 255.0));
    *pwB = Clamp8 ((int)(pfRGB[2] * 255.0));
    return (void *)((( int) pIn) + 2);
}

void * WriteHSL637 ( int wR, int wG, int wB, void *pOut)
{
    float pfHLS[3], pfRGB[3];
    int wH, wL, wS;
    pfRGB[0] = ((float) wR) / 255.0;
    pfRGB[1] = ((float) wG) / 255.0;
    pfRGB[2] = ((float) wB) / 255.0;
    RGB2HLS ( pfRGB, pfHLS);
    wH = Clamp8((int)(pfHLS [0] * 255.0));
    wL = Clamp8((int)(pfHLS [1] * 255.0));
    wS = Clamp8((int)(pfHLS [2] * 255.0));
    wH >>= 2;
    wS >>= 5;
    wL >>= 1;    
    *(unsigned short *) pOut = (wH << 10) | (wS << 7) | wL;
    return (void *)((( int) pOut) + 2);
}

// --------------------------------------------------------------------------

void * ReadHSL888 ( void * pIn, int *pwR, int *pwG, int *pwB)
{
    float pfHLS[3], pfRGB[3];
    unsigned int wPixel = *(unsigned long *) pIn;
    pfHLS [ 0] = ((float)((wPixel >> 16) & 0xff)) / 255.0;
    pfHLS [ 1] = ((float)(wPixel & 0xff)) / 255.0;
    pfHLS [ 2] = ((float)((wPixel >> 8) & 0xff)) / 255.0;
    HLS2RGB ( pfHLS, pfRGB);
    *pwR = Clamp8 ((int)(pfRGB[0] * 255.0));
    *pwG = Clamp8 ((int)(pfRGB[1] * 255.0));
    *pwB = Clamp8 ((int)(pfRGB[2] * 255.0));
    return (void *)((( int) pIn) + 4);
}

void * WriteHSL888 ( int wR, int wG, int wB, void *pOut)
{
    float pfHLS[3], pfRGB[3];
    int wH, wL, wS;
    pfRGB[0] = ((float) wR) / 255.0;
    pfRGB[1] = ((float) wG) / 255.0;
    pfRGB[2] = ((float) wB) / 255.0;
    RGB2HLS ( pfRGB, pfHLS);
    wH = Clamp8((int)(pfHLS [0] * 255.0));
    wL = Clamp8((int)(pfHLS [1] * 255.0));
    wS = Clamp8((int)(pfHLS [2] * 255.0)); 
    *(unsigned long *) pOut = (wH << 16) | (wS << 8) | wL;
    return (void *)((( int) pOut) + 4);
}

// --------------------------------------------------------------------------

void * ReadRGB888 ( void * pIn, int *pwR, int *pwG, int *pwB)
{
    unsigned int wPixel = *(unsigned long *) pIn;
    *pwR = (wPixel >> 16) & 0xff; 
    *pwG = (wPixel >> 8) & 0xff;
    *pwB = wPixel        & 0xff;
    return (void *)((( int) pIn) + 4);
}

void * WriteRGB888 ( int wR, int wG, int wB, void *pOut)
{
    *(unsigned long *) pOut = (wR << 16) | (wG << 8) | wB;
    return (void *)((( int) pOut) + 4);
}

// --------------------------------------------------------------------------

void * ReadRGB565 ( void * pIn, int *pwR, int *pwG, int *pwB)
{
    unsigned int wPixel = *(unsigned short *) pIn;
    *pwR = (((wPixel >> 11) & 0x1f) * 8 * 255) / (31*8); 
    *pwG = (((wPixel >> 5) & 0x3f)  * 4 * 255) / (63*4);
    *pwB = ((wPixel        & 0x1f)  * 8 * 255) / (31*8);
    return (void *)((( int) pIn) + 2);
}

void * WriteRGB565 ( int wR, int wG, int wB, void *pOut)
{
    *(unsigned short *) pOut = ((wR >> 3) << 11) | ((wG >> 2) << 5) | (wB >> 3);
    return (void *)((( int) pOut) + 2);
}

// --------------------------------------------------------------------------

void * ReadRGB555 ( void * pIn, int *pwR, int *pwG, int *pwB)
{
    unsigned int wPixel = *(unsigned short *) pIn;
    *pwR = (((wPixel >> 10) & 0x1f) * 8 * 255) / (31*8); 
    *pwG = (((wPixel >> 5) & 0x1f)  * 8 * 255) / (31*8);
    *pwB = ((wPixel        & 0x1f)  * 8 * 255) / (31*8);
    return (void *)((( int) pIn) + 2);
}

void * WriteRGB555 ( int wR, int wG, int wB, void *pOut)
{
    *(unsigned short *) pOut = ((wR >> 3) << 10) | ((wG >> 3) << 5) | (wB >> 3);
    return (void *)((( int) pOut) + 2);
}

// --------------------------------------------------------------------------

static float fmax (float f1, float f2)
{
  return f1 > f2? f1 : f2;
}

static float fmin (float f1, float f2)
{
  return f1 < f2? f1 : f2;
}

static float fmax3 (const float * f)
{
  return fmax ( fmax ( f[0], f[1]), f[2]);
}

static float fmin3 (const float * f)
{
  return fmin ( fmin(f[0], f[1]), f[2]);
}


// --------------------------------------------------------------------------

void RGB2HLS (const float * rgb, float * hls)
{
    float max = fmax3 ( rgb);
    float min = fmin3 ( rgb);
    float sum = max + min;
    float delta = max - min;
    hls[1] = sum * .5f;
    if (0.f == delta)
        hls[0] = hls[2] = 0.f;
    else
    {
        if (sum > 1.f)
            sum = 2.f - sum;
        hls[2] = delta / sum;
        if (max == rgb[0]) 
            hls[0] = -rgb[2] + rgb[1];
                else 
                    if (max == rgb[1]) 
                        hls[0] = 2.f * delta - rgb[0] + rgb[2];
                    else          
                        hls[0] = 4.f * delta - rgb[1] + rgb[0];
        hls[0] /= (6.f * delta);
    }
    
    if ( hls[0] < 0.0)
        hls[0] += 1.0; 
}


// ----------------------------------------------------------------------------

static float val ( float n1, float n2, float h)
{
    float rv;
    while (h < 0.f)
        h += 1.f;
    while (h > 1.f)
        h -= 1.f;
    if      (h < 1.f/6.f)  
        rv = n1 + (n2 - n1) * h * 6.f;
    else 
        if (h < .5f)      
            rv = n2;
        else 
            if (h < 4.f/6.f)  
                rv = n1 + (n2 - n1) * (4.f/6.f - h) * 6.f;
            else
                rv = n1;
  return rv;
}

// ----------------------------------------------------------------------------

void HLS2RGB (const float * hls, float * rgb)
{
    if (hls[2] == 0.f)
        rgb[0] = rgb[1] = rgb[2] = hls[1];
    else
    {
        float m1, m2;
        if (hls[1] < .5f) 
            m2 = hls[1] + ( hls[1] * hls[2]); 
        else
            m2 = hls[1] + hls[2] - ( hls[1] * hls[2]);
        m1 = 2.f * hls[1] - m2;
        rgb[0] = val ( m1, m2, hls[0] + 1.f/3.f);
        rgb[1] = val ( m1, m2, hls[0]);
        rgb[2] = val ( m1, m2, hls[0] - 1.f/3.f);
    }
}

// ----------------------------------------------------------------------------

static __inline__ float dot3 (const float * m, const float * v)
{
  return m[0] * v[0] + m[1] * v[1] + m[2] * v[2];
}

static __inline__ void vecmat3 ( float * o, const float * m, const float * i)
{
  o[0] = dot3 ( m, i);  
  o[1] = dot3 ( m + 3, i); 
  o[2] = dot3 ( m + 6, i);
}

// ----------------------------------------------------------------------------

void RGB2YUV (const float * rgb, float * yuv)
{
  const float m[9] = 
  {
     0.299f ,  0.587f ,  0.114f,
    -0.147f , -0.289f ,  0.437f,
     0.615f , -0.515f , -0.100f
  };
  vecmat3(yuv, m, rgb);
  yuv [1] += 0.5; 
  yuv [2] += 0.5; 

}

// ----------------------------------------------------------------------------

void YUV2RGB ( float * yuv, float * rgb)
{
  const float m[9] =
  {
     1.000f ,  0.000f ,  1.140f, 
     1.000f , -0.394f , -0.581f,
     1.000f ,  2.028f ,  0.000f
  };

  yuv [1] -= 0.5; 
  yuv [2] -= 0.5; // Chapuza
  vecmat3(rgb, m, yuv);
  yuv [1] += 0.5;  // lo dejamos como estaba
  yuv [2] += 0.5; 
}


