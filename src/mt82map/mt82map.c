#include <stdio.h>
#include <stdlib.h>
#include <stdio.h>
#include <string.h>
#include <math.h>
#include <ctype.h>

/* *** DEFINES *** */



#define BYTE unsigned char


/* LOGO */

void printLogo (void) {
	
	printf ("\nMT8 To MAP v 0.1 MSX MT8 map conversion Tool (c) 2006 Kralizec \n\n");
	
	
}


/* USAGE */

void printUsage (void) {
	
	printf ("Usage: MT82MAP source width height \n\n");
	printf ("Example: \n");
	printf ("        MT82MAP PANGMAP 10 2 \n\n");
	printf ("Creates a PANGMAP.MAP file from PANGMAP.xxx files ...\n\n");
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


void fillDat (BYTE *pMap, BYTE *pDat, int iWidth8) {

	int x,y;
	
	for (y = 0; y < 24; y++) {
	
		for (x = 0; x < 32; x ++) {
			
			*pMap++ = *pDat++;
		
		}
		
	
		pMap  += iWidth8 - 32;
		
	}


}


int fillMT8 (BYTE *pMap, char *pNameSource, int x, int y, int iWidth8) {

	char Let[2];
	char Num[2];
	
	Let[0] = 'A' + y;
	Let[1] = 0;
	sprintf(Num,"%d",x);
	
	
	char *pNameFile = NULL;
	
	pNameFile = (char *) malloc (strlen(pNameSource) + 3 + 4);
	memset(pNameFile,0,(strlen(pNameSource) + 3 + 4)+1);
	
	strcat (pNameFile,pNameSource);
	strcat (pNameFile,Let);
	strcat (pNameFile,Num);
	strcat (pNameFile,".MT8");
	
	
	printf("Processing %s file : ",pNameFile);
	
	// Read File
	
	FILE *pflSRC = NULL;
	
	long wSize = 0;
	long wRead = 0;	
	
	
	if (! (pflSRC = fopen (pNameFile,"rb")) ){
		
		printf ("Error!\n");
		printf ("Problems opening source file %s \n",pNameFile);
		return 1;
	}
	
	
	
	fseek ( pflSRC, -1, SEEK_END);
	wSize = ftell ( pflSRC);
	wSize++;
	
	fseek ( pflSRC, 0, SEEK_SET);
	
	BYTE *pSRC = NULL;
	
	pSRC = (BYTE *) malloc (sizeof (BYTE) * (int) wSize);
	
	
	if (!pSRC){
		printf ("Error!\n");
		printf ("Problems allocating memory ... \n");
		fclose (pflSRC);
		return 1;
	}
	
	
	wRead = fread  ( pSRC, 1, wSize, pflSRC);
	if ( wRead == 0)
    {
		printf ("Error!\n");
        printf ("Can't read source file %s\n", pNameFile);
		return 1;
    }	

	fclose (pflSRC);	
	

	fillDat(pMap,pSRC,iWidth8);
	
	printf ("OK!\n");
	
	free (pSRC);
	free (pNameFile);
	
	
	
	

	return 0;



} 


int createMapFile (BYTE *pMap, char *pNameSource, int iWidthMap, int iHeightMap, int iSize)
{

	int x,y;
	
	for (y = 0; y < iHeightMap; y++){

		for (x = 0; x < iWidthMap; x ++) {
		
			int i = (x*32) + (y*((32*iWidthMap)*24));
		
			int iError = fillMT8(&pMap[i],pNameSource,x,y,iWidthMap*32);
		
			if (iError) {
				return iError;
			}
		
		}
	
	
	}
	




	
	// Write file

	char *pNameFile = NULL;
	pNameFile = (char*) malloc (strlen(pNameSource) + 5);
	memset(pNameFile,0,strlen(pNameSource) + 5);





	strcat (pNameFile,pNameSource);
	strcat (pNameFile,".MAP");

	printf ("\nWriting MAP file %s: " ,pNameFile);


	FILE *pflTemp = NULL;
	long wWrote = 0;
	
	
	pflTemp = fopen (pNameFile,"wb");
	
	if (!pflTemp) {
		printf ("Error!\n");
		printf ("Can't write file %s\n",pNameFile);		
		return 0;
	}
	
	wWrote = fwrite  ( pMap, 1,iSize, pflTemp);
	
	if (!wWrote) {
		printf ("Error!\n");	
		printf ("Can't write file %s\n",pNameFile);	
		return 0;	
	}
	
	
	printf ("OK!\n");	
	fflush(pflTemp);
	fclose(pflTemp);
	free (pNameFile);




	return 0;
}


int main (int argc, const char * argv[]) {

 	// Check arguments
	printLogo();
	
	if (argc < 4) {
		printUsage();
		return 1;
	}
	
	
	int iWidthMap, iHeightMap;
	int iWidth8, iHeight8;
	int iWidth, iHeight;


	
	iWidthMap = atoi (argv[2]);
	iHeightMap = atoi (argv[3]);
	
	iWidth8 = 32 * iWidthMap;
	iWidth = 8 * iWidth8;
	
	iHeight8 = 24 * iHeightMap;
	iHeight = 8 * iHeight8;
	
	printf("Processing MT8 files ...\n\n");

	printf("Width Maps  : %i \n",iWidthMap);
	printf("Width Tiles : %i \n",iWidth8);
	printf("Width Res X : %i \n\n",iWidth);

	printf("Height Maps  : %i \n",iHeightMap);
	printf("Height Tiles : %i \n",iHeight8);
	printf("Height Res Y : %i \n\n",iHeight);



	

	
	
	
	BYTE *pMap = NULL;
	
	// Alloc Mem
	
	pMap = (BYTE *) malloc ((iWidth8 * iHeight8)+1);
	memset(pMap,0,(iWidth8*iHeight8)+1);
	
	int iError = 0;
	
	iError = createMapFile(pMap,(char*)argv[1],iWidthMap,iHeightMap,(iWidth8*iHeight8));

	


	free(pMap);

	if (iError) {
	
		printf("\nProblems creating MAP file... Exit!\n");
		return iError;
	}


	printf ("\nSuccess!!\n");

    return 0;
}
