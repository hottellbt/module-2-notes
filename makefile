.PHONY: module_2
module_2:
	@python3 gluedoc.py -c | pandoc --metadata-file meta.yml --toc --read markdown -o module_2.pdf