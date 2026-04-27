/* CUTTER FOR DREAM ON */

#include <stdio.h>
#include <stdlib.h>
#include <string.h>

typedef unsigned char byte;

void logo (void);
void usage (void);
void makeext (char *nameext,char *nameor,char *ext, int sizename);
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
    char	*options;
    int     size = 0;
    int     sizefile = 0;
    int     sizename=0;

    logo ();
    if (argc < 3) {
        usage();
        return 0;
    }

    filename = argv[1];
    if ((filero = fopen (filename,"rb")) == NULL )
    {
        fprintf(stdout,"ERROR!! An error opening %s \n\n",filename);
        return 1;
    }

    sizename = strlen(filename) +4 ;
    nameexit = (char * ) malloc ( sizename );
    if (nameexit == NULL) {
        fprintf (stdout,"Error allocating memory ... \n");
        return 0;
    }


    fprintf (stdout,"Cutting  -> %s \n\n",filename);		

    if (strlen(argv[2])) {

        // Check si el size del fichero es menor al que quiere cortarse
        size = atoi(argv[2]);
        fseek (filero,0,SEEK_END); 
        sizefile = ftell(filero);
        if (sizefile <= size) {
            fprintf(stdout,"ERROR! size of file < size \n\n",filename);
            return 1;
        }
        fseek (filero,0,SEEK_SET);         

    }
    else {
        fprintf(stdout,"ERROR!! no size! \n\n",filename);
        return 1;

    }

    fprintf(stdout,"Size of file -> %i\n",sizefile);
    fprintf(stdout,"Cut Size -> %i\n\n",size);



    buffer = (byte*) malloc (size);
    if (buffer == NULL) {
        fprintf (stdout,"Error allocating memory ... \n");
        return 0;
    }

    /* Evaluate options */


    if ((argc > 3) && (strlen(argv[3]) > 1)) {		
        options = argv[3];
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
        makeext (nameexit,filename,nameext,sizename);	


        sizeread = fread (buffer,sizeof(byte),size,filero);

        if (sizeread != 0) {
        fprintf(stdout,"To File -> %s \n",nameexit);
        if ((salida = fopen (nameexit,"wb")) == NULL )
        {
            fprintf(stdout,"ERROR!! An error opening %s \n\n",nameexit);
            return 1;
        }

        fwrite (buffer,sizeof(byte),sizeread,salida);   
        fflush(salida);
        fclose (salida);
        if (sizeread != size) 
            exit =1;
        }
        else {
            exit = 1;
        }

    }

    fprintf(stdout,"\nOk!\n\n");
    free(buffer);
    fflush (filero);
    fclose (filero);    
    return 0; 	





}	

void logo (void)
{
    fprintf(stdout,"CutterSize file in xxx files \n");
    fprintf(stdout,"(c) 2009 Kralizec \n\n");    

}

void usage (void)
{
    fprintf(stdout,"Usage	: cuttersize file size  \n\n");
    fprintf(stdout,"Options	:\n");
    fprintf(stdout,"-o	-> No evaluate 7 first bytes (SR5 format) \n");
    fprintf(stdout,"\n");
}	

// Crea extension

void makeext (char *nameext,char *nameor,char *ext,int sizename){

    byte	exit;
    byte	i;
    exit	= 0;
    i	= 0;
    int ii;
    // Borramos nameext

    for (ii = 0 ; ii < sizename; ii++)
        nameext[ii]=0;

    while ((exit ==0) && (i != strlen(nameor)) ){

        if (nameor [i] != 0x2E)
            nameext[i] = nameor[i];
        else
            exit = 1;

        i++;


    }

    if (exit)
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


