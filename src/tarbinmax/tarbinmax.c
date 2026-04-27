/*
 Tareador de binarios
 */

#include <stdlib.h>
#include <stdio.h>
#include <sys/types.h>
#include <sys/stat.h>
#include <unistd.h>
#include <string.h>
#include <ctype.h>

typedef struct
{
	int len;
	char *fname;
}SFILE;

#define LOG(s) printf("%s\n",s)

unsigned short CRC_Table[256] = {
	0x0000U, 0x1021U, 0x2042U, 0x3063U, 0x4084U, 0x50a5U, 0x60c6U, 0x70e7U,
	0x8108U, 0x9129U, 0xa14aU, 0xb16bU, 0xc18cU, 0xd1adU, 0xe1ceU, 0xf1efU,
	0x1231U, 0x0210U, 0x3273U, 0x2252U, 0x52b5U, 0x4294U, 0x72f7U, 0x62d6U,
	0x9339U, 0x8318U, 0xb37bU, 0xa35aU, 0xd3bdU, 0xc39cU, 0xf3ffU, 0xe3deU,
	0x2462U, 0x3443U, 0x0420U, 0x1401U, 0x64e6U, 0x74c7U, 0x44a4U, 0x5485U,
	0xa56aU, 0xb54bU, 0x8528U, 0x9509U, 0xe5eeU, 0xf5cfU, 0xc5acU, 0xd58dU,
	0x3653U, 0x2672U, 0x1611U, 0x0630U, 0x76d7U, 0x66f6U, 0x5695U, 0x46b4U,
	0xb75bU, 0xa77aU, 0x9719U, 0x8738U, 0xf7dfU, 0xe7feU, 0xd79dU, 0xc7bcU,
	0x48c4U, 0x58e5U, 0x6886U, 0x78a7U, 0x0840U, 0x1861U, 0x2802U, 0x3823U,
	0xc9ccU, 0xd9edU, 0xe98eU, 0xf9afU, 0x8948U, 0x9969U, 0xa90aU, 0xb92bU,
	0x5af5U, 0x4ad4U, 0x7ab7U, 0x6a96U, 0x1a71U, 0x0a50U, 0x3a33U, 0x2a12U,
	0xdbfdU, 0xcbdcU, 0xfbbfU, 0xeb9eU, 0x9b79U, 0x8b58U, 0xbb3bU, 0xab1aU,
	0x6ca6U, 0x7c87U, 0x4ce4U, 0x5cc5U, 0x2c22U, 0x3c03U, 0x0c60U, 0x1c41U,
	0xedaeU, 0xfd8fU, 0xcdecU, 0xddcdU, 0xad2aU, 0xbd0bU, 0x8d68U, 0x9d49U,
	0x7e97U, 0x6eb6U, 0x5ed5U, 0x4ef4U, 0x3e13U, 0x2e32U, 0x1e51U, 0x0e70U,
	0xff9fU, 0xefbeU, 0xdfddU, 0xcffcU, 0xbf1bU, 0xaf3aU, 0x9f59U, 0x8f78U,
	0x9188U, 0x81a9U, 0xb1caU, 0xa1ebU, 0xd10cU, 0xc12dU, 0xf14eU, 0xe16fU,
	0x1080U, 0x00a1U, 0x30c2U, 0x20e3U, 0x5004U, 0x4025U, 0x7046U, 0x6067U,
	0x83b9U, 0x9398U, 0xa3fbU, 0xb3daU, 0xc33dU, 0xd31cU, 0xe37fU, 0xf35eU,
	0x02b1U, 0x1290U, 0x22f3U, 0x32d2U, 0x4235U, 0x5214U, 0x6277U, 0x7256U,
	0xb5eaU, 0xa5cbU, 0x95a8U, 0x8589U, 0xf56eU, 0xe54fU, 0xd52cU, 0xc50dU,
	0x34e2U, 0x24c3U, 0x14a0U, 0x0481U, 0x7466U, 0x6447U, 0x5424U, 0x4405U,
	0xa7dbU, 0xb7faU, 0x8799U, 0x97b8U, 0xe75fU, 0xf77eU, 0xc71dU, 0xd73cU,
	0x26d3U, 0x36f2U, 0x0691U, 0x16b0U, 0x6657U, 0x7676U, 0x4615U, 0x5634U,
	0xd94cU, 0xc96dU, 0xf90eU, 0xe92fU, 0x99c8U, 0x89e9U, 0xb98aU, 0xa9abU,
	0x5844U, 0x4865U, 0x7806U, 0x6827U, 0x18c0U, 0x08e1U, 0x3882U, 0x28a3U,
	0xcb7dU, 0xdb5cU, 0xeb3fU, 0xfb1eU, 0x8bf9U, 0x9bd8U, 0xabbbU, 0xbb9aU,
	0x4a75U, 0x5a54U, 0x6a37U, 0x7a16U, 0x0af1U, 0x1ad0U, 0x2ab3U, 0x3a92U,
	0xfd2eU, 0xed0fU, 0xdd6cU, 0xcd4dU, 0xbdaaU, 0xad8bU, 0x9de8U, 0x8dc9U,
	0x7c26U, 0x6c07U, 0x5c64U, 0x4c45U, 0x3ca2U, 0x2c83U, 0x1ce0U, 0x0cc1U,
	0xef1fU, 0xff3eU, 0xcf5dU, 0xdf7cU, 0xaf9bU, 0xbfbaU, 0x8fd9U, 0x9ff8U,
	0x6e17U, 0x7e36U, 0x4e55U, 0x5e74U, 0x2e93U, 0x3eb2U, 0x0ed1U, 0x1ef0U
};

#define BIGENDIAN(value) (((value&0x00FF)<<8)|((value&0xFF00)>>8))

int main (int argc, char *argv[])
{
	SFILE *files;

	char *tbin_output;
	char *h_output;
	char *z8a_output;
	char *z8a_include_output;
	int input_files;
	struct stat status;
	int i,c;
	FILE *f_output;
  	FILE *f_output_h;
	FILE *f_z8a_output;
	FILE *f_z8a_include_output;
	FILE *in;
	int car;
	unsigned short crc;
	int totalsize;
    int maxsize;

	if (argc<6)
	{
		fprintf (stderr,"Usage %s <output.tbin> <output.h> <output.z8a> <output_include.z8a> <maxsize>  <file.bin> [file.bin...]\n",argv[0]);
		return -1;
	}

	tbin_output = argv[1];
	h_output = argv[2];
	z8a_output = argv[3];
	z8a_include_output = argv[4];
	maxsize = atoi(argv[5]);

	input_files = argc-6;



	files = (SFILE*) malloc (input_files*sizeof(SFILE));
		
	fprintf (stdout,"Files -> %i\n",input_files);

		if (input_files < 1) {
		
				// Creamos los 3 ficheros tarbin, pero vacios
				fprintf (stdout,"Creating empty dummy files ... \n");
				

				f_output_h = fopen (h_output,"wb");
				f_z8a_output = fopen (z8a_output,"wb");
				f_z8a_include_output = fopen (z8a_include_output,"wb");
				f_output = fopen (tbin_output,"wb");


    			fflush (f_output);
           		fflush (f_z8a_output);
	    		fflush (f_z8a_include_output);
                fflush (f_output);
                
                fclose (f_output);
				fclose (f_z8a_include_output);
                fclose (f_z8a_output);
				fclose (f_output_h);

                free(files);
				return	0;

		}



    totalsize = 0;
	for (i=0;i<input_files;i++)
	{
		files[i].fname=argv[i+6];

        

		if (stat (files[i].fname,&status)<0)
		{
		
				
			perror (files[i].fname);
			free (files);
			
			// Creamos los 3 ficheros tarbin, pero vacios
			fprintf (stdout,"Creating empty dummy files ... \n");
				
				
			f_output = fopen (h_output,"wb");
			f_z8a_output = fopen (z8a_output,"wb");
			f_z8a_include_output = fopen (z8a_include_output,"wb");
            f_output = fopen (tbin_output,"wb");


			fflush (f_output);
			fflush (f_z8a_output);
			fflush (f_z8a_include_output);
            fflush (f_output);
           

			fclose (f_output);
			fclose (f_z8a_output);
			fclose (f_z8a_include_output);
            fclose (f_output);
			
			

			return	0;
			
		
		}

		files[i].len=status.st_size;
		totalsize += files[i].len;
	}

    // Error de size

    if (totalsize > maxsize) {
        free (files);
    	fprintf (stderr,"Size of File > Maxsize ... \n");

        return -1;

    }


    


	/* crea fichero .tbin*/

	f_output = fopen (tbin_output,"wb");
	if (!f_output)
	{
		perror (tbin_output);
		free(files);
		return -1;
	}


	/* Enrolla */

	for (i=0;i<input_files;i++)
	{
		in = fopen (files[i].fname,"rb");
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
	}

	fclose (f_output);


	/* Calculo de CRC-16 */

	crc = 0;

	in = fopen (tbin_output,"rb");
	if (!in) {
		perror (tbin_output);
		free (files);
	}

	while ((car=fgetc(in))!=EOF){
		crc = CRC_Table[(crc >> 8 ^ car) & 0xffU] ^ (crc << 8);
	}
	fclose (in);


	/* Crea header (indice)   y  tabla z8a y tabla_include.z8a */

	
	
	
	f_output = fopen (h_output,"wb");
	f_z8a_output = fopen (z8a_output,"wb");
	f_z8a_include_output = fopen (z8a_include_output,"wb");
	
	if (!f_output)
	{
		perror (h_output);
		free(files);
		return -1;
	}
	

	if (!f_z8a_output)
	{
		perror (z8a_output);
		free(files);
		return -1;
	}
	
	if (!f_z8a_include_output)
	{
		perror (z8a_output);
		free(files);
		return -1;
	}

	
	
	fprintf (f_output,"/**********************************************\n");
	fprintf (f_output,"\n");
	fprintf (f_output,"          Autogenerated by %s \n",argv[0]);
	fprintf (f_output,"\n");
	fprintf (f_output,"             DO NOT EDIT !!!!!!!!\n");
	fprintf (f_output,"\n");
	fprintf (f_output,"***********************************************/\n");
	fprintf (f_output,"\n\n\n");
	fprintf (f_output,"/*\n");
	fprintf (f_output," Indexes for file: %s\n\n",tbin_output);
	fprintf (f_output," This file contains:\n\n");

	fprintf (f_z8a_output,"/**********************************************\n");
	fprintf (f_z8a_output,"\n");
	fprintf (f_z8a_output,"          Autogenerated by %s \n",argv[0]);
	fprintf (f_z8a_output,"\n");
	fprintf (f_z8a_output,"             DO NOT EDIT !!!!!!!!\n");
	fprintf (f_z8a_output,"\n");
	fprintf (f_z8a_output,"***********************************************/\n");
	fprintf (f_z8a_output,"\n\n\n");

	fprintf (f_z8a_include_output,"/**********************************************\n");
	fprintf (f_z8a_include_output,"\n");
	fprintf (f_z8a_include_output,"          Autogenerated by %s \n",argv[0]);
	fprintf (f_z8a_include_output,"\n");
	fprintf (f_z8a_include_output,"             DO NOT EDIT !!!!!!!!\n");
	fprintf (f_z8a_include_output,"\n");
	fprintf (f_z8a_include_output,"***********************************************/\n");
	fprintf (f_z8a_include_output,"\n\n\n");



	// Create table
	
	fprintf	(f_z8a_output,"tarbinfiles:\n");
	
	
	
	
	
	for (i=0;i<input_files;i++)
	{
		fprintf (f_output," %-40s  %d\n",files[i].fname,files[i].len);
	}
	
	// Create incbin files
	fprintf	(f_z8a_include_output,"\n");	
	
	char tmpString[256];
	char crcString[256];
	
	for (i=0;i<input_files;i++)	
	{
	
		strcpy (tmpString,files[i].fname);
		
		// Quitamos  el directorio
		for (c=strlen(tmpString)-1;c>0;c--)
		{
			if ((tmpString[c]=='\\')||(tmpString[c]=='/')){c++; break;}
		}
		
		strcpy (crcString,tmpString+c);
		strcpy (tmpString,crcString);

		// Quitar el punto y cambiar por _

		for (c=strlen(tmpString)-1;c>-1;c--)
		{
			tmpString[c]=toupper(tmpString[c]);
			if ((tmpString[c]=='.')) tmpString[c] = '_';
		}
		
		
	
		fprintf (f_z8a_include_output,"%s:\t\t\tINCBIN\t\t\"%s\"\n",tmpString,files[i].fname);
	}
	
	fflush (f_z8a_include_output);
	

	fprintf (f_output,"*/\n");
	fprintf (f_output,"\n\n\n");

	
	

	strcpy (tmpString,argv[1]);

	for (c=strlen(tmpString)-1;c>0;c--)
	{
		if ((tmpString[c]=='\\')||(tmpString[c]=='/')){c++; break;}
	}
	strcpy (crcString,tmpString+c);
	strcpy (tmpString,crcString);

	for (c=0;c<strlen(tmpString);c++)
	{
		tmpString[c]=toupper(tmpString[c]);
		if ((!isdigit(tmpString[c]))&&(!isalpha(tmpString[c]))) tmpString[c]='_';
	}
	tmpString[c]=0;

	strcpy (crcString,"#define TARBIN_CRC_");
	strcat (crcString,tmpString);

	fprintf (f_output,"%-40s 0x%X\n\n",crcString,crc);

	int ptr=0;

	for (i=0;i<input_files;i++)
	{
		char fname[256];
		char upname[256];
		char define[256];

		for (c=strlen(files[i].fname)-1;c>0;c--)
		{
		if ((files[i].fname[c]=='\\')
		    ||(files[i].fname[c]=='/')){c++; break;}
		}
		fname[0]=0;
		strcpy (fname,files[i].fname+c);

		for (c=0;c<strlen(fname);c++)
		{
			upname[c]=toupper(fname[c]);
			if ((!isdigit(upname[c]))
			   &&(!isalpha(upname[c]))) upname[c]='_';
		}
		
		// Create point name

		upname[c]=0;
		sprintf (define,"#define TARBIN_%s_NAME",upname);
		fprintf (f_output,"%-40s %d\n",define,i);
		
		
		
		upname[c]=0;
		sprintf (define,"#define TARBIN_%s",upname);
		fprintf (f_output,"%-40s %d\n",define,ptr);
		
		// Z80 extra Create TWO defines for HIGH LOW POINTER
		
		sprintf (define,"#define TARBIN_%s_LOW",upname);
		fprintf (f_output,"%-40s %d\n",define,(ptr&0xFFFF));

		sprintf (define,"#define TARBIN_%s_HIGH",upname);
		fprintf (f_output,"%-40s %d\n",define,((ptr>>16) & 0xFFFF));

		// To Z8a file

		sprintf (define,"\t\t\t\tdw\tTARBIN_%s_LOW\n",upname);
		fprintf (f_z8a_output,define);

		sprintf (define,"\t\t\t\tdw\tTARBIN_%s_HIGH\n",upname);
		fprintf (f_z8a_output,define);
		
		
		
		sprintf (define,"#define TARBIN_%s_SIZE",upname);
		fprintf (f_output,"%-40s %d\n",define,files[i].len);
		
		// Z80 extra Create TWO defines for HIGH LOW SIZE

		sprintf (define,"#define TARBIN_%s_SIZE_LOW",upname);
		fprintf (f_output,"%-40s %d\n",define,(files[i].len & 0xFFFF));

		sprintf (define,"#define TARBIN_%s_SIZE_HIGH",upname);
		fprintf (f_output,"%-40s %d\n",define,((files[i].len >>16) & 0xFFFF));


		sprintf (define,"\t\t\t\tdw\tTARBIN_%s_SIZE_LOW\n",upname);
		fprintf (f_z8a_output,define);

		sprintf (define,"\t\t\t\tdw\tTARBIN_%s_SIZE_HIGH\n",upname);
		fprintf (f_z8a_output,define);

		
		
		ptr+=files[i].len;
		fflush(f_output);
		fflush(f_z8a_output);
	}

	fclose (f_output);
	fclose (f_z8a_output);
	fclose (f_z8a_include_output);
	free (files);

	printf ("Done. %d files added to %s, header at %s\n",input_files,tbin_output,h_output);
	printf ("Size of %s -> %i bytes \n\n",tbin_output,totalsize);
	return 0;
}

