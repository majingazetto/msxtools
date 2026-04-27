
.PHONY: build

CPP			= cc -E -P -xc -Werror
SOURCE 		= msxpage0.z8a
SOURCEPRE 	= $(basename $(SOURCE)).pre
OUTPUT		= $(basename $(SOURCE)).rom

ASM			= sjasm -s -l 

build:

	$(CPP) $(SOURCE) > $(SOURCEPRE)
	$(ASM) $(SOURCEPRE) $(OUTPUT)

clean:
	$(RM) *.lst *.sym
	$(RM) $(SOURCEPRE) $(OUTPUT)

