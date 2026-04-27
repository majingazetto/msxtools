/*
 *  Files.c
 *  AMOSLib
 *
 *  Created by Luis Pons on Sat Nov 30 2002.
 *  Copyright (c) 2002 __MyCompanyName__. All rights reserved.
 *
 */

#include <stdlib.h>
#include <stdio.h>
#include <string.h>

#include <AMOSLib.h>

#include "Files.h"
#include "Memory.h" 

#define MAXLEN_NAME (200)

static char g_pDefaultDir [MAXLEN_NAME];
static char g_pConcat     [MAXLEN_NAME * 2];

// -------------------------------------------------------------------------

void FilesInit ()
{
    strcpy ( g_pDefaultDir, "");
}

// -------------------------------------------------------------------------

static void  GetNameNoPath ( const char *pName, char *pNoPath)
{
    int i=0;
    // Encontrar el final
    while ( pName[i] != 0)
        i++;
    // Buscar el "/"
    while ((i>=0) && ( pName[i] != '/'))
        i--;
    i++;
    // Copiar el nombre
    while ( pName[i] != 0)
    {
        *pNoPath++ = pName[i];
        i++;
    }
    *pNoPath++ = 0;
}

// -------------------------------------------------------------------------

static int ConcatNames ( char *pName)
{
    if ( strlen ( pName) >= MAXLEN_NAME)
    {
        printf ("Invalid file name: %s (too long?)\n", pName);
        return 0;
    }
    else
    {
        strcpy ( g_pConcat, g_pDefaultDir);
        strcat ( g_pConcat, pName);
        return 1;
    }
}

// -------------------------------------------------------------------------

void  SetDir  ( char *pDir)
{
    if ( strlen ( pDir) >= MAXLEN_NAME)
    {
        printf ("Invalid dir name: %s (too long?)\n", pDir);
        return;
    }
    
    strcpy(g_pDefaultDir, pDir);
}

// -------------------------------------------------------------------------

FILE * SpeculativeOpen ( const char * pName, const char * pAttribs)
{
	FILE * pFileHand = NULL;
    if ( ConcatNames ( pName) == 0)
        return 0;
    pFileHand = fopen ( g_pConcat, pAttribs);
	if ( pFileHand == NULL)
    {
        pFileHand = fopen  ( pName, pAttribs);
        if ( pFileHand == NULL)
        {
            char pNoPath [MAXLEN_NAME];
            GetNameNoPath ( pName, pNoPath);
            pFileHand = fopen  ( pNoPath, pAttribs);
            if ( pFileHand == NULL)
            {
                printf ("File %s not found\n", g_pConcat);
                return NULL;
            }
        }
    }
    return pFileHand;
}

// -------------------------------------------------------------------------

void * BinLoad  ( char *pName)
{
	FILE         *pFileHand = NULL;
	void         *pTemp     = NULL;
	long wSize;
	long wRead;

    pFileHand = SpeculativeOpen ( pName, "rb");
    if ( pFileHand == NULL)
        return NULL;

	fseek ( pFileHand, -1, SEEK_END);
	wSize = ftell ( pFileHand);
	wSize++;
	fseek ( pFileHand, 0, SEEK_SET);

	pTemp = ReserveAsFast ( wSize, "BinLoad function\n", DEFAULT_ALIGN, DEFAULT_PREFETCH);
	if ( pTemp == NULL)
    {
        printf ("Not enough memory ( %d bytes requested)\n", (int)wSize);
		return NULL;
    }

	wRead = fread  ( pTemp, 1, wSize, pFileHand);
	if ( wRead == 0)
    {
        printf ("Can't read file %s\n", g_pConcat);
		return NULL;
    }

	fclose ( pFileHand);

	return pTemp;
}

// -------------------------------------------------------------------------

void * BinLoadIn ( char *pName, void *pAddr)
{
	FILE *pFileHand = NULL;
	void *pTemp     = NULL;
	long  wSize;
	long  wRead;

    pFileHand = SpeculativeOpen ( pName, "rb");
    if ( pFileHand == NULL)
        return NULL;

	fseek ( pFileHand, -1, SEEK_END);
	wSize = ftell ( pFileHand);
	wSize++;
	fseek ( pFileHand, 0, SEEK_SET);

	wRead = fread  ( pAddr, 1, wSize, pFileHand);
	if ( wRead == 0)
    {
        printf ("Can't read file %s\n", g_pConcat);
		return NULL;
    }

	fclose ( pFileHand);

	return pTemp;
}

// -------------------------------------------------------------------------

int BinSave ( char *pName, void * pAddr, long wSize)
{
	FILE  *pFileHand = NULL;
	long   wWrote;

    if ( ConcatNames ( pName) == 0)
        return 0;

	pFileHand = fopen  ( g_pConcat, "wb");
	if ( pFileHand == NULL)
    {
        printf ("File %s not found\n", g_pConcat);
		return 0;
    }

	wWrote = fwrite  ( pAddr, 1, wSize, pFileHand);
	if ( wWrote == 0)
    {
        printf ("Can't write file %s\n", g_pConcat);
		return 0;
    }

	fclose ( pFileHand);
  
    return 1;
}

// -------------------------------------------------------------------------

int GetFileSize ( char *pName)
{
	FILE   *pFileHand = NULL;
	long wSize;

    pFileHand = SpeculativeOpen ( pName, "rb");
    if ( pFileHand == NULL)
        return NULL;

	fseek ( pFileHand, -1, SEEK_END);
	wSize = ftell ( pFileHand);
	wSize++;

	fclose ( pFileHand);
  
    return wSize;
}

// -------------------------------------------------------------------------

int  FileExist   ( char *pName)
{
	FILE   *pFileHand = NULL;

    pFileHand = SpeculativeOpen ( pName, "rb");
    if ( pFileHand == NULL)
        return NULL; 
    
    fclose ( pFileHand);
    
    return 1;
}

// -------------------------------------------------------------------------

