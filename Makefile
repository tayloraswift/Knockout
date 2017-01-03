# This Makefile assumes that you have swiftenv installed
# To get going, start with `make init`

SWIFT_VERSION = DEVELOPMENT-SNAPSHOT-2016-12-15-a

# OS specific differences
UNAME = ${shell uname}
ifeq ($(UNAME), Darwin)
SWIFTC_FLAGS =
LINKER_FLAGS =
endif
ifeq ($(UNAME), Linux)
SWIFTC_FLAGS = -Xcc -I/usr/local/include
LINKER_FLAGS = -Xlinker -L/usr/local/lib
PATH_TO_SWIFT = /home/Sandbox/Swift/swift-$(SWIFT_VERSION)-ubuntu16.10/usr/bin
endif


build:
	swift build $(SWIFTC_FLAGS) $(LINKER_FLAGS)

test: build
	swift test $(SWIFTC_FLAGS) $(LINKER_FLAGS)

clean:
	swift build --clean

distclean:
	rm -rf Packages
	swift build --clean

.PHONY: build test distclean init
