

//////////////////////////
///// EXTRACTWAV 0.1 /////
//////////////////////////


#include	<stdio.h>
#include	<stdlib.h>
#include	<memory.h>
#include	<math.h>
#include	<sys/types.h>
#include	<sys/stat.h>
#include	<unistd.h>
#include	<strings.h>
#include	<ctype.h>


#define	BYTE	unsigned char
#define	BOOL	int
#define TRUE	1
#define	FALSE	0


#define	VERSION	"0.1"

#define	WAVCHANNELS	4
#define	MAXWAVES 128

#define	PSGDATA		(BYTE) 0xF0
#define	SCCDATA		(BYTE) 0xF1
#define	SCCWAVEDATA	(BYTE) 0XF2
#define	ENDFRAME	(BYTE) 0xFF



typedef struct
{
		int len;
		char *fname;
}SFILE;

typedef struct
{
	BYTE	channel;
	BYTE	wav[32];

} SCCWAVCHANNEL;


void logo();

int main(int argc, char* argv[]);


