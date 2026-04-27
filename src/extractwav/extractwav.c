
#include	"extractwav.h"

void logo(){
	
	fprintf(stdout,"Extract SCC Wav %s (c) 2009 Kralizec\n\n",VERSION);

}


	


int main(int argc, char* argv[]) {
	
	logo();
	
	if (argc < 2) {
		
		fprintf (stdout,"Usage %s <file.raw> [file.raw...] \n",argv[0]);
		fprintf (stdout,"Creates a separate file.mus and file.wav for file(s).raw\n\n");
		return -1;
		
	}
	
	SFILE*	files;
	struct stat status;	
	int i,w;
	
	int input_files = argc-1;
	files = (SFILE*) malloc (input_files*sizeof(SFILE));
	
	
	for (i=0;i<input_files;i++)
	{
		files[i].fname=argv[i+1];
		if (stat (files[i].fname,&status)<0)
		{
			perror (files[i].fname);
			free (files);
			return -1;
		}
		
		files[i].len=status.st_size;
	}
	
	
	// Create a SCC wav file and MUS files
	
	FILE* filewav;
	
	
	// Create a wav file
	filewav = fopen ("SCCWAV.DAT","wb");
	
	if (!filewav) {
		free (files);
		fprintf (stdout,"Error creating SCC Wav file... \n\n");
		return -1;
	}
	
	// Creates a empty SCC Wav Channel 
	
	SCCWAVCHANNEL*	sccActWaves;
	SCCWAVCHANNEL*	sccStoreWaves;
	
	
	sccActWaves		= (SCCWAVCHANNEL*) malloc (WAVCHANNELS*sizeof(SCCWAVCHANNEL));
	sccStoreWaves	= (SCCWAVCHANNEL*) malloc (MAXWAVES*sizeof(SCCWAVCHANNEL));
	
	if ((!sccActWaves) || (!sccStoreWaves) ){
		fclose (filewav);	
		free (files);
		fprintf (stdout,"Error allocating memory... \n\n");
		return -1;
	}
	
	
	for (i = 0; i < WAVCHANNELS ; i++) {
		
		for (w = 0; w < 32 ; w ++) {
			sccActWaves[i].wav[w] = (BYTE) 0;
		}
		
		
	};
	
	int countWaves = 0;
	int countFiles = 0;
	
	// Bucle de ficheros
	
	while (countFiles < input_files) {
		
		
		
		FILE* in;
		in = fopen (files[countFiles].fname,"rb");
		
		if (!in) {
			
			fclose (filewav);		
			free (files);		
			free (sccActWaves);
			
			fprintf (stdout,"Error opening file %s ... \n\n",files[countFiles].fname);
			return -1;
			
		}
		
		// Read all file
		
		BYTE*	dataFile;
		
		dataFile = (BYTE*) malloc (sizeof(BYTE) * files[countFiles].len);
		fread (dataFile,1,files[countFiles].len,in);
		
		// Create an empty mus file
		
		FILE*	filemus;
		char*	name =	(char *) malloc ( strlen(files[countFiles].fname) + 4 );	
		strcpy (name,files[countFiles].fname);
		char*	pExt  = (char *) malloc ( 5 );
		pExt[0] = '.';
		pExt[1] = 'M';
		pExt[2] = 'U';
		pExt[3] = 'S';
		pExt[4] = 0;
		strcat (name,pExt);		
		filemus = fopen (name,"wb");
		
		free(pExt);
		free(name);
		
		
		i = 0;
		
		while (i < files[countFiles].len) {
			
			BOOL	changeWave = FALSE;
			BOOL	changeW[WAVCHANNELS] = {FALSE,FALSE,FALSE,FALSE};
			BOOL	putChange = FALSE;
			
			while (dataFile[i] != ENDFRAME) {
				
				
				switch (dataFile[i]) {
					case PSGDATA:
					case SCCDATA:				
						fputc  (dataFile[i],filemus);
						fflush (filemus);
						i++;
						do {
							
							fputc  (dataFile[i],filemus);
							fflush (filemus);
							i++;
							fputc  (dataFile[i],filemus);
							fflush (filemus);
							i++;
							
							
						} while ( (dataFile[i] != PSGDATA ) && (dataFile[i]!= SCCDATA) && 
								  (dataFile[i] != ENDFRAME) && (dataFile[i]!= SCCWAVEDATA) );
							
							break;
						
					case SCCWAVEDATA:
						
						// Introducir las waves dentro de nuestras waves temporales
						i++;
						changeWave = TRUE;
						
						
						
						do {
							
							int wc = dataFile[i++];
							int wd = dataFile[i++];
							sccActWaves[wc>>5].wav[wc&0x1F] = wd;
							changeW[wc>>5] = TRUE;
							
						} 
							while ( (dataFile[i] != PSGDATA ) && (dataFile[i]!= SCCDATA) && 
									(dataFile[i] != ENDFRAME) && (dataFile[i]!= SCCWAVEDATA) );
							
							
							break;
						
						
						
				};
				
				
			};
			
			int x,y,z;
			
			if (changeWave) {
				
				
				// La primera siempre
				if (!countWaves) {
					sccStoreWaves[countWaves] =  sccActWaves[0];
					for (x = 0; x < 32 ; x++) {
						fputc(sccStoreWaves[0].wav[x],filewav);
					}
					countWaves++;
				}
				
				for (y = 0; y < WAVCHANNELS; y++) {
					
					BOOL wavEqual = FALSE;
					for (x = 0; x < countWaves ; x++) {
						
						if (!wavEqual) {
							wavEqual = TRUE;
							for (z = 0; z < 32 ; z++) {
								
								if (sccActWaves[y].wav[z] != sccStoreWaves[x].wav[z]) {
									wavEqual = FALSE;
								}
							}
							
							if (wavEqual) {
								if (changeW[y]) {
								    if (!putChange) {
										fputc  (SCCWAVEDATA,filemus);	// Token
										putChange=TRUE;
									}
									fputc  ((BYTE)y,filemus);		// Channel
									fputc  ((BYTE)x,filemus);		// Value Wave
								} 
							}
							
							
						}
					}
					
					
					
					if (!wavEqual) {
						sccStoreWaves[countWaves] = sccActWaves[y];
						
						if (changeW[y]) {
						
							if (!putChange) {
								fputc  (SCCWAVEDATA,filemus);	// Token
								putChange=TRUE;
							}
							fputc  ((BYTE)y,filemus);		// Channel
							fputc  ((BYTE)countWaves,filemus);
							
						}
						for (x = 0; x < 32 ; x++) {
							fputc(sccStoreWaves[countWaves].wav[x],filewav);
						}
						countWaves++;					
						
					}
					
				}
				
			}
			
			
			// End frame 
			fputc  (dataFile[i],filemus);
			fflush (filemus);
			i++;
			
			
			
			
		};
		
	countFiles++;
	fclose (filemus);
	free (dataFile);
		
	};
	
	
	
	fclose (filewav);
	free (files);
	free (sccActWaves);
	free (sccStoreWaves);
	fprintf (stdout,"Finished Ok!\n");
	return 0;
}


