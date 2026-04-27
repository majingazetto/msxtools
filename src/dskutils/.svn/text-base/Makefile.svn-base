
#######################
# Disk Utils Makefile #
#######################


BINDST = ../bin
WRDSK = wrdsk
RDDSK = rddsk

all: $(WRDSK) $(RDDSK) tobin



clean:
	@if [ -f $(WRDSK) ] ;\
	then \
		rm $(WRDSK) ;\
	fi
	
	@if [ -f $(RDDSK) ] ;\
	then \
		rm $(RDDSK) ;\
	fi
	
	@if [ -f $(WRDSK).d ] ;\
	then \
		rm $(WRDSK).d ;\
	fi
	
	@if [ -f $(RDDSK).d ] ;\
	then \
		rm $(RDDSK).d ;\
	fi
	
	@if [ -f $(BINDST)/$(RDDSK) ] ;\
	then \
		rm $(BINDST)/$(RDDSK);\
	fi
	
	@if [ -f $(BINDST)/$(WRDSK) ] ;\
	then \
		rm $(BINDST)/$(WRDSK);\
	fi

$(WRDSK):
	@gcc DiskUtil.c wrdsk.c -o $@
	@echo -n "$@: " > $@.d
	@echo "Boot.h DiskUtil.h DiskUtil.c wrdsk.c" >> $@.d


$(RDDSK):
	@gcc DiskUtil.c rddsk.c -o $@
	@echo -n "$@: " > $@.d
	@echo "Boot.h DiskUtil.h DiskUtil.c rddsk.c" >> $@.d

tobin:
	@if [ -d $(BINDST) ] ;\
	then \
		cp $(RDDSK) $(WRDSK) $(BINDST) ;\
	fi

-include *.d



