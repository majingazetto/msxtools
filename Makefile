# MSXTOOLS Custom Makefile

# Tool Categories
PATTOOLS = sr52spr sr52map sr52pat mt82map
CUTTERTOOLS = cutter cuttersize
TARTOOLS = tar8k tarbin tarbinmax
MUSTOOLS = extractwav
DSKTOOLS = dskutils dsktool
MISCTOOLS = bgm2tmf freepage sms2rom ViewSRC

TARGETS = $(PATTOOLS) $(CUTTERTOOLS) $(TARTOOLS) $(MUSTOOLS) $(DSKTOOLS) $(MISCTOOLS)

# Compilation
SHELL = /bin/bash
BINDST = bin
MAKENP = $(MAKE) --no-print-directory

.PHONY: all clean $(TARGETS)

all: $(BINDST) $(TARGETS)

$(BINDST):
	@mkdir -p $@

$(TARGETS):
	@echo "Building $@..."
	@cd src/$@ && $(MAKENP)
	@if [ -f src/$@/$@ ]; then cp src/$@/$@ $(BINDST)/; fi
	@# Handle cases where binary name differs from folder name
	@if [ "$@" == "dskutils" ]; then cp src/dskutils/wrdsk $(BINDST)/; cp src/dskutils/rddsk $(BINDST)/; fi
	@if [ "$@" == "freepage" ]; then cp src/freepage/freepagebytes $(BINDST)/; fi
	@if [ "$@" == "bgm2tmf" ]; then cp src/bgm2tmf/bgm2tmfall $(BINDST)/; fi

clean:
	@for dir in $(TARGETS); do \
		cd src/$$dir && $(MAKENP) clean; \
		cd ../..; \
	done
	rm -rf $(BINDST)
