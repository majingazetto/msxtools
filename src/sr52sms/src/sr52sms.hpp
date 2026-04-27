



/* SR52SMS */

/* Tile/Sprite conversor from SR5 to SMS VRAM data */

// Defines data types

#define u8  unsigned char
#define u16 unsigned short
#define u32 unsigned int
#define s8  char
#define s16 short
#define s32 int

void logo();
void usage();
u8* readSR5File(s8* filename);
s8* makeext (s8* filename, s8* ext);
u8* convertdata (u8* rawdata, s32 initline, s32 lines);
void convertline (u8* rawdata, u8* convertdata);
void convertcolor (u8 color, u8 pos, u8* b0, u8* b1, u8* b2, u8* b3);
s32 savefile(s8* filename, s32 lines, u8* convertdata);
s32 savepalfile(s8* outputname, u8* paldata);
s32 savepalascfile (s8* filename, u8* paldata);
u8* convert (u8* rawdata, s32 initline, s32 lines);
u8* readPL5File (s8* filename);
void convertpal (u8* sr5pal, u8* convertpal) ;

bool isSC5;


