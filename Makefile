test:
	@echo Testing Notre Dame path finder...
	@chmod +x ./tests/test_pathfinder.py
	python -m unittest discover -s tests -v
	@echo

demo:
	@echo Demoing Notre Dame path finder...
	@chmod +x ./src/pathfinder.py
	@echo Generating shortest path between Alumni Hall and Hesburgh Library...
	./src/pathfinder.py -d data/nd_paths.geojson -o out/alumni_to_hes.png -m data/nd_pois.dat -s "Alumni Hall" -e "Hesburgh Library" 
	@echo Check out/alumni_to_hes.png for a map of the shortest path between Alumni Hall and Hesburgh Library
	@echo
