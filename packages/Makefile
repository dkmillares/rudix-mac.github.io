all:
	@for x in *.json ; do \
		echo $$x ; \
		./create_page_from_json.py package.html.in $$x -o $${x%.json}.html ; \
	done

index.html: index.html.in
	./create_index.py > $@

%.html: %.json
	./create_page_from_json.py package.html.in $< -o $@

clean:
	rm -f *~
