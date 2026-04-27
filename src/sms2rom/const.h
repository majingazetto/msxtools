/********  CONST  ************/





// *** CONSTANTES MSX ***

#define			SNSMAT			0141h
#define			DISSCR			0041h
#define			ENASCR			0044h
#define			OUTDO			0018h
#define			CHGMOD			005Fh
#define			RDSLT			000Ch
#define			WRSLT			0014h
#define			OUTDO			0018h
#define			CHPUT			00A2H
#define			CSRY			0F3DCh
#define			WRTVDP			0047h		// C regnum, B data
#define			CSRSW			0FCA9h		// 0 not showed

#define			CALSLT			001Ch
#define			KEYINT			0038h
#define			ENASLT			024h

#define			CHSNS			09Ch
#define			CHGET			09Fh
#define			KILBUF			0156h


#define			EXPTBL			0FCC1h
#define         SLTTBL          0FCC5h
#define			EXBRSA			0FAF8h
#define			CLIKSW			0F3DBh
#define			STATFL			0F3E7h
#define			HKEYI			0FD9Ah
#define			HTIMI			0FD9FH
#define			JIFFY			0FC9Eh
#define			RGSAV			0F3DFh	// copia de los registros de VDP 0 - 7
#define			RG0SAV			0F3DFh	// copia de los registros de VDP 0 - 7
#define			EXTVDP			0FFE7h	// copy de los registros VDP 8-23
#define			FORCLR			0F3E9h
#define			BAKCLR			0F3EAh
#define			BDRCLR			0F3EBh
#define			LINL40			0F3AEh
#define			EXTVDPPLUS		0FFFAh // #25 y consecutivos
#define			NEWKEY			0FBE5h
#define			PTRFLG			0F416h		
#define			PTRFIL			0F864h
#define			BOTTOM			0FC48h
#define			HIMEM			0FC4Ah
#define			CAPST			0FCABh
#define			MODE			0FAFCh	// 

#define			LDIRMV			0059h
#define			LDIRVM			005Ch

#define         DPPAGE          0FAF5h
#define         ACPAGE          0FAF6h


// ** BDOS AND DISK ***

#define			ERRADR			0F323h					// Error en DOS1
#define			ABTADR			0F1E5h					// Abort
#define			HSTKE			0FEDAh
#define			HPHYD			0FFA7h					// C9 si no hay disco
#define			RAMAD0			0F341h					// slotid DOS ram page 0
#define			RAMAD1			0F342h					// slotid DOS ram page 1
#define			RAMAD2			0F343h					// slotid DOS ram page 2
#define			RAMAD3			0F344H					// slotid DOS ram page 3


//  *** DOS1 CALLS *** 

#define			BSYSRESET		00h

#define			_STROUT			09h					
#define			_FOPEN			0Fh					
#define			_FCLOSE			010h
#define			_FMAKE			016h
#define			_SETDTA			01Ah
#define			_WRBLK			026h
#define			_RDBLK			027h

//  *** DOS2 CALLS ***

#define			_OPEN			043h
#define			_CREATE			044h
#define			_CLOSE			045h
#define			_READ			048h
#define			_WRITE			049h
#define			_SEEK			04Ah

#define			_DEFAB			063h
#define			_DEFER			064h
#define			_DOSVER			06Fh



// **** SUBROM MSX2 ***

#define			INIPLT			0141h	// init pal
#define         SETPAG          013Dh
#define         EXTROM          015Fh
#define         SUBROM          015Ch

// *** VDP PORTS ***

#define			VDP98			098h
#define			VDP99			VDP98 + 1
#define			VDP9A			VDP98 + 2
#define			VDP9B			VDP98 + 3

// *** VDP VALUES ***

#define			V9918			0		// VDP MSX1 (TSM ...)
#define			V9938			1
#define			V9948			2
#define			V9958			3

// *** KEYBOARD TYPES

#define			KJAPANESE		0
#define			KINTERNATIONAL	1
#define			KFRENCH			2
#define			KUK				3
#define			KGERMAN			4
#define			KUSSR			5
#define			KSPANISH		6

//  *** MUSICA CHIPS DEFINITION ***

#define			MCPSG			1			// Only PSG
#define			MCFM			2			// Only FM
#define			MCSCC			3			// Only SCC
#define			MCPSGFM			4			// PSG + FM
#define			MCPSGSCC		5			// PSG+ SCC
#define			MCFMSCC			6			// FM + SCC	(Raro pero posible)
#define			MCALL			7			// PSG + SCC + FM

// *** MUSICA XTRA DEFINITIONS  ** //

#define			MD_FADE_OUT			1			// Normal Fade out (Fade and Stop Music)
#define			MD_FADE_IN			2			// Fade In (from begin of song)
#define			MD_FADE_OUT_PAUSE	3			// Fade Out and Pause Music
#define			MD_FADE_IN_PAUSE	4			// Fade In from Music Pause (complementary MD_FADE_OUT_PAUSE)
#define			MD_FADE_OUT_CONT	5			// Fade out and continue song (mute)
#define			MD_FADE_IN_CONT		6			// Fade in from playing song ... 

// *** MUSICA JUKEBOX COMMANDS 

#define			CMDMUSICJUKE		128
#define			CMDMUSICJUKE_END	CMDMUSICJUKE + 1
#define			CMDMUSICJUKE_GOTO	CMDMUSICJUKE + 2


// *** TURBO R	 ***

#define			CPUZ80			080h
#define			CPUR800			081h
#define			CPUR800DRAM		082h

// *** SPRITES CONF ***

#define			SPR16X16		2
#define			SPR8X8			0
#define			SPRMAG			1
#define			SPRNOMAG		0



// *** MODELO DE MSX ***

#define			MSX				0
#define			MSX2			1
#define			MSX2P			2
#define			TURBOR			3

#define			MSX_ALL			4		// Modelo para hacer juegos MSX1/MSX2

// *** VALORES DE CPU DEL R800 

#define			Z80				080h
#define			R800			081h
#define			R800DRAM		082h


// *** VDP COMMANDS ***

#define			CMDHIGH			0D0h
#define			CMDTIMP			098h	




// *** ROM DEFINES ***

#define			ENDROM32K		0C000h
#define			ENDROM16K		08000h
#define			ENDROM8K		06000h
#define			ENDROMPAGE0		04000h

// *** TIPOS DE ROM BASICO ***

#define			ROM8K			1
#define			ROM16K			2
#define			ROM32K			3	
#define			ROM48K			4
#define			ROMMEGAROM		5


// *** SOPORTE DE MEGAROM *** 

#define			ASCII8K			1
#define			KONAMI4			2
#define			KONAMI5			3

#define         ASCII8          ASCII8K



#define			ZONEPAGE0		04000h
#define			ZONEPAGE1		06000h
#define			ZONEPAGE2		08000h
#define			ZONEPAGE3		0A000h

// ** CONSTANTES PARA LOADSET ***

#define			LOADSETPAT		1
#define			LOADSETCOL		2
#define			LOADSETATR		4
#define			LOADSETSPR		8

#define			LOADSETPATBIT	0
#define			LOADSETCOLBIT	1
#define			LOADSETATRBIT	2
#define			LOADSETSPRBIT	3

// *** RAMTYPUS ***

#define			RAM8K			0
#define			RAM16K			1
#define			RAM32K			2
#define			RAM48K			3
#define			RAM64K			4

// *** MOVIMIENTOS ***

#define					MOV025			0
#define					MOV05			2
#define					MOV075			4
#define					MOV1			6
#define					MOV11			8
#define					MOV125			10
#define					MOV15			12
#define					MOV175			14
#define					MOV2			16
#define					MOV25			18

// **** FRANKY ***

#define         FVDP88          088h    // Franky Data VDP Port
#define         FVDP89          089h    // Franky Control VDP Port
#define         FPSGVC          048h    // Vertical reg (vdp) / PSG write
#define         FPSGHC          049h    // Hor. reg (vdp) / PSG write


