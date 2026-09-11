.PHONY: all clean

ifneq ($(WINDIR),)
dsk2rom_e = dsk2rom.exe
bin2h_e   = bin2h.exe
else
dsk2rom_e = dsk2rom
bin2h_e   = bin2h
endif

CXX ?= g++
CXXFLAGS ?= -O2 -Wall -fomit-frame-pointer

all: $(bin2h_e) dsk2rom.h $(dsk2rom_e)

$(bin2h_e): bin2h.c
	$(CXX) $(CXXFLAGS) -x c++ $^ -o $@

pletter/pletter.o: pletter/pletter.cpp
	$(CXX) $(CXXFLAGS) -c $< -o $@

pletter/unpletter.o: pletter/unpletter.c
	$(CXX) $(CXXFLAGS) -x c++ -c $< -o $@

dsk2rom.h: $(bin2h_e) dsk2rom.rom
	./$(bin2h_e) dsk2rom dsk2rom.rom dsk2rom.h

dsk2rom.o: dsk2rom.c dsk2rom.h
	$(CXX) $(CXXFLAGS) -x c++ -c $< -o $@

$(dsk2rom_e): dsk2rom.o pletter/pletter.o pletter/unpletter.o
	$(CXX) $(CXXFLAGS) $^ -o $@

clean:
	rm -f $(dsk2rom_e) $(bin2h_e) dsk2rom.h dsk2rom.o pletter/*.o
