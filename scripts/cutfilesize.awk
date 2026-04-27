#!/usr/bin/awk -f

# ------------------------
# CUTFILESIZE.AWK
# Cutfile in 8k files with Pletter
# count of files header
# Use: cutter and tar8k
# ------------------------

BEGIN {

	print "Cutting file -> " ARGV[1]
	


	system ("cuttersize "ARGV[1]" "ARGV[2]" "ARGV[3]);
	
	idx = index(ARGV[1],".");
	print idx;
	tmp_string = substr(ARGV[1],1,idx-1);

	print "Packing...";


	
	namefile = "rename0.tmp";
	system ("rm -Rf " namefile);
	system ("find "tmp_string".0?? > " namefile );	
	if ((getline < namefile) > 0) {
		do {

		system ("pletter "$0);

		}
		while (getline < namefile);	
		
	}


	

	print "Tar 8k...";

	system ("tar8k "tmp_string" *.plet5");

	print "Delete TMP Files...";

	system ("rm -Rf "tmp_string".0??");
	system ("rm -Rf *.plet5");
	system ("rm -Rf rename0.tmp");

	print "All done!!";



}
