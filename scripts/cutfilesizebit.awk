#!/usr/bin/awk -f


# ------------------------
# CUTFILESIZEBIT.AWK
# Cutfile in 8k files with BitBuster
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
    namefiles="";
    namefilesnocomp="";
	system ("rm -Rf " namefile);
	system ("find "tmp_string".0?? > " namefile );	
	if ((getline < namefile) > 0) {
		do {

		system ("pack "$0);
        namefiles=namefiles" "$0".pck";
        namefilesnocomp=namefilesnocomp" "$0;
		}
		while (getline < namefile);	
		
	}


	print "Tar 8k...";

	system ("tar8k "tmp_string" "namefiles);

	print "Delete TMP Files...";

	system ("rm -Rf "namefilesnocomp);
	system ("rm -Rf "namefiles);
    system ("rm -Rf rename0.tmp");

	print "All done!!";



}

