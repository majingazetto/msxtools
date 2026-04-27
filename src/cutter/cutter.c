/* CUTTER FOR DREAM ON */

#include <stdio.h>
#include <stdlib.h>
#include <string.h>

typedef unsigned char byte;

void logo (void);
void usage (void);
void makeext (char *nameext,char *nameor,char *ext);
void nextext (int nfile, char *ext);

int main (int argc, char *argv[])
{
	FILE	*filero;
	char	*filename;
	FILE    *salida;
	byte    *buffer;
    	int      sizeread;
    	char    *nameexit;
    	char     nameext[5] = ".001";
    	char    cacho;
	char	*options;
	
	logo ();
	if (argc < 2) {
		usage();
		return 0;
	}
	
	filename = argv[1];
	if ((filero = fopen (filename,"r+b")) == NULL )
	{
		fprintf(stdout,"ERROR!! An error opening %s \n\n",filename);
		return 1;
	}
	
	nameexit = (char * ) malloc (strlen(filename)+1);

	
	fprintf (stdout,"Cutting  -> %s \n\n",filename);		
	

	
	buffer = (byte*) malloc (2048+1);
	if (buffer == NULL) {
		fprintf (stdout,"Error allocating memory ... \n");
		return 0;
	}
	
	/* Evaluate options */
	
	
	if ((argc > 2) && (strlen(argv[2]) > 1)) {		
		options = argv[2];
		if ((options[0] =='-') && (options[1] == 'o'))
			fseek (filero,7,SEEK_SET); 
	}



	
 
    byte exit;
    int	 cnt;
    exit = 0;
    cnt = 1;
    while (exit == 0)    
    {

	nextext (cnt,nameext);
	cnt ++;
	makeext (nameexit,filename,nameext);	
	fprintf(stdout,"To File -> %s \n",nameexit);
	
	sizeread = fread (buffer,sizeof(byte),2048,filero);
	
	if ((salida = fopen (nameexit,"wb")) == NULL )
	{
		fprintf(stdout,"ERROR!! An error opening %s \n\n",nameexit);
		return 1;
	}
  
    fwrite (buffer,sizeof(byte),sizeread,salida);   
    fflush(salida);
    fclose (salida);
    if (sizeread != 2048) 
	    exit =1;
    }

    free(buffer);    
    fclose (filero);    
    return 0; 	
	
	
	
	
	
}	
	
void logo (void)
{
	fprintf(stdout,"CUTTER-SR5 Cut SR5 file in 2048 k files \n\n");
	
}

void usage (void)
{
	fprintf(stdout,"Usage	: cutter file  \n\n");
	fprintf(stdout,"Options	:\n");
	fprintf(stdout,"-o	-> No evaluate 7 first bytes (SR5 format) \n");
	fprintf(stdout,"\n");
}	
	
// Crea extension

void makeext (char *nameext,char *nameor,char *ext){

	byte	exit;
	byte	i;
	exit	= 0;
	i	= 0;
	
	while ((exit ==0) && (i < strlen(nameor)) ){
		
		if (nameor [i] != 0x2E)
			nameext[i] = nameor[i];
		else
		  exit = 1;
		
		i++;
		
	
	}
    nameext [i-1] = 0;
	nameext = strcat (nameext,ext);
	
}	

void nextext (int nfile, char *ext){
	byte	i;
	char	hexa[16] = "0123456789ABCDEF";
	for (i = 3; i > 0 ;i--){
		if (nfile > 15) {
			ext [i] = hexa [nfile & 0x0F];			
			nfile = nfile >> 4;
			

		}
		else
		{
			ext[i] = hexa[nfile];
			nfile =0;
		}
	}
	
}


