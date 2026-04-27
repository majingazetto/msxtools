/* SR52PAT */

/* Conversor de ficheros SR5 a fichero de patrones y colores */

#include <stdio.h>
#include <stdlib.h>
#include <string.h>

typedef unsigned char byte;
void logo (void);
void usage (void);
void makebyte (byte *bytesr5, byte *bytesr4, byte *bytecolor);
int makepatron (FILE *filero, byte *patron, byte *color);
void makeext (char *nameext,char *nameor,char *ext);
void makeline (FILE *filero, byte *tabpatron, byte *tabcolor, byte linea);
byte backcolor;



int main (int argc, char *argv[])
{
    FILE	*filero;
    FILE 	*filepatron;
    FILE	*filecolor;
    char	*filename;
    char	*outputnamepatron;
    char	*outputnamecolor;
    byte	*tabpatron;
    byte	*tabcolor;
    byte	linea;
    int	size;
    int	sizetmp;

    backcolor = 0xFF;

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

    if (argc > 3) {
        backcolor = atoi(argv[3]);
    }

    fprintf (stdout,"Converting -> %s \n\n",filename);	



    tabpatron = (byte *) malloc (6144+1);

    if (tabpatron == NULL) {
        fprintf (stdout,"Error allocating memory ... \n");
        return 0;
    }

    tabcolor = (byte *) malloc (6144+1); 	

    if (tabcolor == NULL) {
        fprintf (stdout,"Error allocating memory ... \n");
        return 0;
    }




    if (argc>2) 
        size = atoi (argv[2]) * 256;
    else
        size = 6144;

    if (size == 0 || size > 6144){
        fprintf(stdout,"ERROR! Error in size ...\n\n");
        return 0;		
    }

    fprintf (stdout,"Lines : %d \n",size/256);	
    fprintf (stdout,"Size  : %d \n \n",size);





    outputnamepatron = (char *) malloc (strlen(filename)+1);
    outputnamecolor = (char *) malloc (strlen(filename)+1);	
    makeext (outputnamepatron,filename,".pat"); 
    makeext (outputnamecolor,filename,".col"); 


    if ((filepatron = fopen (outputnamepatron,"wb")) == NULL )
    {
        fprintf(stdout,"ERROR!! An error opening %s \n\n",outputnamepatron);
        return 1;
    }


    if ((filecolor = fopen (outputnamecolor,"wb")) == NULL )
    {
        fprintf(stdout,"ERROR!! An error opening %s \n\n",outputnamecolor);
        return 1;
    }



    memset (tabpatron,0,6144);
    memset (tabcolor,0,6144);




    linea = 0;
    for (sizetmp = 0; sizetmp < size ; sizetmp += 256){
        makeline (filero,tabpatron,tabcolor,linea);
        linea++;			
    }




    fwrite	(tabpatron,sizeof(byte),size,filepatron);
    fwrite	(tabcolor,sizeof(byte),size,filecolor);

    free (tabcolor);
    free (tabpatron);
    fclose(filero);
    fflush(filepatron);
    fclose(filepatron);
    fflush(filecolor);
    fclose(filecolor);
    free(outputnamepatron);
    free(outputnamecolor);
    return 0;
}



void logo (void)
{
    fprintf(stdout,"SR52PAT Convert Utility v 1.1 (c) 2004-2015 Ramones \n\n");

}

void usage (void)
{
    fprintf(stdout,"Usage : sr52pat image.sr5 lines (default 24) backcolor (optional) \n\n");
}	



void makebyte (byte *bytesr5, byte *bytepatron, byte *bytecolor)
{
    byte	colorfondo;
    byte	colorpapel;
    byte    colortemp;
    byte	bitsuma;
    byte	i;

    bytepatron[0] = 0;
    bytecolor [0] = 0;
    colorfondo = (bytesr5[0] & 0xF0) >> 4;
    colorpapel = (bytesr5[0] & 0x0F);


    if (backcolor != 0xFF) {
       colorfondo = backcolor; 
    }

    
/*    if (colorfondo > colorpapel) {
        colortemp   = colorfondo;
        colorfondo  = colorpapel;
        colorpapel  = colortemp;
    }
*/
    
    bitsuma = 128;
    for (i = 0; i<4 ; i++){

        if ( ((bytesr5[i] & 0xF0) >> 4) != colorfondo ){
            bytepatron[0] += bitsuma;
            colorpapel = (bytesr5[i] & 0xF0) >> 4;			
        }

        bitsuma >>= 1;

        if ((bytesr5[i] & 0x0F) != colorfondo ) {
            bytepatron[0] += bitsuma;
            colorpapel = (bytesr5[i] & 0x0F);			

        }		
        bitsuma >>= 1;
    }


    // Arreglo para que el color de fondo y de papel sean igual
    // color fondo < 
    // color papel >

    if (colorfondo > colorpapel) {        
        colortemp = colorfondo;
        colorfondo  = colorpapel;
        colorpapel  = colortemp;
        // Invertir tambien el byte
        bytepatron[0] = ~bytepatron[0];
        
    }
    

    bytecolor[0] = (colorpapel << 4) + colorfondo;

}


int makepatron (FILE *filero, byte *patron, byte *color)
{

    byte	*buffer;
    byte	i;
    byte	bytepatron;
    byte	bytecolor;

    buffer = (byte *) malloc (4+1); 	


    if (buffer == NULL) {
        fprintf (stdout,"Error allocating memory ... \n");
        return 1;
    }

    for	(i = 0; i < 8; i++){

        fread (buffer,sizeof(byte),4,filero);
        makebyte (buffer,&bytepatron,&bytecolor);
        patron [i] = bytepatron;
        color  [i] = bytecolor;
        fseek (filero,128-4,SEEK_CUR);
    }

    fseek (filero,-128*8,SEEK_CUR);
    free (buffer);  

    return 0;		
}


void makeline (FILE *filero, byte *tabpatron, byte *tabcolor, byte linea)
{



    int	pos;
    byte	i;



    pos = (linea * 1024)+7;
    fseek (filero,pos,SEEK_SET); 




    tabcolor  = tabcolor  + ((32 * 8) * linea);
    tabpatron = tabpatron + ((32 * 8) * linea);	

    for (i = 0 ; i < 32 ; i ++){

        makepatron (filero,tabpatron,tabcolor);
        tabpatron+=8;
        tabcolor+=8;
        fseek (filero,4,SEEK_CUR);			

    }

    tabcolor  = tabcolor - ((32*8)*linea+1);
    tabpatron = tabpatron -((32*8)*linea+1);


}



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




