all: \
	prodmgr.8 \

%.8: %.8.rst
	rst2man $< $@

clean:
	rm -f *.8

.PHONY: all clean
