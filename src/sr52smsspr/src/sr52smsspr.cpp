

/* SR52SMSSPR */

/* Tile conversor from SR5 to SMS VRAM data */
/* (c) 2010 Ramones */

// Includes

#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#include "sr52smsspr.hpp"



#define SR5SIZE 27143
#define SC5SIZE 30375
#define PALSC5  0x7680 
#define MAX_LINES 13 
#define EXT ".SPR"


#define LOG(...)    fprintf(stdout,__VA_ARGS__)


// Logo

void logo ()
{
    fprintf(stdout,"SR52SMSSPR Sprite Convert Utility v 0.0 (c) 2010 Ramones\n\n");
}

// Instructions

void usage()
{
    fprintf(stdout,"Usage : sr52sms image.sr5 initline lines (default 0 12) \n\n");
    fprintf(stdout,"    initline: First line to extract data (0-12\n");
    fprintf(stdout,"    lines: Number of lines to extract data (1-13)\n\n");

}


u8* readSR5File (s8* filename)
{
    FILE* pFile;
    

    if ((pFile = fopen (filename,"r+b")) == NULL )
    {
        fprintf(stdout,"ERROR!! An error opening %s \n\n",filename);
        return NULL;
    }

    // Check size
    fseek(pFile,0,SEEK_END);

    s32 size = ftell(pFile);

    if (size < SR5SIZE) 
    {
        fprintf(stdout,"ERROR!! File %s is not a SR5 file. \n\n",filename);
        return NULL;

    }
   
    if (size > SC5SIZE) 
    {
        fprintf(stdout,"ERROR!! File %s is not a SC5 file. \n\n",filename);
        return NULL;

    }

    isSC5 = size >= PALSC5;

    // Create malloc
    u8* pMem = (u8*) malloc (size); 
    if (pMem == NULL)
    {
        fprintf(stdout,"ERROR!! Can't allocate mem. \n\n");
        return NULL;
    }

    // jump to data (ignore header)
    fseek (pFile,7,SEEK_SET); 
    // And read
    fread (pMem,size-7,sizeof(u8),pFile);
    fclose (pFile);



    return pMem; 
}


u8* readPL5File (s8* filename)
{

    FILE* pFile;
    // Check all filenames
    s8* palfilename;

    palfilename = makeext(filename,(s8*)".PL5");

    if ((pFile = fopen (palfilename,"r+b")) == NULL )
    {
        free(palfilename);
        palfilename = makeext(filename,(s8*)".pl5");
        if ((pFile = fopen (palfilename,"r+b")) == NULL )
        {
            free(palfilename);
            palfilename = makeext(filename,(s8*)".Pl5");
            if ((pFile = fopen (palfilename,"r+b")) == NULL )
            {
                free(palfilename);
                palfilename = makeext(filename,(s8*)".pL5");
                if ((pFile = fopen (palfilename,"r+b")) == NULL )
                {
                    free(palfilename);
                    return NULL;
                }

            }
        }
    }

    // Check size
    fseek(pFile,0,SEEK_END);

    s32 size = ftell(pFile);

    if (size < 32)
    {
        fprintf(stdout,"ERROR!! File %s is not a PL5 file. \n\n",palfilename);
        return NULL;

    }
    
    // Create malloc
    u8* pMem = (u8*) malloc (32); 
    if (pMem == NULL)
    {
        fprintf(stdout,"ERROR!! Can't allocate mem. \n\n");
        return NULL;
    }

    // jump to data (ignore header)
    fseek (pFile,0,SEEK_SET); 
    // And read
    fread (pMem,32,sizeof(u8),pFile);
    fclose (pFile);



    return pMem; 
}


s8* makeext (s8* filename,s8* ext){

    s32  i,x;
    s8* outputname;


    i = strlen(filename) - 1;
   
    // Alloc mem

    outputname  = (s8*) malloc (strlen(filename)+4);
    
    if (outputname == NULL)
    {
        fprintf(stdout,"ERROR!! Can't allocate mem. \n\n");
        return NULL;
    }

    // Search ext
    while ((i > 0) && (filename[i] != '.'))
    {
        i--;
    }
    
    // Copy name to outputname
    if (i  == 0) 
    {
        i = strlen(filename);
    }

    for (x = 0 ; x < i ; x++)
    {
        outputname[x] = filename[x];
    }
    outputname[i] = 0;
    outputname = strcat (outputname,ext);
    
    return outputname;
}



void convertcolor (u8 color, u8 pos, u8* b0, u8* b1, u8* b2, u8* b3)
{
    *b0 = (color & 1) << pos;
    *b1 = ((color>>1)&1) << pos;
    *b2 = ((color>>2)&1) << pos;
    *b3 = ((color>>3)&1) << pos;


}




//0=0
//2=1
//4=3
//7=4

void convertpal (u8* sr5pal, u8* convertpal) 
{
    s32 i;
    s32 pos;
    s32 pospal;
    u8 r,b,g;
    u8 fr,fb,fg;
    u8 color;

    // Conversion table
    u8 convtable[8] = {0,0,1,1,2,2,3,3};
    


    pos = 0;
    pospal = 0;
    for (i = 0; i < 16 ; i++)
    {
        // Reads rgb
        r = sr5pal[pos++];
        g = sr5pal[pos++];
        
        b = r & 0xF;
        r = ((r&0xF0)>>4)&0xF;
        

        fr = convtable[r];
        fg = convtable[g]<<2;
        fb = convtable[b]<<4;
        color = fb | fg | fr;
        convertpal[pospal++] = color; 
    }
}


void convertline (u8* rawdata, u8* convertdata)
{
    s32 tile;
    s32 ltile;
    s32 sr5pix;
    u8 b0;
    u8 b1;
    u8 b2;
    u8 b3;
    u8 tb0;
    u8 tb1;
    u8 tb2;
    u8 tb3;
    u8 pos;
    s32 offset;
    s32 offsetline;
    s32 offsetdata;
    u8 sr5color;

    offset = 0;     // Offset generic 
    offsetline=0;   // Line offset
    offsetdata = 0;

    for (tile = 0; tile < 32 ; tile++)
    {
        for (ltile = 0; ltile < 16; ltile++)
        {
            b0 = 0;
            b1 = 0;
            b2 = 0;
            b3 = 0;
            pos = 7;
            for (sr5pix = 0; sr5pix < 4; sr5pix++)
            {
                // High nibble 
                sr5color = (rawdata[offset+offsetline+sr5pix] & 0xF0) >>4;
                convertcolor(sr5color,pos,&tb0,&tb1,&tb2,&tb3);
                b0 |= tb0;
                b1 |= tb1;
                b2 |= tb2;
                b3 |= tb3;
                pos --;

                sr5color = (rawdata[offset+offsetline+sr5pix] & 0x0F);
                convertcolor(sr5color,pos,&tb0,&tb1,&tb2,&tb3);
                b0 |= tb0;
                b1 |= tb1;
                b2 |= tb2;
                b3 |= tb3;
                pos --;


            }
            // Save bytes
            convertdata[offsetdata++] = b0;
            convertdata[offsetdata++] = b1;
            convertdata[offsetdata++] = b2;
            convertdata[offsetdata++] = b3;
            offsetline +=128;
        }
        offset+=4;
        offsetline=0;
    }


}

u8* convert (u8* rawdata, s32 initline, s32 lines)
{
    // Prepare rawdata pointer
    s32 offset;
    s32 offsetdata;

    offset = initline * 8 * 128 * 2;

    // Allocate memory for converted data
    u8* pData = (u8*) malloc (lines * 32 * 32);
    if (pData == NULL) return NULL;    

    s32 i;
    offsetdata = 0;
    for (i = 0 ; i < lines ; i++)
    {
        convertline (&rawdata[offset],&pData[offsetdata]);
        offset += 8*128*2;
        offsetdata += 32*32*2;
    }


    return pData;
}

s32 savepalascfile (s8* filename, u8* paldata)
{
    FILE* pFile;
    s8* outputname;

    outputname = makeext (filename,(s8*) ".ASC");

    if ((pFile = fopen (outputname,"wb")) == NULL )
    {
        free(outputname);
        return 0;
    }
    
    fprintf(pFile,"; SMS Palette data\n\n");
    
    fprintf(pFile,"    db    ");
    
    s32 i;

    for (i = 0; i < 16 ; i++)
    {
        if (i != 15)
        {
            fprintf(pFile,"%02xh,",paldata[i]);
        }
        else 
        {
            fprintf(pFile,"%02xh",paldata[i]);
        }
    }
    fprintf(pFile,"\n\n");
    fflush(pFile);
    fclose(pFile);
    free(outputname);
    return 1;
        
}


s32 savepalfile(s8* filename, u8* paldata)
{
    FILE* pFile;
    s8* outputname;

    outputname = makeext (filename,(s8*) ".PAL");

    if ((pFile = fopen (outputname,"wb")) == NULL )
    {
        free(outputname);
        return 0;
    }
    
    fwrite(paldata,sizeof(u8),16,pFile);
    fflush(pFile);
    fclose(pFile);
    free(outputname);
    return 1;
}

s32 savefile(s8* outputname, s32 lines, u8* convertdata)
{

    FILE* pFile;

    if ((pFile = fopen (outputname,"wb")) == NULL )
    {
        return 0;
    }
    
    fwrite(convertdata,sizeof(u8),lines*32*32*2,pFile);
    fflush(pFile);
    fclose(pFile);
    return 1;
}

// Main

s32 main (s32 argc, s8** argv)
{
    
    s8* filename;
    s8* outfilename;
    u8* rawdata;
    u8* paldata;
    u8* convertdata;
    u8* convertpaldata;
    s32 initline;
    s32 lines;
    isSC5 = false; 

    logo();
    if (argc < 2) {
        usage();
        return 0;
    }

    // Try open input file

    filename = argv[1];
    
    // Read the file
    rawdata = readSR5File(filename);
    if (rawdata == NULL) return -1;
   


    initline = 0;
    lines = 12;

    // Parse lines and number lines
    
    if (argc > 2) 
    {
        initline = atoi(argv[2]);

        if ((initline > 23) || (initline < 0))
        {
            fprintf(stdout,"ERROR!! initline param (0-12) \n\n");
            return -1;
        }

        if (argc > 3)
        {
            lines = atoi(argv[3]);
            if ((lines < 1) || (lines > MAX_LINES))
            {
                fprintf(stdout,"ERROR!! lines param (1-13) \n\n");
                return -1;

            }
        }
        // Adapt lines 
        if (lines > (MAX_LINES  -  initline)) 
        {
            lines = MAX_LINES - initline;
        }
    }
    
    // Show info
     
    outfilename = makeext (filename,(s8*)EXT); 
    if (outfilename == NULL)
    {
        return -1;
    }

    fprintf(stdout,"Converting %s to %s\n",filename,outfilename);
    fprintf(stdout,"Init Line: %i\n",initline);
    fprintf(stdout,"Number of lines: %i\n",lines);
    
    convertdata = convert (rawdata,initline,lines);

    if (convertdata == NULL)
    {
        fprintf(stdout,"ERROR! Converting data ... \n\n");
        return -1;
    }


    // Save file
    if (!savefile(outfilename,lines,convertdata))
    {
        fprintf(stdout,"ERROR! Saving file %s\n",outfilename);
        return -1;

    }


    // Converting palete
    if (!isSC5)
        paldata = readPL5File(filename);
    else 
    {
        paldata = (u8*) malloc (32);
        // Copy pal data
        memcpy (paldata,&rawdata[PALSC5],32);
    }
    if (paldata)
    {
        fprintf (stdout,"Saving palette file...\n"); 
        convertpaldata = (u8*) malloc(16);
        if (convertpaldata == NULL)
        {
            fprintf(stdout,"ERROR!! Can't allocate mem. \n\n");
            return -1;
        }
        convertpal (paldata,convertpaldata);
        if (!savepalfile (filename,convertpaldata))
        {
            fprintf(stdout,"ERROR! Saving palette file\n");
            return -1;
        }
        if (!savepalascfile(filename,convertpaldata))
        {
            fprintf(stdout,"ERROR! Saving palette file\n");
        }
        free (paldata);
        free (convertpaldata);
    }
    // Free mem

    free(convertdata);
    free(outfilename);
    free(rawdata);

    fprintf (stdout,"All ok! Bye!\n");
    return 0;
}

