#!/usr/bin/env python3
from math import sqrt, radians, sin, cos, sqrt, atan2
from heapq import heappop, heappush

import os
import argparse

import geopandas as gpd
import networkx as nx
import matplotlib.pyplot as plt
import contextily as ctx

def read_pois(filename):
	pois = dict()
	with open(filename) as f:
		for line in f:
			(name, lat, lon) = line.split('\t')
			pois[name] = (float(lat), float(lon))
	
	return pois

def haversine(a, b):
	lat1, lon1 = a
	lat2, lon2 = b
	R = 6371000
	phi1, phi2 = radians(lat1), radians(lat2)
	dphi = radians(lat2 - lat1)
	dlambda = radians(lon2 - lon1)
	a = sin(dphi/2)**2 + cos(phi1)*cos(phi2)*sin(dlambda/2)**2
	return 2 * R * atan2(sqrt(a), sqrt(1-a))

def nearest_node(G, point):
    x, y = point
    best = None
    best_dist = float("inf")
    for node in G.nodes:
        d = (node[0]-x)**2 + (node[1]-y)**2
        if d < best_dist:
            best_dist = d
            best = node
    return best


def djikstra(G, start, end):
	pq = [(0, start)]
	dists = {start: 0}
	prev = {start: None}
	visited = set()

	while pq:
		dist, node = heappop(pq)

		if node in visited: continue
		visited.add(node)

		if node == end: break

		for neighbor, attrs in G[node].items():
			w = attrs["weight"]
			new_dist = dist + w
			if neighbor not in dists or new_dist < dists[neighbor]:
				dists[neighbor] = new_dist
				heappush(pq, (new_dist, neighbor))
				prev[neighbor] = node
	
	if end not in dists:
		return float('inf'), []

	path = []
	cur = end
	while cur is not None:
		path.append(cur)
		cur = prev[cur]

	return dists[end], path

def main():
	# Create argparser
	parser = argparse.ArgumentParser(description="Pathfinder script to process data and find paths.")

	# Arguments
	parser.add_argument('--data', '-d', required=True, help='Path to the input data file')
	parser.add_argument('--output', '-o', required=True, help='Path to the output file')

	parser.add_argument('--mode', '-m', default=None, help="Mode of operation: 'coord' for coordinates, or a path to a POIs file")

	parser.add_argument('--start', '-s', required=True, help='Start node/index')
	parser.add_argument('--end', '-e', required=True, help='End node/index')

	# Parse the arguments
	args = parser.parse_args()

	# Get data
	gdf = gpd.read_file(args.data)
	gdf = gdf[gdf.geometry.type.isin(["LineString", "MultiLineString"])]

	# Instantiate graph
	G = nx.Graph()

	# Populate graph
	for _, row in gdf.iterrows():
		coords = list(row.geometry.coords)
		
		for i in range(len(coords)-1):
			a = tuple(coords[i])
			b = tuple(coords[i+1])
			w = haversine(a, b)
			
			# Add edge and store name as edge attribute
			G.add_edge(a, b, weight=w)
	
	# Mode
	mode	= args.mode

	# Get start and end pts
	start	= args.start
	end     = args.end

	# Acquire coordinates based on mode
	if args.mode == 'coord':
		start_coord = tuple(map(float, start.split(',')))
		end_coord = tuple(map(float, end.split(',')))
	elif os.path.isfile(mode):
		pois = read_pois(mode)
		start_coord = pois[start.replace(' ', '_')]
		end_coord =   pois[end.replace(' ', '_')]
	else:
		raise Exception("Invalid mode. Choose from 'coord' (coordinate entry) and 'man' (named location entry).")

	# Locate nearest node on the path to start and end
	start_node = nearest_node(G, reversed(start_coord))
	end_node = nearest_node(G, reversed(end_coord))

	# Diagnostic output
	print(f"Start: {start_node} End: {end_node}")

	# Run djikstra and output
	length, path = djikstra(G, start_node, end_node)
	print(f"Length: {length}")
	
	# MPL output
	_, ax = plt.subplots(figsize=(10,10), dpi=200)

	# Plot all edges
	for u, v in G.edges:
		xs = [u[0], v[0]]
		ys = [u[1], v[1]]
		ax.plot(xs, ys, color='lightgray', linewidth=0.5)

	# Plot path
	path_x = [node[0] for node in path]
	path_y = [node[1] for node in path]
	ax.plot(path_x, path_y, color='red', linewidth=2, label='Shortest Path')

	ctx.add_basemap(ax, crs="EPSG:4326", source=ctx.providers.OpenStreetMap.Mapnik, zoom=17)

	# Add text
	ax.set_xlabel("Longitude")
	ax.set_ylabel("Latitude")
	ax.set_title(f"Shortest Path from {start} to {end}")
	ax.legend()

	# Save to output file
	plt.savefig(args.output)

if __name__ == "__main__":
    main()
