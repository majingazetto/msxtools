/*--------------------------------------------------------------------

    TLOTB Mod Player

	Astharoth / Hgh on July 2002

---------------------------------------------------------------------*/

#ifndef TLOTB_SOUND_PLAYER 
#define TLOTB_SOUND_PLAYER 0xbebecafe

//-----------------Codigos de error------------------------

#define TLOTB_PLAYER_OK         0x0000
#define TLOTB_PLAYER_MODPLAYING	0x0001
#define TLOTB_MODSTILLALLOCATED 0x0002
#define TLOTB_PLAYER_NOMOD      0x0003
#define TLOTB_PLAYER_WRONGMOD   0x0004
#define TLOTB_PLAYER_NOSUCHPAT  0x0005
#define TLOTB_PLAYER_WRONGROW   0x0006

//--------------------Interface-----------------------------
unsigned long TLOTB_InitPlayer();
unsigned long TLOTB_FinishPlayer();
unsigned long TLOTB_LoadMod(const char* MemAddress);
unsigned long TLOTB_FreeMod();
unsigned long TLOTB_PlayMusic();
unsigned long TLOTB_PauseMusic();
unsigned long TLOTB_StopMusic();
unsigned long TLOTB_GetModPosition(unsigned char* Pattern,
                                       unsigned char* Row);
unsigned long TLOTB_SetModPosition(unsigned char Pattern,
                                       unsigned char Row);

//Callback para el play
void ControlChannels ();

#endif
