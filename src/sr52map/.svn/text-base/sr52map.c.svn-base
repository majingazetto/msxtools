#include <stdlib.h>
#include <stdio.h>
#include <string.h>
#include <math.h>
#include <ctype.h>

/* *** DEFINES *** */

#define PT8		0
#define PT16  64 * 128
#define PTE  128 * 128

#define nTiles8x		32
#define nTiles8y		24
#define	nTiles16y		nTiles8y>>1
#define	nTiles16x		nTiles8x>>1


#define nTilesSety  8

#define BYTE unsigned char


// ------------------------------------------------------------------------------

/* *** TEXT ROUTINES ***/

/* LOGO */

void printLogo (void) {
		
		printf ("\nSR5 To Map v 0.1 Map conversion Tool (c) 2009 Kralizec \n\n");
		
		
}

/* USAGE */

void printUsage (void) {
		
		printf ("Usage: SR52MAP source mapfile charadd (optional)\n\n");
		printf ("Example: \n");
		printf ("        SR52MAP MAPSR5.SR5 MAP01.SR5\n\n");
		printf ("Creates a MAP01 files from MAP01.SR5...\n\n");
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



int createNewMapFiles (char *pNameMap, char **pNameT8, char **pNameT16, char **pNameT16Ext, 
				       char **pNameTE) {
		
		*pNameT8  	 = (char *) malloc ( strlen(pNameMap) );
		*pNameT16 	 = (char *) malloc ( strlen(pNameMap) );
		*pNameT16Ext = (char *) malloc ( strlen(pNameMap) );
		*pNameTE   	 = (char *) malloc ( strlen(pNameMap) );	
				
		char *pExt = NULL;
		char *pWExt = NULL;
		
		pExt  = (char *) malloc ( strlen(pNameMap) );
		pWExt = (char *) malloc ( strlen(pNameMap) );	
		
		if ( (!*pNameT8) || (!*pNameT16) || (!pNameT16Ext) || (!*pNameTE)  || (!pExt) || (!pWExt) )
		{
				return 1;
		}
		
		ExtractExt(pNameMap,pExt,pWExt);
		
		// Create Name files 
		
		strcpy (*pNameT8,pWExt);
		strcpy (*pNameT16,pWExt);
		strcpy (*pNameT16Ext,pWExt);
		strcpy (*pNameTE,pWExt);
		
		// Add Extension
		
		strcat (*pNameT8,"MT8");
		strcat (*pNameT16,"MT6");
		strcat (*pNameT16Ext,"ME6");
		strcat (*pNameTE,"MTE");
		
		
		
		free (pExt);
		free (pWExt);
		return	0;
		
		
}


// ------------------------------------------------------------------------------


/* *** FILE ROUTINES *** */

int readFilesSR5 (char *pNameSRC, char *pNameMAP, BYTE **pSRC, BYTE **pMAP){
		
		FILE *pflSRC = NULL;
		FILE *pflMAP = NULL;
		long wSize = 0;
		long wRead = 0;
		
		long wSize2 = 0;
		long wRead2 = 0;
		
		
		if (! (pflSRC = fopen (pNameSRC,"rb")) ){
				
				printf ("Problems opening source file %s \n",pNameSRC);
				return 0;
		}
		
		if (! (pflMAP = fopen (pNameMAP,"rb")) ){
				
				printf ("Problems opening map file %s \n",pNameMAP);
				return 0;
		}
		
		
		// Read SOURCE file 
		
		fseek ( pflSRC, -1, SEEK_END);
		wSize = ftell ( pflSRC);
		wSize++;
		wSize -=7;
		
		fseek ( pflSRC, 7, SEEK_SET);
		
		*pSRC = (BYTE *) malloc (sizeof (BYTE) * (int) wSize);
		
		// Read MAP file
		
		fseek ( pflMAP, -1, SEEK_END);
		wSize2 = ftell ( pflMAP);
		wSize2++;
		wSize2 -=7;
		
		fseek ( pflMAP, 7, SEEK_SET);
		
		*pMAP = (BYTE *) malloc (sizeof (BYTE) * (int) wSize2);
		
		
		if ((!*pSRC)  || (!*pMAP)){
				printf ("Problems allocating memory ... \n");
				fclose (pflSRC);
				fclose (pflMAP);
				return 0;
		}
		
		
		wRead = fread  ( *pSRC, 1, wSize, pflSRC);
		if ( wRead == 0)
		{
				printf ("Can't read source file %s\n", pNameSRC);
				return 0;
		}
		
		wRead2 = fread  ( *pMAP, 1, wSize, pflMAP);
		if ( wRead2 == 0)
		{
				printf ("Can't read map file %s\n", pNameMAP);
				return 0;
		}
		
		printf ("Source file   : %s\n",pNameSRC);
		printf ("Map file      : %s\n",pNameMAP);
		
		
		
		fclose (pflSRC);
		fclose (pflMAP);	
		
		
		return 1;
}


// ------------------------------------------------------------------------------

/* PROGRAM ROUTINES */

// Compare 2 SR5 Tiles 8x8 size

int cmpSR5T8 (BYTE *pT81, BYTE *pT82) {
		
		int x,y,src;
		for (y = 0; y < 8 ; y++){
				
				src = (y<<7);
				
				for (x = 0; x < 4 ; x ++ ) {
						
						
						if (pT81[src] != pT82[src]) {
								
								return 0;
						}
						src++;
				}
		}
		
		
		return 1;
}

// Compare 2 SR5 Tiles 16x16 size

int cmpSR5T16 (BYTE *pT161, BYTE *pT162) {
		
		int x,y,src;
		int noreturn = 0;
		for (y = 0; y < 16 ; y++){
				
				src = (y<<7);
				
				for (x = 0; x < 8 ; x ++ ) {
						
						if	((pT161[src] != 0) || (pT162[src] != 0)) {
								noreturn = 1;
						}
						
						if (pT161[src] != pT162[src]) {
								
								return 0;
						}
						src++;
				}
		}
		
		
		
		return noreturn;
}


int cmpSR5T162 (BYTE *pT161, BYTE *pT162) {
		
		int x,y,src;
		for (y = 0; y < 16 ; y++){
				
				src = (y<<7);
				
				for (x = 0; x < 8 ; x ++ ) {
						
						if (pT161[src] != pT162[src]) {
								
								return 0;
						}
						src++;
				}
		}
		
		
		
		return 1;
}



// Extract tile number of pPos of Map

BYTE extractT8 (BYTE *pSource, BYTE *pPos, int iAdd,int xm, int ym) {
		
		int x,y,src;
		BYTE tile;
		
		tile = 0;
		for (y = 0; y < nTilesSety ; y++) {
				
				
				for (x = 0 ; x < nTiles8x ; x ++) {
						
						src = (y << 10) + (x << 2);
						
						
						if (cmpSR5T8(&pSource[src],pPos)) {
								
								return tile + iAdd;
						}
						
						tile++;
				}
				
		} 
		
		// Hemos tenido un error lo printeamos en el LOG
		
		printf ("\n    ERROR: Tile not Found!!!\n");
		printf ("       Tile X : %i Tile Y: %i X: %i Y: %i NumTile : %i\n",xm,ym,xm*8,ym*8,(ym*32)+xm);
		
		return 0;
}


// Extract tile number of pPos of Map

int extractT16 (BYTE *pSource, BYTE *pPos) {
		
		int x,y,src;
		BYTE tile;
		
		tile = 0;
		for (y = 0; y < (nTilesSety >>1) ; y++) {
				
				
				for (x = 0 ; x < (nTiles8x >>1) ; x ++) {
						
						src = (y << 11) + (x << 3);
						
						
						// Check if src is empty
						if (cmpSR5T16(&pSource[src],pPos)) {
								
								return (tile & 0xFF);
						}
						
						tile++;
				}
				
		} 
		
		
		
		
		return 256;
}


int extractT162 (BYTE *pSource, BYTE *pPos) {
		
		int x,y,src;
		BYTE tile;
		
		tile = 0;
		
		

		
		for (y = 0; y < (nTilesSety >>1) ; y++) {
				
				
				for (x = 0 ; x < (nTiles8x >>1) ; x ++) {
						
						src = (y << 11) + (x << 3);
						
						
						if (cmpSR5T162(&pSource[src],pPos)) {
								
								return (tile & 0xFF);
						}
						
						tile++;
				}
				
		} 
		
		
		
		
		return 0;
}




// Generate MT8 file.

int genT8File (char *pNameFile, BYTE *pSRC, BYTE *pMAP, int iAdd){
		
		printf ("Generating T8 file : %s",pNameFile);
		
		BYTE *pTemp = NULL;
		pTemp = (BYTE *) malloc (nTiles8x * nTiles8y);
		
		if (!pTemp) {
				printf ("\nProblems allocating memory ... \n");
				return 0;
				
		}
		
		// Fill with 0
		
		memset(pTemp,0,nTiles8x * nTiles8y);
		
		int i = 0;
		int x,y,src;
		
		for (y = 0; y < nTiles8y ; y++) {
				
				
				for (x = 0; x < nTiles8x ; x++) {
						
						src = (y << 10) + (x<<2);
						pTemp[i] = extractT8(pSRC,&pMAP[src],iAdd,x,y);
						
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
		
		wWrote = fwrite  ( pTemp, 1,nTiles8x * nTiles8y, pflTemp);
		
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

// Generate MT16 file

int genT16File (char *pNameFile, BYTE *pSRC, BYTE *pMAP){
		
		printf ("Generating T16 file : %s",pNameFile);
		
		BYTE *pTemp = NULL;
		pTemp = (BYTE *) malloc ((nTiles8x * nTiles8y)<<2);
		
		
		
		
		
		if (!pTemp) {
				printf ("\nProblems allocating memory ... \n");
				return 0;
				
		}
		
		memset(pTemp,0,(nTiles8x * nTiles8y)<<1);
		
		int i = 0;
		int x,y,src,tile;
		
		for (y = 0; y < nTiles16y ; y++) {
				
				
				for (x = 0; x < nTiles16x ; x++) {
						
						src = (y << 11) + (x<<3);
						
						

						tile = extractT162(pSRC,&pMAP[src]);
						
						
						
						pTemp[i++] = (BYTE) (tile & 0xFF);
				}
		}
		
		// Write file
		
		if (i >0) {
				
				FILE *pflTemp = NULL;
				long wWrote = 0;
				
				
				pflTemp = fopen (pNameFile,"wb");
				
				if (!pflTemp) {
						
						printf ("\nCan't write file %s\n",pNameFile);		
						return 0;
				}
				
				wWrote = fwrite  ( pTemp, 1,i, pflTemp);
				
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
		
		printf (" No info!\n");
		return 0;
		
}





int genT16ExtFile (char *pNameFile, BYTE *pSRC, BYTE *pMAP){
		
		printf ("Generating T16 Extended file : %s",pNameFile);
		
		BYTE *pTemp = NULL;
		pTemp = (BYTE *) malloc ((nTiles8x * nTiles8y)<<2);
		
		
		
		
		
		if (!pTemp) {
				printf ("\nProblems allocating memory ... \n");
				return 0;
				
		}
		
		memset(pTemp,0,(nTiles8x * nTiles8y)<<1);
		
		int i = 0;
		int x,y,src,tile,comp;
		
		
		for (y = 0; y < nTiles8y ; y++) {
				
				
				for (x = 0; x < nTiles8x ; x++) {
						
						src = (y << 10) + (x << 2);
						
						

						tile = extractT16(pSRC,&pMAP[src]);
						if (tile != 256) {
						
						
							comp 	=  ( ( (x << 11) & 0xF800) | ( (y << 6) & 0x07C0) | (tile & 0x3F) );
				
							pTemp[i++] = ((comp & 0xFF00) >> 8);
							pTemp[i++] = (comp & 0x00FF);
						
						
						}
						
						
						
				}
		}
		
		// Ending 
		
		if	(i > 0) {
		
		pTemp[i++] = 0xFF;
		pTemp[i++] = 0xFF;
		
		}
		
		
		// Write file
		
		if (i >0) {
				
				FILE *pflTemp = NULL;
				long wWrote = 0;
				
				
				pflTemp = fopen (pNameFile,"wb");
				
				if (!pflTemp) {
						
						printf ("\nCan't write file %s\n",pNameFile);		
						return 0;
				}
				
				wWrote = fwrite  ( pTemp, 1,i, pflTemp);
				
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
		
		printf (" No info!\n");
		return 0;
		
}




// ------------------------------------------------------------------------------

/* *** MAIN  *** */

int main (int argc, const char * argv[]) {
		
		// Check arguments
		printLogo();
		
		if (argc < 3) {
				printUsage();
				return 1;
		}
		
		// Options por defecto 
		
		
		
		
		int iError = 0;
		BYTE *pSource = NULL;
		BYTE *pMap = NULL;
		
		
		iError = readFilesSR5 ((char *) argv[1], (char*) argv[2],&pSource,&pMap);
		

		
		
		if (!iError)
		{	
				printf ("\n");
				return 2;
		}

		
		char *pNameMapT8 = NULL;
		char *pNameMapT16 = NULL;
		char *pNameMapT16Ext = NULL;
		char *pNameMapTE = NULL;


		int iAdd = 0;

		

		
		if (argc>3) {
			
				iAdd = atoi (argv[3]);
		}


		
		iError = createNewMapFiles ((char*)argv[2],&pNameMapT8,&pNameMapT16,&pNameMapT16Ext,&pNameMapTE);
		
		

		
		if (iError!=0){
				
				printf ("Problems allocating mem ...\n");
				return 3;
		}
		
		
		printf("\nTiles 8 File  : %s\n",pNameMapT8);
		printf("Tiles 16 File : %s\n",pNameMapT16);
		printf("Tiles 16 Extended File : %s\n",pNameMapT16Ext);
		printf("Tiles E File  : %s\n\n",pNameMapTE);
		
		iError = genT8File (pNameMapT8,&pSource[PT8],pMap,iAdd);
		

		
		if (!iError) {
				
			//	return 4;
		}
		
		
		iError = genT16File (pNameMapT16,&pSource[PT16],pMap);
		
		
		if (!iError) {
				
			//	return 5;
		}
		
		// Generate MT6EXT File
		
		iError = genT16ExtFile (pNameMapT16Ext,&pSource[PT16],pMap);
		
		if (!iError) {
				
				//return 6;
		}
		
	
		// Enemies	
		
		iError = genT16ExtFile (pNameMapTE,&pSource[PTE],pMap);
		
		
		if (!iError) {
				
			//	return 7;	
		}
		
		
		printf("\nSuccess!!\n\n");
		
		free (pNameMapTE);
		free (pNameMapT16);
		free (pNameMapT16Ext);
		free (pNameMapT8);
		free (pSource);
		free (pMap);
		
		
		
		return 0;
		
}

