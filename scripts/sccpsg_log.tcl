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

set_help_text sccpsg_log \
{This script logs PSG registers 0 through 14 to a file at every frame end.
The file format is the PSG format used in some emulators. More information
is here:  http://www.msx.org/forumtopic6258.html (and in the comments of
this script).

Usage:
   sccpsg_log start <filename>  start logging PSG registers to <filename> 
                             (default: log.psg)
   sccpsg_log stop              stop logging PSG registers

Examples:
   sccpsg_log start             start logging registers to default file log.psg
   sccpsg_log start myfile.psg  start logging to file myfile.psg
   sccpsg_log stop              stop logging PSG registers
}

set_tabcompletion_proc sccpsg_log tab_sccpsg_log
proc tab_sccpsg_log { args } {
	if {[llength $args] == 2} {
		return "start stop"
	}
}

set __sccpsg_log_file -1

set array psg{}
set array psgold{}
set array scc{}
set array sccold{}

proc sccpsg_log { subcommand {filename "data.mus"} } {
	global __sccpsg_log_file
	global array psg
	global array psgold	
	global array scc
	global array sccold

	
	if [string equal $subcommand "start"] {
		set __sccpsg_log_file [open $filename {WRONLY TRUNC CREAT}]
		fconfigure $__sccpsg_log_file -translation binary
		
		# Init registers
		
		puts -nonewline $__sccpsg_log_file [binary format c 0xF0]
		for {set i 0} {$i < 14} {incr i} {
				set psg($i)		[debug read "PSG regs" $i]
				set psgold($i)	[debug read "PSG regs" $i]
				puts -nonewline $__sccpsg_log_file [binary format c2 "$i $psg($i)"]	
		}


		puts -nonewline $__sccpsg_log_file [binary format c 0xF1]

		for {set i 0} {$i < 16} {incr i} {
	
			set reg [expr $i + 0x80]
			set value [debug read "SCC SCC" [expr $i + 0xA0]]
			set scc($reg) $value
			set sccold($reg) $value
			puts -nonewline $__sccpsg_log_file [binary format c2 "$reg $value"]
		}
		



		puts -nonewline $__sccpsg_log_file [binary format c 0xF2]
		for {set i 0} {$i < 128} {incr i} {
				set scc($i)		[debug read "SCC SCC" $i]
				set sccold($i)	[debug read "SCC SCC" $i]
				puts -nonewline $__sccpsg_log_file [binary format c2 "$i $scc($i)"]	
		}

		
		
		__do_sccpsg_log
		return ""
	} elseif [string equal $subcommand "stop"] {
		close $__sccpsg_log_file
		set __sccpsg_log_file -1
		return ""
	} else {
		error "bad option \"$subcommand\": must be start, stop"
	}
}

proc __do_sccpsg_log {} {
	global __sccpsg_log_file
	global array psg
	global array psgold	
	global array scc
	global array sccold


	
	if {$__sccpsg_log_file == -1} return
	
	
	# Psg Regs
	
	set putPSG	0
	set putSCC	0
	
	for {set i 0} {$i < 14} {incr i} {
		set value [debug read "PSG regs" $i]
		set psg($i) $value
		if {$psg($i) != $psgold($i)} {
				
				if {$putPSG == 0} {
						puts -nonewline $__sccpsg_log_file [binary format c 0xF0]
						set putPSG 1
				}
		
				puts -nonewline $__sccpsg_log_file [binary format c2 "$i $value"]
				set psgold($i) $value
		}
				
	}
	
	# SCC Waves
	

	for {set i 0} {$i < 128} {incr i} {
		set value [debug read "SCC SCC" $i]
		set scc($i) $value
		if {$scc($i) != $sccold($i)} {
				
				if {$putSCC == 0} {
						puts -nonewline $__sccpsg_log_file [binary format c 0xF2]
						set putSCC 1
				}
		
				puts -nonewline $__sccpsg_log_file [binary format c2 "$i $value"]
				set sccold($i) $value
		}
				
	}


	# SCC Regs
	
	set putSCC 0

	for {set i 0} {$i < 16} {incr i} {
	
		set reg [expr $i + 0x80]
		set value [debug read "SCC SCC" [expr $i + 0xA0]]
		
		
		set scc($reg) $value
		if {$scc($reg) != $sccold($reg)} {
				
				if {$putSCC == 0} {
						puts -nonewline $__sccpsg_log_file [binary format c 0xF1]
						set putSCC 1
				}
		
				puts -nonewline $__sccpsg_log_file [binary format c2 "$reg $value"]
				set sccold($reg) $value
		}
				
	}



	# End of frame
		
	puts -nonewline $__sccpsg_log_file [binary format c 0xFF]
	
	
	
	
	after frame __do_sccpsg_log
}


