#include <stdlib.h>
#include <stdio.h>
#include <string.h>
#include <math.h>
#include <ctype.h>

// ------------------------------------------------------------------------------

/* *** DEFINES *** */



#define BYTE unsigned char


// ------------------------------------------------------------------------------

/* LOGO */

void printLogo (void) {
	
	printf ("\nSR5 To Spr v 0.1 MSX Spr conversion Tool (c) 2005 Kralizec \n\n");
	
	
}




/* USAGE */

void printUsage (void) {
	
	printf ("Usage: SR52SPR source\n\n");
	printf ("Example: \n");
	printf ("        SR52MAP SPRSET.SR5 \n\n");
	printf ("Creates a SPRSET.XXX files from SPRSET.SR5...\n\n");
}



void ExtractExt (char *pName, char *pExt, char *pNameWExt) { 
	
	int i = 0;
	BYTE hext = 0;
	
	if (pName) {
		
        // Search end of array and "."
		
        while ( pName[i] != 0) {
			
			if (!hext) 
				hext = (pName[i] == '.');
			i++;
        }
		
		
		
		// Search .
		
        if (hext) {
			
			while ((i>=0) && ( pName[i] != '.'))
				i--;        
			
			// Copy ext        
			
			strcpy (pNameWExt,pName);
			
			pNameWExt[i+1] = 0; // End
			
			while ( pName[i] != 0)
			{
				i++;
				*pExt++ = toupper(pName[i]);
				
			}
			
			
        }
		
	}
	
}


int createNewSprFiles (char *pNameMap, char **pNameDAT, char **pNameC1, char **pNameC2, char **pNameC3) {
	
	*pNameDAT =	(char *) malloc ( strlen(pNameMap) );
	*pNameC1  = (char *) malloc ( strlen(pNameMap) );
	*pNameC2  = (char *) malloc ( strlen(pNameMap) );
	*pNameC3  = (char *) malloc ( strlen(pNameMap) );	
	
	char *pExt = NULL;
	char *pWExt = NULL;
	
	pExt  = (char *) malloc ( strlen(pNameMap) );
	pWExt = (char *) malloc ( strlen(pNameMap) );	
	
	if ( (!*pNameDAT) || (!*pNameC1) || (!*pNameC2) || (!*pNameC3) || (!pExt) || (!pWExt) ){
		return 0;
	}
	
	ExtractExt(pNameMap,pExt,pWExt);
	
	// Create Name files 
	
	strcpy (*pNameDAT,pWExt);
	strcpy (*pNameC1,pWExt);
	strcpy (*pNameC2,pWExt);
	strcpy (*pNameC3,pWExt);
	
	
	// Add Extension
	
	strcat (*pNameDAT,"DAT");
	strcat (*pNameC1,"CC1");
	strcat (*pNameC2,"CC2");
	strcat (*pNameC3,"CC3");
	
	
	
	
	free (pExt);
	free (pWExt);
	
	
	return 1;
}



// ------------------------------------------------------------------------------

/* *** FILE ROUTINES *** */

int readFilesSR5 (char *pNameSRC, BYTE **pSRC){
	
	FILE *pflSRC = NULL;
	
	long wSize = 0;
	long wRead = 0;
	
	
	if (! (pflSRC = fopen (pNameSRC,"rb")) ){
		
		printf ("Problems opening source file %s \n",pNameSRC);
		return 0;
	}
	
	
	// Read SOURCE file 
	
	fseek ( pflSRC, -1, SEEK_END);
	wSize = ftell ( pflSRC);
	wSize++;
	wSize -=7;
	
	fseek ( pflSRC, 7, SEEK_SET);
	
	*pSRC = (BYTE *) malloc (sizeof (BYTE) * (int) wSize);
	
	
	if (!*pSRC){
		printf ("Problems allocating memory ... \n");
		fclose (pflSRC);
		return 0;
	}
	
	
	wRead = fread  ( *pSRC, 1, wSize, pflSRC);
	if ( wRead == 0)
    {
        printf ("Can't read source file %s\n", pNameSRC);
		return 0;
    }
	
	printf ("Source file   : %s\n",pNameSRC);
	
	
	
	fclose (pflSRC);
	
	
	return 1;
}

// ------------------------------------------------------------------------------

/* *** PROGRAM ROUTINES *** */


// Extract 1 tile from sprite

void extractSPRTile (BYTE *pSRC, BYTE *pDAT) {
	
	int i,isrc,ispr;
	BYTE b0,b1,b2,b3,b4,b5,b6,b7;
	
	ispr = 0;
	
	for (i = 0 ; i < 8 ; i++) {
		
		isrc = i*128;
		b7 = ((pSRC[isrc]   & 0xF0) != 0) << 7;
		b6 = ((pSRC[isrc++] & 0x0F) != 0) << 6;		
		b5 = ((pSRC[isrc]   & 0xF0) != 0) << 5;
		b4 = ((pSRC[isrc++] & 0x0F) != 0) << 4;		
		b3 = ((pSRC[isrc]   & 0xF0) != 0) << 3;
		b2 = ((pSRC[isrc++] & 0x0F) != 0) << 2;
		b1 = ((pSRC[isrc]   & 0xF0) != 0) << 1;
		b0 = ((pSRC[isrc++] & 0x0F) != 0);		
		
		
		
		pDAT[ispr++] = b7|b6|b5|b4|b3|b2|b1|b0;
		
	}
	
	
}


// Generates 16x16 SPR Data from Source into Dat

void extractSPR (BYTE *pSRC, BYTE *pDAT){
	
	int SourcesArray[] = {0,128*8,4,(128*8)+4};
	
	int i,cnt;
	
	cnt = 0;
	for (i = 0; i< 4 ; i++) {
		
		extractSPRTile(&pSRC[SourcesArray[i]],&pDAT[cnt]);
		
		cnt += 8;
		
	}
	
	
}

BYTE extractCC1 (BYTE *pSRC) {
	
	int x,y,isrc;
	BYTE c1,c2;
	
	for (y = 0; y <  16; y++) {
		
		isrc = y * 128;
		
		for (x = 0; x < 8 ; x ++) {
			
			c1 = (pSRC [isrc] & 0xF0) >> 4;
			c2 = (pSRC [isrc] & 0x0F);
			
			if (c1) return c1;
			if (c2) return c2;
			
			
			isrc ++;
		}
		
	} 
	
	return 0;
}


void  extractCCC (BYTE *pSRC, BYTE *pDAT, BYTE bMask) {
	
	int x,y,isrc;
	BYTE c1,c2,cf,set;	
	
	for (y = 0; y <  16; y++) {
		
		isrc = y * 128;
		set = 0;
		cf = 0;
		for (x = 0; x < 8 ; x ++) {
			
			
			if (!set) {
			c1 = (pSRC [isrc] & 0xF0) >> 4;
			c2 = (pSRC [isrc++] & 0x0F);
			
			
			if (c1) cf = c1;
			if (c2) cf = c2;
			
			if (cf) set = 1;
			
			}
			
			
			
		}
		
		*pDAT++ = cf | bMask;
		
		
	}
	
	
}



// Gen DAT File

int genDATFile (char *pNameFile, BYTE *pSRC){
	
	printf ("Generating DAT file : %s",pNameFile);	
	BYTE *pTemp = NULL;
	pTemp = (BYTE *) malloc (8*32*8);	
	
	if (!pTemp) {
		printf ("\nProblems allocating memory ... \n");
		return 0;
		
	}
	// Fill with 0
	
	memset(pTemp,0,8*32*8);
	
	int x,y,isrc,ispr;
	
	ispr = 0;
	for (y = 0; y < 4 ; y++) {	
		
		for (x = 0; x < 16; x++) {
			
			isrc = (y << 11) + (x<<3);
			extractSPR (&pSRC[isrc],&pTemp[ispr]);			
			ispr+=32;
			
		}			
		
		
	}
	
	// Write file
	
	FILE *pflTemp = NULL;
	long wWrote = 0;
	
	
	pflTemp = fopen (pNameFile,"wb");
	
	if (!pflTemp) {
		
		printf ("\nCan't write file %s\n",pNameFile);		
		return 0;
	}
	
	wWrote = fwrite  ( pTemp, 1,2048, pflTemp);
	
	if (!wWrote) {
		
		printf ("\nCan't write file %s\n",pNameFile);	
		return 0;	
	}
	
	fflush(pflTemp);
	fclose(pflTemp);
	free (pTemp);
	
	printf (" OK!\n");
	
	return 1;
}




int genC1File (char *pNameFile, BYTE *pSRC){
	
	printf ("Generating CC1 file : %s",pNameFile);	
	BYTE *pTemp = NULL;
	pTemp = (BYTE *) malloc (64);	
	
	if (!pTemp) {
		printf ("\nProblems allocating memory ... \n");
		return 0;
		
	}
	// Fill with 0
	
	memset(pTemp,0,64);
	
	int x,y,isrc,i;
	i = 0;
	
	for (y = 0; y < 4 ; y++) {	
		
		for (x = 0; x < 16; x++) {
			
			isrc = (y << 11) + (x<<3);
			pTemp[i] = extractCC1 (&pSRC[isrc]);			
			i++;
		}			
		
		
	}
	
	// Write file
	
	FILE *pflTemp = NULL;
	long wWrote = 0;
	
	
	pflTemp = fopen (pNameFile,"wb");
	
	if (!pflTemp) {
		
		printf ("\nCan't write file %s\n",pNameFile);		
		return 0;
	}
	
	wWrote = fwrite  ( pTemp, 1,64, pflTemp);
	
	if (!wWrote) {
		
		printf ("\nCan't write file %s\n",pNameFile);	
		return 0;	
	}
	
	fflush(pflTemp);
	fclose(pflTemp);
	free (pTemp);
	
	
	
	printf (" OK!\n");
	return 1;
}


int genCCCFile (char *pNameFile, BYTE *pSRC, BYTE bMask1, BYTE bMask2){
	
	printf ("Generating CCE file : %s",pNameFile);	
	BYTE *pTemp = NULL;
	pTemp = (BYTE *) malloc (64*16);	
	
	if (!pTemp) {
		printf ("\nProblems allocating memory ... \n");
		return 0;
		
	}
	// Fill with 0
	
	memset(pTemp,0,64);
	
	int x,y,isrc,i;
	BYTE bMask;
	
	i = 0;
	
	for (y = 0; y < 4 ; y++) {	
		
		for (x = 0; x < 16; x++) {
			
			
			if (x & 1) {
				bMask = bMask2;
			}
			else {
				bMask = bMask1;
				
			}
			
			isrc = (y << 11) + (x<<3);
			extractCCC (&pSRC[isrc],&pTemp[i],bMask);			
			i+=16;
		}			
		
		
	}
	
	// Write file
	
	FILE *pflTemp = NULL;
	long wWrote = 0;
	
	
	pflTemp = fopen (pNameFile,"wb");
	
	if (!pflTemp) {
		
		printf ("\nCan't write file %s\n",pNameFile);		
		return 0;
	}
	
	wWrote = fwrite  ( pTemp, 1,64*16, pflTemp);
	
	if (!wWrote) {
		
		printf ("\nCan't write file %s\n",pNameFile);	
		return 0;	
	}
	
	fflush(pflTemp);
	fclose(pflTemp);
	free (pTemp);
	
	
	
	printf (" OK!\n");
	return 1;
}




// ------------------------------------------------------------------------------

int main (int argc, const char * argv[]) {
	
	
 	// Check arguments
	printLogo();
	
	if (argc < 2) {
		printUsage();
		return 1;
	}
	
	int iError = 0;
	BYTE *pSource = NULL;
	
	
	iError = readFilesSR5 ((char *) argv[1],&pSource);
	
	if (!iError)
	{	
		printf ("\n");
		return 2;
	}
	
	char *pNameMapDAT = NULL;
	char *pNameMapC1  = NULL;
	char *pNameMapC2  = NULL;
	char *pNameMapC3  = NULL;
	
	iError = createNewSprFiles ((char*)argv[1],&pNameMapDAT,&pNameMapC1,&pNameMapC2,&pNameMapC3);		
	
 	if (!iError){
		
		printf ("Problems allocating mem ...\n");
		return 3;
	}
	
	
	printf("\nSPR Dat File             : %s\n",pNameMapDAT);
	printf("SPR Color MSX1 File      : %s\n",pNameMapC1);
	printf("SPR Color MSX2 File      : %s\n",pNameMapC2);
	printf("SPR Color MSX2 File (nom): %s\n\n",pNameMapC3);
	
	iError = genDATFile (pNameMapDAT,pSource);
	
 	if (!iError){
		
		printf ("\n");
		return 3;
	}
	
	iError = genC1File (pNameMapC1,pSource);
	
 	if (!iError){
		
		printf ("\n");
		return 4;
	}
	
	iError = genCCCFile (pNameMapC2,pSource,(BYTE)0x20,(BYTE)0x60);
	
 	if (!iError){
		
		printf ("\n");
		return 5;
	}
	
	iError = genCCCFile (pNameMapC3,pSource,(BYTE)0x20,(BYTE)0x20);
	
 	if (!iError){
		
		printf ("\n");
		return 6;
	}
	
	
	
	
	free (pNameMapDAT);
	free (pNameMapC1);
	free (pNameMapC2);
	free (pNameMapC3);
	
	
	free (pSource);
	
	printf ("\nSuccess!!\n\n");
	
    return 0;
}
