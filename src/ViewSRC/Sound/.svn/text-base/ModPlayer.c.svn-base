/*--------------------------------------------------------------------------

        TLOTB Mod Player

        Astharoth / Hgh on July 2002

--------------------------------------------------------------------------*/

//Includes-
//---------

#include <stdlib.h>
#include <stdio.h>

#include "Common.h"
//#include <Console.h>
#include "../AMOSLib.h"            //Solo para las alocaciones de memoria y liberacion (solo dos)
#include "Sound.h"                      //Funciones de temporizacion.
#include "Mixer.h"                      //Funciones de mezclador.
//#include <MixerTable.h>                 //Funciones de mezclador.

#include "ModPlayer.h"          //Nuestro interface.

// Defines
// ----------

// El protracker guarda loops con valor 256 en algunos instrumentos sin loop
// Si se graba con otro tracker no ocurre
#define _BUGGED_MOD_LOOP_

static int invertedMachine()
{
    int v = 1;
    return *(char*)&v != 0;
}

//Estructuras formato .MOD
//-------------------------------------------------------------------

struct SampleInfo
{
        char                    SampleName [22];        // Nombre del sample 
        unsigned short  SampleLen;                      // Tamaño (en WORDS) del sample
        unsigned char   SampleFT;                       // Finetune del sample
        unsigned char   SampleVolume;           // Volumen del sample
        unsigned short  SampleLoopStart;        // Posición de inicio del loop relativa al inicio 
                                                                                // en WORDS
        unsigned short  SampleRepeatLen;        // Tamáño del loop (en WORDS)
} __attribute__((packed));

struct ModInfo
{
        unsigned char   NumPatterns;            // Número de paterns que se van a tocar
        unsigned char   Dummy;                          // ...
        unsigned char   PatternTable[128];      // Tabla de la secuencia de patterns
        char                    Signature[4];           // Firma, para saber el tipo de .mod
} __attribute__((packed));

struct ModStruct
{
        char                    ModName[20];            // Nombre del modulo
        struct SampleInfo       SInfo[31];              // Enlace a la informacion de samples
        struct ModInfo          MInfo;                  // Enlace a la informacion de modulo (patterns,etc)
} __attribute__((packed));

// Tablas para finetunes
static const unsigned short PeriodTable_0[]={4064,3840,3624,
3424,3232,3048,2880,2712,2560,2416,2280,2152,2032,1920,1812,
1712,1616,1524,1440,1356,1280,1208,1140,1076,1016,960,906,
856,808,762,720,678,640,604,570,538,508,480,453,
428,404,381,360,339,320,302,285,269,254,240,226,
214,202,190,180,170,160,151,143,135,127,120,113,
107,101, 95, 90, 85, 80, 75, 71, 67, 63, 60, 56
};

static const unsigned short PeriodTable_1[]={4058,3834,3618,
3418,3226,3042,2874,2706,2554,2410,2274,2146,2026,1914,1806,
1706,1610,1518,1436,1350,1274,1202,1134,1070,1010,984,900,
850,802,757,715,674,637,601,567,535,505,477,450,
425,401,379,357,337,318,300,284,268,253,239,225,
213,201,189,179,169,159,150,142,134,126,119,113,
106,100, 94, 89, 84, 79, 75, 71, 67, 83, 59, 56};

static const unsigned short PeriodTable_2[]={4064,3840,3624,
3424,3232,3048,2880,2712,2560,2416,2280,2152,2032,1920,1812,
1712,1616,1524,1440,1356,1280,1208,1140,1076,1016,960,906,
844,796,752,709,670,632,597,563,532,502,474,447,
422,398,376,355,335,316,298,282,266,251,237,224,
211,199,188,177,167,158,149,141,133,125,118,112,
105, 99, 94, 88, 83, 79, 74, 70, 66, 62, 59, 56 };

static const unsigned short PeriodTable_3[]={4064,3840,3624,
3424,3232,3048,2880,2712,2560,2416,2280,2152,2032,1920,1812,
1712,1616,1524,1440,1356,1280,1208,1140,1076,1016,960,906,
838,791,746,704,665,628,592,559,528,498,470,444,
419,395,373,352,332,314,296,280,264,249,235,222,
209,198,187,176,166,157,148,140,132,125,118,111,
104, 99, 93, 88, 83, 78, 74, 70, 66, 62, 59, 55};


static const unsigned short PeriodTable_4[]={4064,3840,3624,
3424,3232,3048,2880,2712,2560,2416,2280,2152,2032,1920,1812,
1712,1616,1524,1440,1356,1280,1208,1140,1076,1016,960,906,
832,785,741,699,660,623,588,555,524,495,467,441,
416,392,370,350,330,312,294,278,262,247,233,220,
208,196,185,175,165,156,147,139,131,124,117,110,
104, 98, 92, 87, 82, 78, 73, 69, 65, 62, 58, 55};

static const unsigned short PeriodTable_5[]={4064,3840,3624,
3424,3232,3048,2880,2712,2560,2416,2280,2152,2032,1920,1812,
1712,1616,1524,1440,1356,1280,1208,1140,1076,1016,960,906,
826,779,736,694,655,619,584,551,520,491,463,437,
413,390,368,347,328,309,292,276,260,245,232,219,
206,195,184,174,164,155,146,138,130,123,116,109,
103, 97, 92, 87, 82, 77, 73, 69, 65, 61, 58, 54};

static const unsigned short PeriodTable_6[]={4064,3840,3624,
3424,3232,3048,2880,2712,2560,2416,2280,2152,2032,1920,1812,
1712,1616,1524,1440,1356,1280,1208,1140,1076,1016,960,906,
820,774,730,689,651,614,580,547,516,487,460,434,
410,387,365,345,325,307,290,274,258,244,230,217,
205,193,183,172,163,154,145,137,129,122,115,109,
102, 96, 91, 86, 81, 77, 72, 68, 64, 61, 57, 54};

static const unsigned short PeriodTable_7[]={4064,3840,3624,
3424,3232,3048,2880,2712,2560,2416,2280,2152,2032,1920,1812,
1712,1616,1524,1440,1356,1280,1208,1140,1076,1016,960,906,
814,768,725,684,646,610,575,543,513,484,457,431,
407,384,363,342,323,305,288,272,256,242,228,216,
204,192,181,171,161,152,144,136,128,121,114,108,
102, 96, 90, 85, 80, 76, 72, 68, 64, 60, 57, 54};

static const unsigned short PeriodTable_8[]={4064,3840,3624,
3424,3232,3048,2880,2712,2560,2416,2280,2152,2032,1920,1812,
1712,1616,1524,1440,1356,1280,1208,1140,1076,1016,960,906,
907,856,808,762,720,678,640,604,570,538,504,480,
453,428,404,381,360,339,320,302,285,269,254,240,
226,214,202,190,180,170,160,151,143,135,127,120,
113,107,101, 95, 90, 85, 80, 75, 71, 67, 63, 60};

static const unsigned short PeriodTable_9[]={4064,3840,3624,
3424,3232,3048,2880,2712,2560,2416,2280,2152,2032,1920,1812,
1712,1616,1524,1440,1356,1280,1208,1140,1076,1016,960,906,
900,850,802,757,715,675,636,601,567,535,505,477,
450,425,401,379,357,337,318,300,284,268,253,238,
225,212,200,189,179,169,159,150,142,134,126,119,
112,106,100, 94, 89, 84, 79, 75, 71, 67, 63, 59};

static const unsigned short PeriodTable_10[]={4064,3840,3624,
3424,3232,3048,2880,2712,2560,2416,2280,2152,2032,1920,1812,
1712,1616,1524,1440,1356,1280,1208,1140,1076,1016,960,906,
894,844,796,752,709,670,632,597,563,532,502,474,
447,422,398,376,355,335,316,298,282,266,251,237,
223,211,199,188,177,167,158,149,141,133,125,118,
111,105, 99, 94, 88, 83, 79, 74, 70, 66, 62, 59};

static const unsigned short PeriodTable_11[]={4064,3840,3624,
3424,3232,3048,2880,2712,2560,2416,2280,2152,2032,1920,1812,
1712,1616,1524,1440,1356,1280,1208,1140,1076,1016,960,906,
887,838,791,746,704,665,628,592,559,528,498,470,
444,419,395,373,352,332,314,296,280,264,249,235,
222,209,198,187,176,166,157,148,140,132,125,118,
111,104, 99, 93, 88, 83, 78, 74, 70, 66, 62, 59};

static const unsigned short PeriodTable_12[]={4064,3840,3624,
3424,3232,3048,2880,2712,2560,2416,2280,2152,2032,1920,1812,
1712,1616,1524,1440,1356,1280,1208,1140,1076,1016,960,906,
881,832,785,741,699,660,623,588,555,524,494,467,
441,416,392,370,350,330,312,294,278,262,247,233,
220,208,196,185,175,165,156,147,139,131,123,117,
110,104, 98, 92, 87, 82, 78, 73, 69, 65, 61, 58};

static const unsigned short PeriodTable_13[]={4064,3840,3624,
3424,3232,3048,2880,2712,2560,2416,2280,2152,2032,1920,1812,
1712,1616,1524,1440,1356,1280,1208,1140,1076,1016,960,906,
875,826,779,736,694,655,619,584,551,520,491,463,
437,413,390,368,347,338,309,292,276,260,245,232,
219,206,195,184,174,164,155,146,138,130,123,116,
109,103, 97, 92, 87, 82, 77, 73, 69, 65, 61, 58};

static const unsigned short PeriodTable_14[]={4064,3840,3624,
3424,3232,3048,2880,2712,2560,2416,2280,2152,2032,1920,1812,
1712,1616,1524,1440,1356,1280,1208,1140,1076,1016,960,906,
868,820,774,730,689,651,614,580,547,516,487,460,
434,410,387,365,345,325,307,290,274,258,244,230,
217,205,193,183,172,163,154,145,137,129,122,115,
108,102, 96, 91, 86, 81, 77, 72, 68, 64, 61, 57};

static const unsigned short PeriodTable_15[]={4064,3840,3624,
3424,3232,3048,2880,2712,2560,2416,2280,2152,2032,1920,1812,
1712,1616,1524,1440,1356,1280,1208,1140,1076,1016,960,906,
862,814,768,725,684,646,610,575,543,513,484,457,
431,407,384,363,342,323,305,288,272,256,242,228,
216,203,192,181,171,161,152,144,136,128,121,114,
108,101, 96, 90, 85, 80, 76, 72, 68, 64, 60, 57 };

static const unsigned short *FinetuneTables[]={PeriodTable_0,PeriodTable_1,PeriodTable_2,PeriodTable_3,
PeriodTable_4,PeriodTable_5,PeriodTable_6,PeriodTable_7,PeriodTable_8,PeriodTable_9,
PeriodTable_10,PeriodTable_11,PeriodTable_12,PeriodTable_13,PeriodTable_14,PeriodTable_15};



//Este define indica la frecuencia real de salida del dispositivo hardware
//necesario para realizar los calculos pertientes para los periodos de las notas
//-------------------------------------------------------------------------------
#define TLOTB_STARTPLAYING      0x0002
#define TLOTB_PLAYING           0x0001
#define TLOTB_STOPED            0x0000
#define TLOTB_PAUSED            0x0003

//Estructura de canales
//En esta estructura se guarda informacion adicional para los comandos de tick que
//no existen en la estructura del mixer.
//---------------------------------------------------------------------------------
struct TrackInfo
{
        unsigned char   Command;                        // Comando (-1 si ninguno)
        unsigned char   CommandProcessed;       // Flag de valor procesado.
        unsigned char   Value;                          // Valor generico del comando.
        unsigned char   PortaToNoteSpeed;       // Específico del efecto Porta To Note.
        unsigned short  Period;                         // Periodo al que tiende con un porta to note.
        unsigned short  ActualPeriod;           // Periodo actual del canal.
        unsigned char   LastSampleOffset;       // Especifico del sample offset.
        unsigned char   VibratoSpeed;           // Velocidad del vibrato.
        unsigned char   VibratoDepth;           // Cantidad de vibrato.
        unsigned char   VibratoPos;                     // Posición dentro de la tabla de frecuencias para Vibrato.
        unsigned short  VibratoPeriod;          // Periodo base para el vibrato.
        unsigned short  ArpeggioPeriod;         // Periodo base para el arpeggio.
        unsigned char   Sample;                         // Sample Actual en el canal.
        unsigned char   Panning;                        // Panning actual del canal.
        unsigned char   TremoloSpeed;           // Velocidad del efecto tremolo.
        unsigned char   TremoloDepth;           // profundidad del efecto tremolo.
        unsigned char   TremoloPos;                     // posicion del efecto tremolo.
        unsigned short  TremoloVolume;          // volumen actual del efecto tremolo.
        unsigned char   Volume;                         // Volumen del canal.
        unsigned char   ActualFineTune;         // Finetune actual (esto cambia con el instrumento).
};


//Definiciones de comandos de un .MOD
//-------------------------------------
#define MODFORMAT_ARPEGIO                       0x00
#define MODFORMAT_PORTAUP                       0x01
#define MODFORMAT_PORTADOWN                     0x02
#define MODFORMAT_PORTATONOTE           0x03
#define MODFORMAT_VIBRATO                       0x04
#define MODFORMAT_PORTAVOLSLIDE         0x05
#define MODFORMAT_VIBRATOVOLSLIDE       0x06
#define MODFORMAT_TREMOLO                       0x07
#define MODFORMAT_PANNING                       0x08
#define MODFORMAT_SAMPLEOFFSET          0x09
#define MODFORMAT_VOLUMESLIDE           0x0A
#define MODFORMAT_JUMPTOPATTERN         0x0B
#define MODFORMAT_SETVOLUME                     0x0C
#define MODFORMAT_PATTERNBREAK          0x0D
#define MODFORMAT_SETSPEED                      0x0F
#define MODFORMAT_ECOMMAND                      0x0E
#define MODFORMAT_ESETFILTER            0x00
#define MODFORMAT_EFINEPORTAUP          0x10
#define MODFORMAT_EFINEPORTADOWN        0x20
#define MODFORMAT_EGLISANDOCONTROL      0x30
#define MODFORMAT_ESETVIBRATOWAVE       0x40
#define MODFORMAT_ESETFINETUNE          0x50
#define MODFORMAT_EPATTERNLOOP          0x60
#define MODFORMAT_ESETTREMOLOWAVE       0x70
#define MODFORMAT_EUNUSED                       0x80            //Can be used to synchro
#define MODFORMAT_ERETRIGNOTE           0x90
#define MODFORMAT_EFINEVOLSLIDEUP       0xA0
#define MODFORMAT_EFINEVOLSLIDEDOWN     0xB0
#define MODFORMAT_ECUTNOTE                      0xC0
#define MODFORMAT_EDELAYNOTE            0xD0
#define MODFORMAT_EPATTERNDELAY         0xE0
#define MODFORMAT_EINVERTLOOP           0xF0

//Tabla de senos para los efectos de vibrato y tremolo.
//------------------------------------------------------------------------------
static const unsigned char MODFORMAT_SinTab[] = {0,25,50,74,98,120,142,162,180,197,212,225,236,
                                                              244,250,254,255,254,250,244,236,225,212,197,180,
                                                              162,142,120,98,74,50,25};

//Modulo.
//---------------------------------------------------------------------
struct MOD
{
        unsigned char MOD_Tempo;                                //Tempo del modulo (Actual)
        unsigned char MOD_Bpm;                                  //Bpm's del modulo (Actual);
        unsigned char MOD_State;                                //Estado del modulo (Actual);   
        unsigned const char* MOD_Address;                       //Direccion del modulo en memoria;
        unsigned char* MOD_PatternsOffset;              //Puntero a la base de los patterns;
        unsigned char* MOD_PatternsOrder;               //Puntero al inicio de los Orders.
        unsigned char* MOD_SamplesBase;                 //Puntero al inicio de los samples.
        unsigned char  MOD_NumOrders;                   //Numero de Orders en el modulo.
        unsigned char* MOD_ActualRow;                   //Puntero al row actual
        unsigned char* MOD_ActualOrder;                 //Puntero al order actual
        unsigned char  MOD_Row;                                 //Row actual (entero)
        unsigned char  MOD_Order;                               //Order actual (entero)
        unsigned long  MOD_BpmSpeed;                    //Velocidad fraccional 8:8 del BPM.
        unsigned char* MOD_SampleOffset[31];    //Direcciones de memoria con los samples
        unsigned long  MOD_SampleLenght[31];    //Longitudes de los samples.
        unsigned char  MOD_SampleFineTune[31];  //Finetune del sample.
        unsigned char  MOD_SampleVolume[31];    //Volumen por defecto del Sample
        unsigned long  MOD_SampleLoopStart[31]; //Comienzo del loop del sample.
};


//Player.
//-------------------------------------------------------------------
struct PLAYER
{
        unsigned long PLAYER_BpmSpeedCount;     //Contador para los BMP.
        unsigned long PLAYER_TempoCount;                //Contador para el Tempo.
        unsigned char PLAYER_PatternDelay;      //Contador para el efecto de pattern delay.
        unsigned char PLAYER_VibratoWaveForm;//Tipo de vibrato a emplear.
        unsigned char PLAYER_TremoloWaveForm;//Tipo de tremolo a emplear.
        unsigned char PLAYER_RowLoop;           //Row para el loop.
        unsigned char PLAYER_LoopTimes;         //Contador para los loops.
        unsigned char PLAYER_GlisandoControl;//GlisandoControl (para PortaToNote)
        unsigned long PLAYER_OutputFrequency;//Frecuencia de salida 
        unsigned long PLAYER_BpmRate;           //Rate de actualizacion (60Hz)
    unsigned char PLAYER_SetNewPositionFlag; //Flag para cambio de posicion en el modulo.
        struct TrackInfo PLAYER_Channels[4];    //Estructuras para efectos del player por canal.
};


//Variables globales
//-------------------------------------------------------------
struct PLAYER*  pP;
struct MOD*             pM;


//Funciones internas del player. Prototipos.
//--------------------------------------------
static void Internal_SetBPM(unsigned char BPM);
static void Internal_SetNote(int wChannel,unsigned long Pos,unsigned long FreqAdd,unsigned char Arpeggio);
static void Internal_VolumeSlide(int wChannel);
static void Internal_PortaToNote(int wChannel);
static void Internal_Vibrato(int wChannel);
static void Internal_SetSample(int wChannel,unsigned char Sample);
static void Internal_DoArpegio(int wChannel,unsigned long Tick);
static void Internal_Tremolo(int wChannel);
static unsigned short Internal_FindPeriodFinetune(unsigned short Period,unsigned char FineTune,unsigned char Arpeggio);
static void Internal_SetVolume(int wChannel,unsigned char Volume);


//Inicializa las variables del player en funcion
//de la frequencia a la que se nos despache la interrupcion.
//----------------------------------------------------------
unsigned long TLOTB_InitPlayer()
{
        //Inicializamos la estructura PLAYER
        //y fijamos los valores.
        pP = (struct PLAYER*) Reserve (sizeof(struct PLAYER),"Player structs");
        memset(pP, 0, sizeof(struct PLAYER));
        pP->PLAYER_OutputFrequency = Sound_GetFrequency();
        pP->PLAYER_BpmRate = Sound_GetFrequency() / Sound_GetSamplesToMix();
        fprintf( stderr,"Player initialized. Freq: %d BPM: %d\n", 
            pP->PLAYER_OutputFrequency, pP->PLAYER_BpmRate);
        return TLOTB_PLAYER_OK;
}

//Liberamos los posibles recursos del player
//------------------------------------------
unsigned long TLOTB_FinishPlayer()
{
        //Liberamos la estructura PLAYER
        if (pM != NULL)
        {
            TLOTB_StopMusic();
            TLOTB_FreeMod();
        }
        if (pP == NULL)
                return TLOTB_PLAYER_OK;
        Free(pP);
        pP = NULL;
        fprintf(stderr,"Player terminated\n");
        return TLOTB_PLAYER_OK;
}

static int isMod(const char * pAddr)
{
    return pAddr[0x438] == 'M'
        && pAddr[0x439] == '.'
        && pAddr[0x43a] == 'K'
        && pAddr[0x43b] == '.';
}

//Carga el modulo e inicializa las variables propias para tocarlo
//IN: Puntero al modulo en memoria.
//----------------------------------------------------------------
unsigned long TLOTB_LoadMod(const char* MemAddress)
{
        struct ModStruct* pMod;
        unsigned long ind;
        unsigned char* SamplesBase;
        unsigned short SampleSize,SampleSizePartial;
        unsigned short NumberOfPatterns;
        if (!isMod(MemAddress))
            return TLOTB_PLAYER_WRONGMOD;
        if (pM)
            return TLOTB_MODSTILLALLOCATED;
        //Creamos la estructura MOD
        pM = (struct MOD*) Reserve ( sizeof(struct MOD), "Player structs");
        memset(pM, 0, sizeof(struct MOD));

        //Guardamos la direccion del modulo en memoria para futuros fixups
        pM->MOD_Address = MemAddress;
        pMod = (struct ModStruct*) pM->MOD_Address;
        pM->MOD_NumOrders = pMod->MInfo.NumPatterns;
        pM->MOD_PatternsOrder = pMod->MInfo.PatternTable;
        pM->MOD_PatternsOffset= (char*)((unsigned long) pM->MOD_Address + sizeof(struct ModStruct));
        //La base para los samples se calcula en base a que cada pattern es 1k
        //(4canales). Si se soportan modulos de mas canales hay que tener una variable
        //para el numero de canales y variar este calculo en consecuencia.
        NumberOfPatterns=0; //Buscamos el numero maximo de patterns
        for(ind=0;ind<pMod->MInfo.NumPatterns;ind++)
        {
                if (pMod->MInfo.PatternTable[ind] > NumberOfPatterns)
                                NumberOfPatterns = pMod->MInfo.PatternTable[ind];
        }
        NumberOfPatterns++; //En la tabla están basados en cero
        pM->MOD_SamplesBase = ((char*)pM->MOD_PatternsOffset)  +( NumberOfPatterns << 10); //(pMod->MInfo.NumPatterns<<10);
        //Rellenamos las tablas de instrumentos.
        SamplesBase = pM->MOD_SamplesBase;
        for(ind=0;ind<31;ind++)
        {
                //Indicamos en nuestro array la base de memoria del sample
                pM->MOD_SampleOffset[ind] = SamplesBase;
                //Obtenemos la longitud
                SampleSize = pMod->SInfo[ind].SampleLen;
                //La longitud del sample esta en big endian, le damos la vuelta.
                if (invertedMachine())
                {
                    SampleSizePartial = SampleSize >> 8;
                    SampleSize <<= 8;
                    SampleSize += SampleSizePartial;
                }
                //La longitud esta en words, asi que multiplicamos por dos.
                pM->MOD_SampleLenght[ind] = SampleSize << 1;
                //Actualizamos el puntero de samples base.
                SamplesBase+= pM->MOD_SampleLenght[ind];
                pM->MOD_SampleFineTune[ind] = pMod->SInfo[ind].SampleFT & 0x0F;
                pM->MOD_SampleVolume[ind] = pMod->SInfo[ind].SampleVolume;
                SampleSize = pMod->SInfo[ind].SampleLoopStart;
                if (invertedMachine())
                {
                    SampleSizePartial = SampleSize >> 8;
                    SampleSize <<= 8;
                    SampleSize += SampleSizePartial;
                }
                pM->MOD_SampleLoopStart[ind] = SampleSize << 1; //pMod->SInfo[ind].SampleLoopStart << 1;
#ifdef _BUGGED_MOD_LOOP_
                if ((pMod->SInfo[ind].SampleRepeatLen == 0) || 
                    (pMod->SInfo[ind].SampleRepeatLen == 256) ||
                    (pMod->SInfo[ind].SampleRepeatLen == 1)
)
#else
                if (pMod->SInfo[ind].SampleRepeatLen == 0)
#endif
                        pM->MOD_SampleLoopStart[ind] = pM->MOD_SampleLenght[ind];
        }
        return TLOTB_PLAYER_OK;
}

//Libera del player los valores de las variables
//inicializados por la carga de un modulo
//-----------------------------------------------
unsigned long TLOTB_FreeMod()
{
        if (pM == NULL)
                return TLOTB_PLAYER_OK;
        //Comprobamos si el modulo continua en Play
        if (pM->MOD_State != TLOTB_STOPED)
                return TLOTB_PLAYER_MODPLAYING;
        //Liberamos la estructura MOD
        Free(pM);
        pM = NULL;
        return TLOTB_PLAYER_OK;
}

//Pausa la musica en play actual
//-----------------------------------
unsigned long TLOTB_PauseMusic()
{
    if (!pM)
        return TLOTB_PLAYER_NOMOD;
    if (pM->MOD_State == TLOTB_PLAYING)
        pM->MOD_State = TLOTB_PAUSED;
    else
        if (pM->MOD_State == TLOTB_PAUSED)
            pM->MOD_State = TLOTB_PLAYING;
    return TLOTB_PLAYER_OK;
}


//Inicializa el player de musica (variables por defecto)
//-------------------------------------------------------
unsigned long TLOTB_PlayMusic()
{
        unsigned long NChannels;
        if (!pM)
            return TLOTB_PLAYER_NOMOD;
        //Tempo & Bpm's.
        pM->MOD_Tempo = 6;
        pP->PLAYER_TempoCount = 0;
        Internal_SetBPM(125);
        //Inicio de la cancion
        pM->MOD_Row = 0;
        pM->MOD_Order = 0;
        pM->MOD_ActualOrder = pM->MOD_PatternsOrder;
        pM->MOD_ActualRow = pM->MOD_PatternsOffset+((*pM->MOD_ActualOrder) << 10); //(Idem.. *1024 ... 4 canales)
        pM->MOD_State = TLOTB_STARTPLAYING;
        pP->PLAYER_PatternDelay = 0;
    //pP->PLAYER_NewPositionFlag = 0;
        for (NChannels = 0; NChannels != 4;NChannels++)
        {
                pP->PLAYER_Channels[NChannels].Command = -1;
                pP->PLAYER_Channels[NChannels].Panning = 0x80;
        }
        return TLOTB_PLAYER_OK;
}

//Detine el play del modulo
//-----------------------------
unsigned long TLOTB_StopMusic()
{
    if (!pM)
        return TLOTB_PLAYER_NOMOD;
    pM->MOD_State = TLOTB_STOPED;
    return TLOTB_PLAYER_OK;
}


//Devuelve la posicion actual del modulo.
//---------------------------------------------------------------------------
unsigned long TLOTB_GetModPosition(unsigned char* Pattern,unsigned char* Row)
{
    if (!pM)
        return TLOTB_PLAYER_NOMOD;
    *Pattern = pM->MOD_Order;
    *Row = pM->MOD_Row;
    return TLOTB_PLAYER_OK;
}

//Fija una posicion absoluta en el modulo.
unsigned long TLOTB_SetModPosition(unsigned char Pattern,unsigned char Row)
{
    if (!pM)
        return TLOTB_PLAYER_NOMOD;
    if (Pattern >= pM->MOD_NumOrders)
        return TLOTB_PLAYER_NOSUCHPAT;
    if (Row >= 64)
        return TLOTB_PLAYER_WRONGROW;
    //pP->PLAYER_NewPositionFlag = 1;
    pM->MOD_Row = Row;
    pM->MOD_ActualOrder = pM->MOD_PatternsOrder+Pattern;
        pM->MOD_Order = Pattern;
        pM->MOD_ActualRow = pM->MOD_PatternsOffset+((*pM->MOD_ActualOrder) << 10);
        pM->MOD_ActualRow += pM->MOD_Row * (4*4); 
    return TLOTB_PLAYER_OK;
}


//Procesa el modulo para un periodo determinado
//---------------------------------------------
void ControlChannels ()
{
        char Actualice = 0;
        unsigned long BPMTemp;                  //Contador para los ciclos de BPM's
        unsigned long ChannelProcess;   //Contador del numero de canales.

        //Comprobamos si se ha inicializado algo.
        if ( (pM == NULL) || (pP == NULL))
                return;
        //Comprobamos si estamos detenidos.
        //---------------------------------
        if ( (pM->MOD_State == TLOTB_STOPED) || (pM->MOD_State == TLOTB_PAUSED))
        {
                Mixer_SetChannelVolume(0,0,0);
                Mixer_SetChannelVolume(1,0,0);
                Mixer_SetChannelVolume(2,0,0);
                Mixer_SetChannelVolume(3,0,0);
                return;
        }
        //Si es la primera vez que entramos, marcamos actualizar posiciones.
        //------------------------------------------------------------------
        if (pM->MOD_State == TLOTB_STARTPLAYING)
        {
                Actualice = 1;
                pM->MOD_State = TLOTB_PLAYING;
        }
        //Comprobamos si hemos de actualizar posiciones...
        //-----------------------------------------------------
        pP->PLAYER_BpmSpeedCount += pM->MOD_BpmSpeed;
        BPMTemp = pP->PLAYER_BpmSpeedCount & 0xffff0000;
        if (BPMTemp)
        {
                pP->PLAYER_BpmSpeedCount = pP->PLAYER_BpmSpeedCount & 0x0000ffff;
                //En base a TempoCount hemos de aplicar valores tipo arpegio, vibrato y tremolo.
                if (pP->PLAYER_TempoCount == pM->MOD_Tempo)
                {
                        Actualice = 1;
                        pP->PLAYER_TempoCount = 1;
                        //Reseteamos comandos en cola
                        for (ChannelProcess = 0; ChannelProcess != 4; ChannelProcess++) //4 Numero de canales...
                        {
                                //Si el comando es alguno de estos... comando procesado al cambiar de row.
                                //------------------------------------------------------------------------
                                if ( (pP->PLAYER_Channels[ChannelProcess].Command == MODFORMAT_VOLUMESLIDE)  ||
                                         (pP->PLAYER_Channels[ChannelProcess].Command == MODFORMAT_PORTAVOLSLIDE) ||
                                         (pP->PLAYER_Channels[ChannelProcess].Command == MODFORMAT_PORTAUP) ||
                                         (pP->PLAYER_Channels[ChannelProcess].Command == MODFORMAT_PORTADOWN) ||
                                         (pP->PLAYER_Channels[ChannelProcess].Command == MODFORMAT_VIBRATOVOLSLIDE) ||
                                         (pP->PLAYER_Channels[ChannelProcess].Command == MODFORMAT_ARPEGIO) ||
                                         (pP->PLAYER_Channels[ChannelProcess].Command == MODFORMAT_TREMOLO) ||
                                         (pP->PLAYER_Channels[ChannelProcess].Command == MODFORMAT_VIBRATO) ||
                                         (pP->PLAYER_Channels[ChannelProcess].Command == MODFORMAT_ECUTNOTE) ||
                                         (pP->PLAYER_Channels[ChannelProcess].Command == MODFORMAT_ERETRIGNOTE) )
                                        pP->PLAYER_Channels[ChannelProcess].CommandProcessed = 0x1;
                        }
                }
                else
                {
                        pP->PLAYER_TempoCount++;
                        //Procesamos los efectos en cola para cada tick.
                        //-----------------------------------------------------------------------------------------------
                        for (ChannelProcess = 0; ChannelProcess != 4; ChannelProcess++) //4 Numero de canales...
                        {
                                if (!pP->PLAYER_Channels[ChannelProcess].CommandProcessed)
                                {
                                        switch(pP->PLAYER_Channels[ChannelProcess].Command)
                                        {
                                                //Arpegio
                                                case MODFORMAT_ARPEGIO:
                                                        Internal_DoArpegio(ChannelProcess,pP->PLAYER_TempoCount);
                                                break;
                                                //Tremolo
                                                case MODFORMAT_TREMOLO:
                                                        Internal_Tremolo(ChannelProcess);
                                                        break;
                                                //Portamento UP.
                                                case MODFORMAT_PORTAUP:
                                                        pP->PLAYER_Channels[ChannelProcess].ActualPeriod -= pP->PLAYER_Channels[ChannelProcess].Value;
                                                        Internal_SetNote(ChannelProcess,-1,0,0);
                                                        break;
                                                //Portamento Down.
                                                case MODFORMAT_PORTADOWN:
                                                        pP->PLAYER_Channels[ChannelProcess].ActualPeriod += pP->PLAYER_Channels[ChannelProcess].Value;
                                                        Internal_SetNote(ChannelProcess,-1,0,0);
                                                        break;
                                                //Volume Slide
                                                case MODFORMAT_VOLUMESLIDE:
                                                        Internal_VolumeSlide(ChannelProcess);
                                                        break;
                                                //Porta To Note
                                                case MODFORMAT_PORTATONOTE:
                                                        Internal_PortaToNote(ChannelProcess);
                                                        break;
                                                //Vibrato
                                                case MODFORMAT_VIBRATO:
                                                        Internal_Vibrato(ChannelProcess);
                                                        break;
                                                //Porta to note + Volume Slide
                                                case MODFORMAT_PORTAVOLSLIDE:
                                                        Internal_VolumeSlide(ChannelProcess);
                                                        Internal_PortaToNote(ChannelProcess);
                                                        break;
                                                //Vibrato + Volume Slide
                                                case MODFORMAT_VIBRATOVOLSLIDE:
                                                        Internal_Vibrato(ChannelProcess);
                                                        Internal_VolumeSlide(ChannelProcess);
                                                        break;
                                                //Delay note
                                                case MODFORMAT_EDELAYNOTE:
                                                        if (pP->PLAYER_TempoCount != pP->PLAYER_Channels[ChannelProcess].Value)
                                                                break;
                                                        Internal_SetSample(ChannelProcess,pP->PLAYER_Channels[ChannelProcess].Sample);
                                                        Internal_SetNote(ChannelProcess,0,0,0);
                                                        break;
                                                //Cut Note
                                                case MODFORMAT_ECUTNOTE:
                                                        if (pP->PLAYER_TempoCount < pP->PLAYER_Channels[ChannelProcess].Value)
                                                                break;
                                                        Mixer_SetChannelVolume(ChannelProcess,0,0);
                                                        break;
                                                //Retrig Note
                                                case MODFORMAT_ERETRIGNOTE:
                                                        if ((pP->PLAYER_TempoCount % pP->PLAYER_Channels[ChannelProcess].Value) == 0)
                                                                Internal_SetNote(ChannelProcess,0,0,0);
                                                        break;
                                                default:
                                                        break;
                                        }
                                }
                        }
                }
        }
        //Procesado de un ROW del modulo
        //----------------------------------------------------------
        if ( (Actualice) && (pM->MOD_State != TLOTB_STOPED) && (pP->PLAYER_PatternDelay == 0) )
        {
                //Variables para los saltos (Efectos 0x0B y 0x0D.. PatternBreak y JumpPattern)
                unsigned char   BreakPatternFlag;
                unsigned char   JumpPatternFlag;
                unsigned char   LoopFlag;
                unsigned char*  NewActualOrder;
                unsigned char   NewOrder;
                unsigned char   NewRow;
                BreakPatternFlag = 0;
                JumpPatternFlag = 0;
                LoopFlag = 0;
                NewOrder = 0;
                NewRow = 0;

                //Leer nota y actualizar parametros de la tabla.
                //----------------------------------------------
                for (ChannelProcess = 0; ChannelProcess != 4; ChannelProcess++) //4 Numero de canales...
                {
                        //Valores leidos del MOD.
                        unsigned short  Period;
                        unsigned char   Sample;
                        unsigned char   Command;
                        unsigned char   Value;
                        unsigned long   SampleStart;
                        //Variables necesitadas.
                        unsigned char   HiValue;
                        unsigned char   LoValue;

                        //Parametros de arranque del canal
                        //---------------------------------

                        //Obtenemos el numero de sample
                        Sample  = *(pM->MOD_ActualRow) & 0xF0;
                        Sample += *(pM->MOD_ActualRow+2) >> 4;
                        //Obtenemos el periodo
                        Period = *(pM->MOD_ActualRow+1);
                        Period += (*pM->MOD_ActualRow & 0x0F) << 8;
                        //Obtenemos el comando
                        Command = *(pM->MOD_ActualRow+2) & 0x0F;
                        //Obtenemos el valor.
                        Value = *(pM->MOD_ActualRow+3);
                        //Fijamos parametros por defecto.. modificables por los efectos y que han de actuar en consecuencia.
                        SampleStart = 0;

                        //Logica del player, efectos.
                        //----------------------------

                        //Si hay instrumento, hay que resetear el volumen.
                        //Si existe un delay note.. no se ha de realizar esto ahora..
                        //------------------------------------------------------------
                        if ( (Sample != 0) && ( Command != MODFORMAT_EDELAYNOTE))
                        {
                                pP->PLAYER_Channels[ChannelProcess].Sample = Sample;
                                Internal_SetSample(ChannelProcess,Sample);
                        }

                        //Si existe un efecto que atender...
                        //------------------------------------
                        if ( (Command) || (Value))
                        {
                                switch(Command)
                                {
                                        //Arpegio
                                        case MODFORMAT_ARPEGIO:
                                                pP->PLAYER_Channels[ChannelProcess].Command = Command;
                                                pP->PLAYER_Channels[ChannelProcess].CommandProcessed = 0x00;
                                                if (Period != 0)
                                                        pP->PLAYER_Channels[ChannelProcess].ArpeggioPeriod = Period;
                                                else
                                                        pP->PLAYER_Channels[ChannelProcess].ArpeggioPeriod = pP->PLAYER_Channels[ChannelProcess].ActualPeriod;
                                                if ( pP->PLAYER_Channels[ChannelProcess].ArpeggioPeriod == 0) 
                                                        pP->PLAYER_Channels[ChannelProcess].CommandProcessed = 0x01;
                                                pP->PLAYER_Channels[ChannelProcess].Value = Value;
                                                if (Value == 0)
                                                        pP->PLAYER_Channels[ChannelProcess].CommandProcessed = 0x01;
                                                break;
                                        //Tremolo
                                        case MODFORMAT_TREMOLO:
                                                if (Value)
                                                {
                                                        pP->PLAYER_Channels[ChannelProcess].TremoloSpeed = (Value & 0xF0)>>4;
                                                        pP->PLAYER_Channels[ChannelProcess].TremoloDepth = (Value & 0x0F);
                                                }
                                                pP->PLAYER_Channels[ChannelProcess].Command = Command;
                                                pP->PLAYER_Channels[ChannelProcess].CommandProcessed = 0x00;
                                                if (pP->PLAYER_TremoloWaveForm < 4)
                                                        pP->PLAYER_Channels[ChannelProcess].TremoloPos = 31; 
                                                pP->PLAYER_Channels[ChannelProcess].TremoloVolume = pP->PLAYER_Channels[ChannelProcess].Volume;
                                                break;
                                        //Comando SET PANNING
                                        case MODFORMAT_PANNING:
                                                pP->PLAYER_Channels[ChannelProcess].Panning = Value;
                                                break;
                                        //Comando SETVOLUME (Cambia el volume de la nota sea cual sea este).
                                        case MODFORMAT_SETVOLUME:
                                                pP->PLAYER_Channels[ChannelProcess].Volume = Value;
                                                Internal_SetVolume(ChannelProcess,0);
                                                break;
                                        //Comando SETSPEED (Cambia la velocidad o los BPM's dependiendo del rango del parámetro)
                                        case MODFORMAT_SETSPEED:
                                                if (Value == 0)
                                                        break;
                                                if (Value>=0x20)
                                                {
                                                        //Cambiamos los Bpm's
                                                        Internal_SetBPM(Value);
                                                        break;
                                                }
                                                //Cambiamos la "speed"
                                                pM->MOD_Tempo = Value;
                                                pP->PLAYER_TempoCount = 1;
                                                break;
                                        //Comando VOLUME SLIDE.. programamos la accion para entre ticks.
                                        case MODFORMAT_VOLUMESLIDE:
                                                HiValue = Value & 0xF0;
                                                LoValue = Value & 0x0F;
                                                //Solo se admite UP o DOWN (no los dos a la vez...)
                                                if ((HiValue) && (LoValue))
                                                        break;
                                                pP->PLAYER_Channels[ChannelProcess].Command = Command;
                                                pP->PLAYER_Channels[ChannelProcess].CommandProcessed = 0x00;
                                                pP->PLAYER_Channels[ChannelProcess].Value = Value;
                                                break;
                                        //Comando PORTA TO NOTE (Programa un slide de periodo)
                                        case MODFORMAT_PORTATONOTE:
                                                if (Period !=0)
                                                        pP->PLAYER_Channels[ChannelProcess].Period  = Period;
                                                if (Value !=0)
                                                        pP->PLAYER_Channels[ChannelProcess].PortaToNoteSpeed = Value;
                                                Period =0;
                                                pP->PLAYER_Channels[ChannelProcess].Command  = Command;
                                                pP->PLAYER_Channels[ChannelProcess].CommandProcessed = 0x00;
                                                break;
                                        //Comando SAMPLE OFFSET (cambia el inicio de un sample)
                                        case MODFORMAT_SAMPLEOFFSET:
                                                if (Value == 0)
                                                        Value = pP->PLAYER_Channels[ChannelProcess].LastSampleOffset;
                                                SampleStart = Value << 8;
                                                pP->PLAYER_Channels[ChannelProcess].LastSampleOffset = Value;
                                                break;
                                        //Comando PATTERN BREAK(incrementa order y salta al row indicado)
                                        case MODFORMAT_PATTERNBREAK:
                                                HiValue = Value & 0xF0;
                                                LoValue = Value & 0x0F;
                                                HiValue >>= 4;
                                                NewRow = (HiValue*10)+LoValue;
                                                if (NewRow > 63)
                                                        NewRow = 0;
                                                if ((!BreakPatternFlag) && (!JumpPatternFlag))
                                                {
                                                        NewOrder = pM->MOD_Order +1;
                                                        NewActualOrder = pM->MOD_ActualOrder +1;
                                                }
                                                BreakPatternFlag = 1;
                                                break;
                                        //Comando JUMP TO PATTERN
                                        case MODFORMAT_JUMPTOPATTERN:
                                                if (JumpPatternFlag)
                                                        break;
                                                NewOrder = Value;
                                                NewActualOrder = pM->MOD_PatternsOrder+Value;
                                                NewRow = 0;
                                                JumpPatternFlag = 1;
                                                break;
                                        //Comando VIBRATO
                                        case MODFORMAT_VIBRATO:
                                                if (Value)
                                                {
                                                        pP->PLAYER_Channels[ChannelProcess].VibratoSpeed = (Value & 0xF0)>>4;
                                                        pP->PLAYER_Channels[ChannelProcess].VibratoDepth = (Value & 0x0F);
                                                }
                                                if (pP->PLAYER_VibratoWaveForm < 4)
                                                        pP->PLAYER_Channels[ChannelProcess].VibratoPos = 31; 
                                                pP->PLAYER_Channels[ChannelProcess].Command = Command;
                                                pP->PLAYER_Channels[ChannelProcess].CommandProcessed = 0x00;
                                                if (Period != 0)
                                                        pP->PLAYER_Channels[ChannelProcess].VibratoPeriod = Period;
                                                else
                                                        pP->PLAYER_Channels[ChannelProcess].VibratoPeriod = pP->PLAYER_Channels[ChannelProcess].ActualPeriod;
                                                //Comprobacion de que no nos den un Vibrato sin periodo previo.
                                                if (pP->PLAYER_Channels[ChannelProcess].VibratoPeriod == 0)
                                                        pP->PLAYER_Channels[ChannelProcess].CommandProcessed = 0x01;
                                                break;
                                        //Porta To Note + Volume Slide
                                        case MODFORMAT_PORTAVOLSLIDE:
                                                HiValue = Value & 0xF0;
                                                LoValue = Value & 0x0F;
                                                //Solo se admite UP o DOWN (no los dos a la vez...)
                                                if ((HiValue) && (LoValue))
                                                        break;
                                                pP->PLAYER_Channels[ChannelProcess].Command = Command;
                                                pP->PLAYER_Channels[ChannelProcess].CommandProcessed = 0x00;
                                                pP->PLAYER_Channels[ChannelProcess].Value = Value;
                                                break;
                                        //Vibrato + Volume Slide
                                        case MODFORMAT_VIBRATOVOLSLIDE:
                                                HiValue = Value & 0xF0;
                                                LoValue = Value & 0x0F;
                                                //Solo se admite UP o DOWN (no los dos a la vez...)
                                                if ((HiValue) && (LoValue))
                                                        break;
                                                if (pP->PLAYER_VibratoWaveForm < 4)
                                                        pP->PLAYER_Channels[ChannelProcess].VibratoPos = 31; 
                                                pP->PLAYER_Channels[ChannelProcess].Command = Command;
                                                pP->PLAYER_Channels[ChannelProcess].CommandProcessed = 0x00;
                                                pP->PLAYER_Channels[ChannelProcess].Value = Value;
                                                break;
                                        //Portamento arriba.
                                        case MODFORMAT_PORTAUP:
                                                pP->PLAYER_Channels[ChannelProcess].Command = Command;
                                                pP->PLAYER_Channels[ChannelProcess].Value = Value;
                                                pP->PLAYER_Channels[ChannelProcess].CommandProcessed = 0x0;
                                                break;
                                        //Portamento abajo.
                                        case MODFORMAT_PORTADOWN:
                                                pP->PLAYER_Channels[ChannelProcess].Command = Command;
                                                pP->PLAYER_Channels[ChannelProcess].Value = Value;
                                                pP->PLAYER_Channels[ChannelProcess].CommandProcessed = 0x0;
                                                break;

                                        //Comandos Extendidos (0Ex)
                                        //-------------------------
                                        case MODFORMAT_ECOMMAND:
                                                HiValue = Value & 0XF0;
                                                switch(HiValue)
                                                {
                                                        //Fine Volume Slide UP
                                                        case MODFORMAT_EFINEVOLSLIDEUP:
                                                                pP->PLAYER_Channels[ChannelProcess].Volume += Value & 0x0F;
                                                                if (pP->PLAYER_Channels[ChannelProcess].Volume > 64)
                                                                        pP->PLAYER_Channels[ChannelProcess].Volume = 64;
                                                                Internal_SetVolume(ChannelProcess,0);
                                                                break;
                                                        //Fine Volume Slide Down
                                                        case MODFORMAT_EFINEVOLSLIDEDOWN:
                                                                pP->PLAYER_Channels[ChannelProcess].Volume -= Value & 0x0F;
                                                                if (pP->PLAYER_Channels[ChannelProcess].Volume>64)
                                                                        pP->PLAYER_Channels[ChannelProcess].Volume=0;
                                                                Internal_SetVolume(ChannelProcess,0);
                                                                break;
                                                        //Fine portamento up (incrementar el periodo)
                                                        case MODFORMAT_EFINEPORTAUP:
                                                                LoValue = Value & 0x0F;
                                                                pP->PLAYER_Channels[ChannelProcess].ActualPeriod += LoValue;
                                                                Internal_SetNote(ChannelProcess,-1,0,0);
                                                                break;
                                                        //Fine portamente down (decrementar el periodo)
                                                        case MODFORMAT_EFINEPORTADOWN:
                                                                LoValue = Value & 0x0F;
                                                                pP->PLAYER_Channels[ChannelProcess].ActualPeriod -= LoValue;
                                                                Internal_SetNote(ChannelProcess,-1,0,0);
                                                                break;
                                                        //Pattern Delay
                                                        case MODFORMAT_EPATTERNDELAY:
                                                                pP->PLAYER_PatternDelay = (Value & 0x0F)+1;
                                                                break;
                                                        //Set Vibrato WaveForm
                                                        case MODFORMAT_ESETVIBRATOWAVE:
                                                                pP->PLAYER_VibratoWaveForm = Value & 0x0F;
                                                                break;
                                                        //Set Tremolo WaveForm
                                                        case MODFORMAT_ESETTREMOLOWAVE:
                                                                pP->PLAYER_TremoloWaveForm = (Value & 0x0F);
                                                                break;
                                                        //Delay Note
                                                        case MODFORMAT_EDELAYNOTE:
                                                                pP->PLAYER_Channels[ChannelProcess].Sample = Sample;
                                                                pP->PLAYER_Channels[ChannelProcess].ActualPeriod = Period;
                                                                pP->PLAYER_Channels[ChannelProcess].Period = Period;
                                                                pP->PLAYER_Channels[ChannelProcess].Value = (Value & 0x0F);
                                                                pP->PLAYER_Channels[ChannelProcess].Command = (Value & 0xF0);
                                                                pP->PLAYER_Channels[ChannelProcess].CommandProcessed = 0x00;
                                                                //No playear ahora...
                                                                Period = 0;
                                                                break;
                                                        //Extendido CUTNOTE
                                                        case MODFORMAT_ECUTNOTE:
                                                                pP->PLAYER_Channels[ChannelProcess].Command = (Value & 0xF0);
                                                                pP->PLAYER_Channels[ChannelProcess].CommandProcessed = 0x00;
                                                                pP->PLAYER_Channels[ChannelProcess].Value = (Value & 0x0F);
                                                                break;
                                                        //Extendido RETRIG NOTE
                                                        case MODFORMAT_ERETRIGNOTE:
                                                                pP->PLAYER_Channels[ChannelProcess].Command = (Value & 0xF0);
                                                                pP->PLAYER_Channels[ChannelProcess].CommandProcessed = 0x00;
                                                                pP->PLAYER_Channels[ChannelProcess].Value = (Value & 0x0F);
                                                                break;
                                                        //Extendido SET FINETUNE
                                                        case MODFORMAT_ESETFINETUNE:
                                                                if (Sample == 0)
                                                                        break;
                                                                pM->MOD_SampleFineTune[Sample-1] = (Value & 0x0F);
                                                                break;
                                                        //Extendido SET LOOP - JUMP LOOP
                                                        case MODFORMAT_EPATTERNLOOP:
                                                                if ((Value & 0x0F) == 0)
                                                                {
                                                                        pP->PLAYER_RowLoop = pM->MOD_Row;
                                                                }
                                                                else
                                                                {
                                                                        if  (pP->PLAYER_LoopTimes == 0)
                                                                                pP->PLAYER_LoopTimes = (Value & 0x0f);
                                                                        if  (pP->PLAYER_LoopTimes == 0xff)
                                                                        {
                                                                                pP->PLAYER_LoopTimes = 0;
                                                                                break;
                                                                        }
                                                                        LoopFlag = 0x01;
                                                                }
                                                                break;
                                                        //Extendido GLISANDO CONTROL
                                                        case MODFORMAT_EGLISANDOCONTROL:
                                                                pP->PLAYER_GlisandoControl = (Value & 0x0F);
                                                                break;
                                                        default:
                                                                break;
                                                }
                                        default:
                                                break;
                                }
                                
                        }
                        if (Period != 0)
                        {
                                pP->PLAYER_Channels[ChannelProcess].ActualPeriod = Period;
                                Internal_SetNote(ChannelProcess,SampleStart,0,0);
                        }
                        pM->MOD_ActualRow += 4; //4 Bytes cada canal..
                }
                //Control de saltos.
                if ( (BreakPatternFlag) || (JumpPatternFlag))
                {
                        pM->MOD_Row = NewRow;
                        pM->MOD_ActualOrder = NewActualOrder;
                        pM->MOD_Order = NewOrder;
                        if (pM->MOD_Order >= pM->MOD_NumOrders)
                        {
                                //(Comprobar si loop)
                                //MOD Finished!!!
                                //----------------------
                                pM->MOD_State = TLOTB_STOPED;
                                return;
                        }
                        pM->MOD_ActualRow = pM->MOD_PatternsOffset+((*pM->MOD_ActualOrder) << 10);
                        pM->MOD_ActualRow += pM->MOD_Row * (4*4); // 4canales...
                }
                else
                {
                        //Bajamos un row
                        //--------------
                        pM->MOD_Row++;
                }
                //Control de loops
                if ( (LoopFlag) && (pP->PLAYER_LoopTimes != 0xff))
                {
                        pM->MOD_Row = pP->PLAYER_RowLoop;
                        pM->MOD_ActualRow = pM->MOD_PatternsOffset+((*pM->MOD_ActualOrder) << 10);
                        pM->MOD_ActualRow += pM->MOD_Row * (4*4); // 4canales...
                        pP->PLAYER_LoopTimes--;
                        if (pP->PLAYER_LoopTimes == 0)
                                pP->PLAYER_LoopTimes = 0xff;
                }
                //Control de avance
                if (pM->MOD_Row == 64)
                {
                        //Cambiar de pattern
                        pM->MOD_Order++;
                        pM->MOD_ActualOrder++;
                        if (pM->MOD_Order >= pM->MOD_NumOrders)
                        {
                                //MOD Finished!!!
                                //----------------------
                                pM->MOD_State = TLOTB_STOPED;
                                return;
                        }
                        else
                        {
                                pM->MOD_ActualRow = pM->MOD_PatternsOffset+((*pM->MOD_ActualOrder) << 10); //(Idem.. *1024 ... 4 canales)
                                pM->MOD_Row = 0;
                        }
                }
        }
        if (Actualice)
                if (pP->PLAYER_PatternDelay > 0)
                        pP->PLAYER_PatternDelay--;
}

//Modifica la temporizacion (BPM) del player
//---------------------------------------------
static void Internal_SetBPM(unsigned char BPM)
{
        unsigned short Hertz;

        //Almacenamos los nuevos BPM's
        pM->MOD_Bpm = BPM;
        //Obtenemos los hz a los que va este nuevo BPM
        Hertz = (BPM<<1) /5;
        pM->MOD_BpmSpeed = (Hertz << 16) / (pP->PLAYER_BpmRate);
        pP->PLAYER_BpmSpeedCount = 0;
}

//Modifica la frecuencia de un instrumento
//----------------------------------------
static void Internal_SetNote(int wChannel,unsigned long Pos,unsigned long FreqAdd,unsigned char Arpeggio)
{
        unsigned long   Frequency;              //Para los calculos de frecuencia.
        unsigned short  Period;
        unsigned char   Finetune;
        
        //Este calculo da como resultado la frecuencia del sample
        //dado su periodo, la constante de actualizacion de un AMIGA NTSC
        //y nuestra frecuencia de replay (GBA 22Khz)
        if (pP->PLAYER_Channels[wChannel].ActualPeriod == 0)
                return;
        Period = pP->PLAYER_Channels[wChannel].ActualPeriod;
        Finetune = pP->PLAYER_Channels[wChannel].ActualFineTune;
        Period =Internal_FindPeriodFinetune(Period,pP->PLAYER_Channels[wChannel].ActualFineTune,Arpeggio);
        //NTSC 7159090.5 //PAL 7093789.2
        Frequency = (7159090 << 8) + (1 << 7);
        Frequency /= Period; 
        Frequency += pP->PLAYER_OutputFrequency - 1;
        Frequency /= pP->PLAYER_OutputFrequency;
        Frequency <<= 1;
        Frequency += FreqAdd;
        //Si nos indican posicion para el sample, la usamos.. en caso contrario modificamos solo frecuencia.
        if (Pos == -1)
                Mixer_SetChannelStep ( wChannel,Frequency);
        else
                Mixer_SetChannelNote ( wChannel,Pos << 10,Frequency);
}

//Realiza un volume Slide segun Value en nuestra estructura de canal
//-------------------------------------------------------------------
static void Internal_VolumeSlide(int wChannel)
{
        unsigned char Volume;
        
        Volume = pP->PLAYER_Channels[wChannel].Volume;
        if (pP->PLAYER_Channels[wChannel].Value > 0x0f)                 
        {
                Volume += (pP->PLAYER_Channels[wChannel].Value >> 4);
                if (Volume>64)
                        Volume=64;
        }
        else
        {
                Volume -= (pP->PLAYER_Channels[wChannel].Value);
                if (Volume>64)
                        Volume=0;
        }
        pP->PLAYER_Channels[wChannel].Volume = Volume;
        Internal_SetVolume(wChannel,0);
}



//Efecto Vibrato
//----------------------------------------
static void Internal_Vibrato(int wChannel)
{
        unsigned short VibratoPeriod;
        unsigned char WaveFormValue;
        

        switch(pP->PLAYER_VibratoWaveForm & 0x3) // En este momento no nos preocupa el "retriggered"
        {
                case 0: // Sinus
                case 3:
                        WaveFormValue = MODFORMAT_SinTab[pP->PLAYER_Channels[wChannel].VibratoPos];
                        break;
                case 1: // Rampdown
                        
                        if (pP->PLAYER_Channels[wChannel].VibratoPos<=31)
                                WaveFormValue = 255 -((pP->PLAYER_Channels[wChannel].VibratoPos + 31)<<3);
                        else
                                WaveFormValue = pP->PLAYER_Channels[wChannel].VibratoPos<<3;
                        break;
                case 2:
                        WaveFormValue = 255;
                        break;

        }
        if (pP->PLAYER_Channels[wChannel].VibratoPos>=31)
        {
                VibratoPeriod = pP->PLAYER_Channels[wChannel].VibratoPeriod -
                ((pP->PLAYER_Channels[wChannel].VibratoDepth*
                WaveFormValue)>>7);
        }
        else
        {
                VibratoPeriod = pP->PLAYER_Channels[wChannel].VibratoPeriod +
                ((pP->PLAYER_Channels[wChannel].VibratoDepth*
                WaveFormValue)>>7);
        }

        pP->PLAYER_Channels[wChannel].VibratoPos+=pP->PLAYER_Channels[wChannel].VibratoSpeed;
        if (pP->PLAYER_Channels[wChannel].VibratoPos>62)
                pP->PLAYER_Channels[wChannel].VibratoPos=0;

        pP->PLAYER_Channels[wChannel].ActualPeriod = VibratoPeriod;
        Internal_SetNote(wChannel,-1,0,0);
}

//Fija un instrumento a un canal
//------------------------------------------
static void Internal_SetSample(int wChannel,unsigned char Sample)
{
        pP->PLAYER_Channels[wChannel].Volume = pM->MOD_SampleVolume[Sample-1];
        pP->PLAYER_Channels[wChannel].ActualFineTune = pM->MOD_SampleFineTune[Sample-1];
        //Reseteamos el volumen pero tambien fijamos el instrumento (El sample base, pero no su origen ni nada mas..)

    // Pone las notas
    Mixer_SetChannelSample ( wChannel, 
                            pM->MOD_SampleOffset[Sample-1], 
                            pM->MOD_SampleLenght[Sample-1], 
                            pM->MOD_SampleLoopStart[Sample-1]);

        Internal_SetVolume(wChannel,0);
}

//Realiza un efecto de arpegio
//-------------------------------------------------------------
static void Internal_DoArpegio(int wChannel,unsigned long Tick)
{
        if ((Tick & 3) == 0)
                Internal_SetNote(wChannel,-1,0,0);

        if ((Tick & 3) == 1)
                Internal_SetNote(wChannel,-1,0,((pP->PLAYER_Channels[wChannel].Value & 0xF0) >> 4));
        if ((Tick & 3) == 2)
                Internal_SetNote(wChannel,-1,0,(pP->PLAYER_Channels[wChannel].Value & 0x0F));
        
}


//Efecto Tremolo
//----------------------------------------
static void Internal_Tremolo(int wChannel)
{
        unsigned long TremoloVol;
        unsigned char WaveFormValue=0;

        switch(pP->PLAYER_TremoloWaveForm & 0x3) // En este momento no nos preocupa el "retriggered"
        {
                case 0: // Sinus
                case 3:
                        WaveFormValue = MODFORMAT_SinTab[pP->PLAYER_Channels[wChannel].TremoloPos];
                        break;
                case 1: // Rampdown
                        
                        if (pP->PLAYER_Channels[wChannel].TremoloPos<=31)
                                WaveFormValue = 255 -((pP->PLAYER_Channels[wChannel].TremoloPos + 31)<<3);
                        else
                                WaveFormValue = pP->PLAYER_Channels[wChannel].TremoloPos<<3;
                        break;
                case 2:
                        WaveFormValue = 255;
                        break;

        }
        WaveFormValue*=pP->PLAYER_Channels[wChannel].TremoloDepth;
        WaveFormValue>>=6;
        if (pP->PLAYER_Channels[wChannel].TremoloPos>=31)
        {
                if ((pP->PLAYER_Channels[wChannel].TremoloVolume - WaveFormValue)<0)
                        TremoloVol = WaveFormValue;
                else
                        TremoloVol = pP->PLAYER_Channels[wChannel].TremoloVolume - WaveFormValue;
        }
        else
        {
                if ((pP->PLAYER_Channels[wChannel].TremoloVolume + WaveFormValue)>64)
                        TremoloVol = 64-WaveFormValue;
                else
                        TremoloVol = pP->PLAYER_Channels[wChannel].TremoloVolume + WaveFormValue;
        }

        pP->PLAYER_Channels[wChannel].TremoloPos+=pP->PLAYER_Channels[wChannel].TremoloSpeed;
        if (pP->PLAYER_Channels[wChannel].TremoloPos>62)
                pP->PLAYER_Channels[wChannel].TremoloPos=0;
        Internal_SetVolume(wChannel,(unsigned char)TremoloVol);
}

//Devuelve el periodo asociado a un periodo mas un finetune
//----------------------------------------------------------------------------------------------
static unsigned short Internal_FindPeriodFinetune(unsigned short Period,unsigned char FineTune,unsigned char Arpeggio)
{
        #define TABLE_SIZE 75 // Tamaño de nuestra tabla de periodos

        unsigned char  Pos=TABLE_SIZE>>1;
        unsigned short MaxPos = TABLE_SIZE-1;
        unsigned short MinPos = 0;
        short              LastPos = -1;
        
        //Búsqueda binaria
        while (1)
        {
                if (PeriodTable_0[Pos]==Period)
                        return FinetuneTables[FineTune][Pos+Arpeggio];
                if (PeriodTable_0[Pos]<Period)
                {
                        MaxPos  = Pos;
                        Pos=(MaxPos-MinPos)>>1;
                        if (Pos == LastPos)
                        {
                                return FinetuneTables[FineTune][Pos+Arpeggio];
                        }
                        LastPos = Pos;
                        continue;
                }

                if (PeriodTable_0[Pos]>Period)
                {
                        MinPos = Pos;
                        Pos=Pos+((MaxPos-MinPos)>>1);
                        if (Pos == LastPos)
                                return FinetuneTables[FineTune][Pos+Arpeggio];
                        
                        LastPos = Pos;
                        continue;
                }
         }
}


//Fija el volumen de un canal a partir del volumen actual y calculando panning
//----------------------------------------------------------------------------
static void Internal_SetVolume(int wChannel,unsigned char Volume)
{
        unsigned long VolLeft,VolRight;
        unsigned long InverseVolume;
        ASSERT(Volume <= 64);
        if (Volume == 64)
                Volume = 63;
        if (!Volume)
        {
                VolLeft = pP->PLAYER_Channels[wChannel].Volume << 1;
                VolRight = pP->PLAYER_Channels[wChannel].Volume << 1;
        }
        else
        {
                VolLeft = (unsigned char)Volume << 1;
                VolRight = (unsigned char)Volume << 1;
        }

        //Panning!!!!
        //FastTracker 2 format! ;) 00 full left ff full right 80 middle
        //-------------------------------------------------------------
        if (pP->PLAYER_Channels[wChannel].Panning < 0x80)
        {
                InverseVolume = 0x80 - pP->PLAYER_Channels[wChannel].Panning;
                VolRight -= InverseVolume;
                if (VolRight > 128)
                        VolRight = 0;
        }
        if (pP->PLAYER_Channels[wChannel].Panning > 0x80)
        {
                InverseVolume = pP->PLAYER_Channels[wChannel].Panning - 0x80;
                VolLeft -= InverseVolume;
                if (VolLeft > 128)
                        VolLeft = 0;
        }
        Mixer_SetChannelVolume ( wChannel,VolLeft,VolRight);
}


//Efecto Porta To Note... 
//--------------------------------------------
static void Internal_PortaToNote(int wChannel)
{
        if (pP->PLAYER_Channels[wChannel].ActualPeriod > pP->PLAYER_Channels[wChannel].Period)
        {
                if (!pP->PLAYER_GlisandoControl)
                        pP->PLAYER_Channels[wChannel].ActualPeriod-=pP->PLAYER_Channels[wChannel].PortaToNoteSpeed;
                else
                        pP->PLAYER_Channels[wChannel].ActualPeriod=Internal_FindPeriodFinetune(pP->PLAYER_Channels[wChannel].ActualPeriod,
                        0,1);

                if (pP->PLAYER_Channels[wChannel].ActualPeriod <= pP->PLAYER_Channels[wChannel].Period)
                {
                        pP->PLAYER_Channels[wChannel].ActualPeriod =pP->PLAYER_Channels[wChannel].Period;
                        pP->PLAYER_Channels[wChannel].CommandProcessed = 0x1;
                }
                //Chequeamos.. por si nos han dado una velocidad fuera de lo normal
                if (pP->PLAYER_Channels[wChannel].ActualPeriod > 15000)
                {
                        pP->PLAYER_Channels[wChannel].ActualPeriod =pP->PLAYER_Channels[wChannel].Period;
                        pP->PLAYER_Channels[wChannel].CommandProcessed = 0x1;
                }

        }
        else
        {
                if (!pP->PLAYER_GlisandoControl)
                        pP->PLAYER_Channels[wChannel].ActualPeriod+=pP->PLAYER_Channels[wChannel].PortaToNoteSpeed;
                else
                        pP->PLAYER_Channels[wChannel].ActualPeriod=Internal_FindPeriodFinetune(pP->PLAYER_Channels[wChannel].ActualPeriod,
                        0,-1);

                if (pP->PLAYER_Channels[wChannel].ActualPeriod >= pP->PLAYER_Channels[wChannel].Period)
                {
                        pP->PLAYER_Channels[wChannel].ActualPeriod =pP->PLAYER_Channels[wChannel].Period;
                        pP->PLAYER_Channels[wChannel].CommandProcessed = 0x1;
                }
                //Chequeamos.. por si nos han dado una velocidad fuera de lo normal
                if (pP->PLAYER_Channels[wChannel].ActualPeriod > 15000)
                {
                        pP->PLAYER_Channels[wChannel].ActualPeriod =pP->PLAYER_Channels[wChannel].Period;
                        pP->PLAYER_Channels[wChannel].CommandProcessed = 0x1;
                }
        }
        Internal_SetNote(wChannel,-1,0,0);
}



