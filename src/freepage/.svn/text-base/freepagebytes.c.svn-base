// Mini aplicacion para averiguar a ojímetro el sitio libre en cada página

#include "freepagebytes.h"


int checkFreeBytes (byte* data){
    int cnt = 0;
    int pnt = 8191; 
    BOOL exit = FALSE;

    do {
        if (data[pnt] != 0xFF) {
            exit = TRUE;
        }
        else {
            cnt++;
            pnt--;
            if (pnt<0) exit == TRUE;
        }
    } while (exit == FALSE);

    return cnt;
}


int main (int argc, char *argv[]){

    //! Print Logo
    fprintf(stdout, "Free Page Bytes. (c) 2009 Kralizec\n");

    //! Check Params
    if (argc < 2) { fprintf(stderr,"Usage: %s FILE.ROM\n",argv[0]);
        return -1;
    }

    //! Open file
    nameFile = argv[1];    
    fprintf(stdout,"Open File: %s\n\n",nameFile);

    file = fopen (nameFile,"rb");
    if (!file)
    {
        fprintf(stderr,"Can't open file: %s\n",nameFile);
        perror (nameFile);

        return -1;
    }


    stat (nameFile,&status);
    lenFile = status.st_size; 

    // Read entire file

    data = (byte*) malloc(8192+1);
    if (!data) {
        fprintf(stderr,"Problems allocating memory...\n");
        return -1;
    }

    int sizeread;

    BOOL exit;
    exit = FALSE;
    int page;
    page = 0;
    int freeBytes;
    int total;
    total = 0;

    while (exit == FALSE) {

        sizeread = fread (data,sizeof(byte),8192,file);

        freeBytes = 0;

        if (sizeread == 0) {
            exit = TRUE;
        }
        if (!exit) {
            if (sizeread != 8192) {
                freeBytes = 8192 - sizeread;
                exit = TRUE;
            }
            else {
               freeBytes = checkFreeBytes(data); 
            }
            fprintf(stdout,"Free Bytes Page %2X: %d\n",page,freeBytes);
            page++;
        }
        total += freeBytes;
    };

    fprintf(stdout,"\nTotal : %d\n",total);

    fclose(file);
    free(data);

    return 0;
}
