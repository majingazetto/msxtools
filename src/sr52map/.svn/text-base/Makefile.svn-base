SHELL=/bin/bash

BINDST = ../bin
TARGETS = sr52map

all: $(TARGETS) tobin


clean:
	rm -f *.d
	rm -f $(TARGETS)

$(TARGETS):
	gcc $@.c -o $@
	@echo "$@: $@.c" > $@.d

tobin:
	@if [ -d $(BINDST) ] ;\
	then \
		cp $(TARGETS) $(BINDST) ;\
	fi


-include *.d	


