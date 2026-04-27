/*
Tareador de binarios
 */

#include <stdlib.h>
#include <stdio.h>
#include <sys/types.h>
#include <sys/stat.h>
#include <unistd.h>
#include <string.h>
#include <strings.h>
#include <ctype.h>

typedef struct
{
		int len;
		char *fname;
}SFILE;

#define LOG(s) printf("%s\n",s)

char strHex[16] = {
		"0123456789ABCDEF"
};


void getNewName (char *namebase, char **name, int counter) {
		
		*name =	(char *) malloc ( strlen(namebase) + 4 );	
		char *pExt = NULL;
		pExt  = (char *) malloc ( 5 );
		
		strcpy (*name,namebase);
		
		// Add Ext
		
		pExt[0] = '.';
		pExt[1] = 'T';
		pExt[2] = strHex[(counter>>4)&0x0F];
		pExt[3] = strHex[(counter&0xF)];
		pExt[4] = 0;
		
		
		
		strcat (*name,pExt);		

        
		free (pExt);


		
		

}

void addHeader (char *name, unsigned char count, int counter) {

		FILE *f_output;
		FILE *in;
		
		
		
		if (counter>0) {


				unsigned char *data;

				data = (unsigned char *) malloc (counter+1);								

				data[0] = count;
				data++;

				in = fopen (name,"rb");
				fread (data,1,counter,in);
				fclose (in);

				f_output = fopen (name,"wb");

				data--;
				fwrite (data,1,counter+1,f_output);

				fflush (f_output);
				fclose (f_output);

		}
		

}


#define BIGENDIAN(value) (((value&0x00FF)<<8)|((value&0xFF00)>>8))

int main (int argc, char *argv[])
{
		SFILE *files;
		
		char *tbin_output;
		char *tbin_output_tmp;
		int input_files;
		struct stat status;
		int i,c;
		FILE *f_output;
		FILE *in;
		int car;
		
		
        
		
		if (argc<3)
		{
				fprintf (stderr,"Usage %s <output> <file.bin> [file.bin...] \n",argv[0]);
				return -1;
		}
		
		tbin_output = argv[1];
		
		input_files = argc-2;
		
		
		
		
		files = (SFILE*) malloc (input_files*sizeof(SFILE));
		
		
		if (input_files <= 1) {
				
				// Creamos los 3 ficheros tarbin, pero vacios
				fprintf (stdout,"Creating empty dummy files ... \n");
				
				f_output = fopen (tbin_output,"wb");
				fclose (f_output);
				
				return	0;
				
		}
		
		
		
		
		

		
		for (i=0;i<input_files;i++)
		{
				files[i].fname=argv[i+2];
				if (stat (files[i].fname,&status)<0)
				{
						perror (files[i].fname);
						free (files);
						return -1;
				}
				
				files[i].len=status.st_size;
		}

		
		/* crea ficheros .tbin*/
		



		i = 0;
		c = 0;
		
		while (c<input_files) {
		
				getNewName(tbin_output,&tbin_output_tmp,i);
				f_output = fopen (tbin_output_tmp,"wb");
				if (!f_output)
				{
						perror (tbin_output_tmp);
						free(files);
						return -1;
				}
		
				// Enrollamos los ficheros dentro

				int counter = 0;
				int counters = 0;
				unsigned char header = 0;
				
				while (counter != -1) {

						if (files[c].len > 8192) {
								c++;
						
						}
						else {
						
								counter += files[c].len;
								
								if ((counter < 8193) && (c < input_files)) {
										in = fopen (files[c].fname,"rb");
										if (!in)
										{
												perror (files[i].fname);
												fclose (f_output);
												free (files);
										}
										
										while ((car=fgetc(in))!=EOF)
										{
												fputc (car,f_output);
												fflush(f_output);
										}
										fflush(f_output);
										fclose (in);
										c++;
										header ++;
										counters = counter;
								}
								else
								{
										
										counter = -1;
										i++;
								}

						}
						

				
						
				}	
				
				
				// Pasa a otro nuevo, a–ado cabecera
				
				fclose (f_output);

				addHeader (tbin_output_tmp,header,counters);
				
		
		}
		
		free (files);
				
		
		fprintf (stdout,"Exit OK!\n");
		
		return 0;

		  
}

