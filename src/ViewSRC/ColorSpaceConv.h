/*
 *  ColorSpaceConv.h
 *  AMOSLib
 *
 *  Created by Luis Pons on Sat Nov 30 2002.
 *  Copyright (c) 2002 __MyCompanyName__. All rights reserved.
 *
 */

#ifndef _COLOR_SPACE_CONV_H_
#define _COLOR_SPACE_CONV_H_

void ColorTransform ( void *pSrc, int wColorModeSrc,
        void *pDst, int wColorModeDst,
        int wPixels);

int  GetColorModePixelSize ( int wColorMode);

void YUV2RGB (       float * yuv, float * rgb);
void RGB2YUV ( const float * rgb, float * yuv);
void HLS2RGB ( const float * hls, float * rgb);
void RGB2HLS ( const float * rgb, float * hls);

#endif // _COLOR_SPACE_CONV_H_

