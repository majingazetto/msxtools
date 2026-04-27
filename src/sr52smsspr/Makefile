
############################
# SR52SMSSPRSPR Spr Conversor #
############################


WINPLATFORM = OFF
EXT =
CXXFLAGS	= -Wall -O2


# Check CYGWIN or MINGW (change to EXE)

ISMINGW 	:= $(shell uname | grep MINGW)
ISCYGWIN 	:= $(shell uname | grep CYGWIN)

ifneq ($(ISMINGW),)
	CXXFLAGS += -DISMINGW
	EXT	= .exe
endif

ifneq ($(ISCYGWIN),)
	EXT	= .exe
	CXXFLAGS += -DISCYGWIN
endif

SR52SMSSPR	= sr52smsspr
SRC_DIR	= src
OBJ_DIR	= obj

SRC_FILES	:= $(shell find $(SRC_DIR) -type f -name "*.cpp")
OBJS		:= $(subst $(SRC_DIR),$(OBJ_DIR),$(SRC_FILES:.cpp=.o))
DEPDIR		= dep



EXE			= $(SR52SMSSPR)$(EXT)
SETUP_DIRS 	= $(DEPDIR) $(OBJ_DIR)
CXXFLAGS	+= -I$(SRC_DIR)

all: $(EXE)

clean:
	$(RM) *.o
	$(RM) $(EXE)
	$(RM) -r $(SETUP_DIRS)


-include $(DEPDIR)/*.d

$(SETUP_DIRS):
	@echo "Creating directory: $@"
	@mkdir $@


$(OBJS):
	@echo "Compiling $(SRC_DIR)/$(notdir $(basename $@)).cpp -> $@"
	$(CXX) $(CXXFLAGS) -MD -c $(SRC_DIR)/$(notdir $(basename $@)).cpp -o $@
	@mv $(basename $@).d $(DEPDIR)

$(EXE): $(SETUP_DIRS) $(OBJS)
	@echo
	@echo "Linking -> $@"
	$(CXX) $(CXXFLAGS) $(OBJS) -o $@ 
	
echoes:
	@echo $(OBJS)

