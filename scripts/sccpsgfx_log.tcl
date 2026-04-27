# 
# Binary format PSG logger
#
# (see http://www.msx.org/forumtopic6258.html for more context)
#
# Shiru wrote:
# 
#  Is it possible to make output in standart binary *.psg format (used in
#  emulators like x128, very-very old version of fMSX, Z80Stealth and some other)?
#
#  Header:
#
#   +0 4 Signature #50 #53 #47 #1A ('PSG' and byte #1A)
#   +4 1 Version number
#   +5 1 Interrupts freq. (50/60)
#   +6 10 Unused
#
#  Note: only signature is necessary, many emulators just fill other bytes by zero.
# 
#  Data stream:
# 
#  #00..#FC - register number, followed by data byte (value for that register)
#  #FD - EOF (usually not used in real logs, and not all progs can handle it)
#  #FE - number of interrupts (followed byte with number of interrupts/4, usually not used)
#  #FF - single interrupt
#

set_help_text sccpsgfx_log \
{This script logs PSG registers 0 through 14 to a file at every frame end.
The file format is the PSG format used in some emulators. More information
is here:  http://www.msx.org/forumtopic6258.html (and in the comments of
this script).

Usage:
   sccpsgfx_log start <filename>  start logging PSG registers to <filename> 
                             (default: log.psg)
   sccpsgfx_log stop              stop logging PSG registers

Examples:
   sccpsgfx_log start             start logging registers to default file log.psg
   sccpsgfx_log start myfile.psg  start logging to file myfile.psg
   sccpsgfx_log stop              stop logging PSG registers
}

set_tabcompletion_proc sccpsgfx_log tab_sccpsgfx_log
proc tab_sccpsgfx_log { args } {
	if {[llength $args] == 2} {
		return "start stop"
	}
}

set __sccpsgfx_log_file -1

set array psg{}
set array psgold{}
set array scc{}
set array sccold{}

proc sccpsgfx_log { subcommand {filename "data.mus"} } {
	global __sccpsgfx_log_file
	global array psg
	global array psgold	
	global array scc
	global array sccold

	
	if [string equal $subcommand "start"] {
		set __sccpsgfx_log_file [open $filename {WRONLY TRUNC CREAT}]
		fconfigure $__sccpsgfx_log_file -translation binary
		
		# Init registers
		
		puts -nonewline $__sccpsgfx_log_file [binary format c 0xF0]
		
		# PSG Freq
		
		set psg(0)		[debug read "PSG regs" 0]
		set psgold(0)	[debug read "PSG regs" 0]
        puts -nonewline $__sccpsgfx_log_file [binary format c2 "0 $psg(0)"]	

		set psg(1)		[debug read "PSG regs" 1]
		set psgold(1)	[debug read "PSG regs" 1]
        puts -nonewline $__sccpsgfx_log_file [binary format c2 "1 $psg(1)"]			
		
		# PSG Noise
		
		set psg(6)		[debug read "PSG regs" 6]
		set psgold(6)	[debug read "PSG regs" 6]		
        puts -nonewline $__sccpsgfx_log_file [binary format c2 "6 $psg(6)"]			
        
        # PSG Mixer
        
		set psg(7)		[debug read "PSG regs" 7]
		set psgold(7)	[debug read "PSG regs" 7]
        puts -nonewline $__sccpsgfx_log_file [binary format c2 "7 $psg(7)"]			
		
		# PSG Vol
		
		set psg(8)		[debug read "PSG regs" 8]
		set psgold(8)	[debug read "PSG regs" 8]
        puts -nonewline $__sccpsgfx_log_file [binary format c2 "8 $psg(8)"]			
		
		
		

		
		


		puts -nonewline $__sccpsgfx_log_file [binary format c 0xF1]

		
	    # SCC Freq
	    
        set reg [expr 0 + 0x80]
        set value [debug read "SCC SCC" [expr 0 + 0xA0]]
        set scc($reg) $value
        set sccold($reg) $value
        puts -nonewline $__sccpsgfx_log_file [binary format c2 "$reg $value"]
        
        set reg [expr 1 + 0x80]
        set value [debug read "SCC SCC" [expr 1 + 0xA0]]
        set scc($reg) $value
        set sccold($reg) $value
        puts -nonewline $__sccpsgfx_log_file [binary format c2 "$reg $value"]

        # SCC Vol

        set reg [expr 10 + 0x80]
        set value [debug read "SCC SCC" [expr 10 + 0xA0]]
        set scc($reg) $value
        set sccold($reg) $value
        puts -nonewline $__sccpsgfx_log_file [binary format c2 "$reg $value"]
        

        # SCC Mixer

        set reg [expr 15 + 0x80]
        set value [debug read "SCC SCC" [expr 15 + 0xA0]]
        set scc($reg) $value
        set sccold($reg) $value
        puts -nonewline $__sccpsgfx_log_file [binary format c2 "$reg $value"]
        
        
		
		



		puts -nonewline $__sccpsgfx_log_file [binary format c 0xF2]
		for {set i 0} {$i < 16} {incr i} {
				set scc($i)		[debug read "SCC SCC" $i]
				set sccold($i)	[debug read "SCC SCC" $i]
				puts -nonewline $__sccpsgfx_log_file [binary format c2 "$i $scc($i)"]	
		}

		
		
		__do_sccpsgfx_log
		return ""
	} elseif [string equal $subcommand "stop"] {
		close $__sccpsgfx_log_file
		set __sccpsgfx_log_file -1
		return ""
	} else {
		error "bad option \"$subcommand\": must be start, stop"
	}
}

proc __do_sccpsgfx_log {} {
	global __sccpsgfx_log_file
	global array psg
	global array psgold	
	global array scc
	global array sccold


	
	if {$__sccpsgfx_log_file == -1} return
	
	
	# Psg Regs
	
	set putPSG	0
	set putSCC	0
	

    set i 0
	set value [debug read "PSG regs" $i]
	set psg($i) $value
	if {$psg($i) != $psgold($i)} {
			
			if {$putPSG == 0} {
					puts -nonewline $__sccpsgfx_log_file [binary format c 0xF0]
					set putPSG 1
			}
	
			puts -nonewline $__sccpsgfx_log_file [binary format c2 "$i $value"]
			set psgold($i) $value
	}
				

    set i 1
	set value [debug read "PSG regs" $i]
	set psg($i) $value
	if {$psg($i) != $psgold($i)} {
			
			if {$putPSG == 0} {
					puts -nonewline $__sccpsgfx_log_file [binary format c 0xF0]
					set putPSG 1
			}
	
			puts -nonewline $__sccpsgfx_log_file [binary format c2 "$i $value"]
			set psgold($i) $value
	}


    set i 6
	set value [debug read "PSG regs" $i]
	set psg($i) $value
	if {$psg($i) != $psgold($i)} {
			
			if {$putPSG == 0} {
					puts -nonewline $__sccpsgfx_log_file [binary format c 0xF0]
					set putPSG 1
			}
	
			puts -nonewline $__sccpsgfx_log_file [binary format c2 "$i $value"]
			set psgold($i) $value
	}


    set i 7
	set value [debug read "PSG regs" $i]
	set psg($i) $value
	if {$psg($i) != $psgold($i)} {
			
			if {$putPSG == 0} {
					puts -nonewline $__sccpsgfx_log_file [binary format c 0xF0]
					set putPSG 1
			}
	
			puts -nonewline $__sccpsgfx_log_file [binary format c2 "$i $value"]
			set psgold($i) $value
	}


    set i 8
	set value [debug read "PSG regs" $i]
	set psg($i) $value
	if {$psg($i) != $psgold($i)} {
			
			if {$putPSG == 0} {
					puts -nonewline $__sccpsgfx_log_file [binary format c 0xF0]
					set putPSG 1
			}
	
			puts -nonewline $__sccpsgfx_log_file [binary format c2 "$i $value"]
			set psgold($i) $value
	}


	
	# SCC Waves
	

	for {set i 0} {$i < 16} {incr i} {
		set value [debug read "SCC SCC" $i]
		set scc($i) $value
		if {$scc($i) != $sccold($i)} {
				
				if {$putSCC == 0} {
						puts -nonewline $__sccpsgfx_log_file [binary format c 0xF2]
						set putSCC 1
				}
		
				puts -nonewline $__sccpsgfx_log_file [binary format c2 "$i $value"]
				set sccold($i) $value
		}
				
	}


	# SCC Regs
	
	set putSCC 0

	
	set i 0	
	set reg [expr $i + 0x80]
	set value [debug read "SCC SCC" [expr $i + 0xA0]]
	
	
	set scc($reg) $value
	if {$scc($reg) != $sccold($reg)} {
			
			if {$putSCC == 0} {
					puts -nonewline $__sccpsgfx_log_file [binary format c 0xF1]
					set putSCC 1
			}
	
			puts -nonewline $__sccpsgfx_log_file [binary format c2 "$reg $value"]
			set sccold($reg) $value
	}
				

	set i 1
	set reg [expr $i + 0x80]
	set value [debug read "SCC SCC" [expr $i + 0xA0]]
	
	
	set scc($reg) $value
	if {$scc($reg) != $sccold($reg)} {
			
			if {$putSCC == 0} {
					puts -nonewline $__sccpsgfx_log_file [binary format c 0xF1]
					set putSCC 1
			}
	
			puts -nonewline $__sccpsgfx_log_file [binary format c2 "$reg $value"]
			set sccold($reg) $value
	}

	
	set i 10
	set reg [expr $i + 0x80]
	set value [debug read "SCC SCC" [expr $i + 0xA0]]
	
	
	set scc($reg) $value
	if {$scc($reg) != $sccold($reg)} {
			
			if {$putSCC == 0} {
					puts -nonewline $__sccpsgfx_log_file [binary format c 0xF1]
					set putSCC 1
			}
	
			puts -nonewline $__sccpsgfx_log_file [binary format c2 "$reg $value"]
			set sccold($reg) $value
	}


	set i 15
	set reg [expr $i + 0x80]
	set value [debug read "SCC SCC" [expr $i + 0xA0]]
	
	
	set scc($reg) $value
	if {$scc($reg) != $sccold($reg)} {
			
			if {$putSCC == 0} {
					puts -nonewline $__sccpsgfx_log_file [binary format c 0xF1]
					set putSCC 1
			}
	
			puts -nonewline $__sccpsgfx_log_file [binary format c2 "$reg $value"]
			set sccold($reg) $value
	}






	# End of frame
		
	puts -nonewline $__sccpsgfx_log_file [binary format c 0xFF]
	
	
	
	
	after frame __do_sccpsgfx_log
}


