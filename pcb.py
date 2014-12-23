#!/opt/local/bin/pypy -tt
# -*- coding: utf-8 -*-
#Copyright (C) 2014 Chris Hinsley All Rights Reserved

import sys, argparse, router
from copy import deepcopy
from ast import literal_eval
from mymath import *

def main():
	parser = argparse.ArgumentParser(description = 'Pcb layout optimizer.',  formatter_class = argparse.RawTextHelpFormatter)
	parser.add_argument('infile', nargs = '?', type = argparse.FileType('r'), default = sys.stdin, help = 'filename, default stdin')
	parser.add_argument('--t', nargs = 1, type = int, default = [600], help = 'timeout in seconds, default 600')
	parser.add_argument('--v', nargs = 1, type = int, default = [0], choices = range(0, 2), help = 'verbosity level 0..1, default 0')
	parser.add_argument('--s', nargs = 1, type = int, default = [1], help = 'number of samples, default 1')
	parser.add_argument('--g', nargs = 1, type = float, default = [0.1], help = 'track gap, default 0.1')
	parser.add_argument('--r', nargs = 1, type = int, default = [1], choices = range(1, 5), help = 'grid resolution 1..4, default 1')
	parser.add_argument('--d', nargs = 1, type = int, default = [0], choices = range(0, 6), \
			help = 'distance metric 0..5, default 0.\n' \
					 '0 -> manhattan\n1 -> squared_euclidean\n2 -> euclidean\n3 -> chebyshev\n4 -> reciprocal\n5 -> random')
	parser.add_argument('--fr', nargs = 1, type = int, default = [2], choices = range(1, 6), help = 'flood range 1..5, default 2')
	parser.add_argument('--xr', nargs = 1, type = int, default = [1], choices = range(0, 6), help = 'even layer x range 0..5, default 1')
	parser.add_argument('--yr', nargs = 1, type = int, default = [1], choices = range(0, 6), help = 'odd layer y range 0..5, default 1')
	args = parser.parse_args()

	flood_range = args.fr[0]
	flood_range_x_even_layer = args.xr[0]
	flood_range_y_odd_layer = args.yr[0]
	path_range = flood_range + 0
	path_range_x_even_layer = flood_range_x_even_layer + 0
	path_range_y_odd_layer = flood_range_y_odd_layer + 0

	routing_flood_vectors = [[(x, y, 0) for x in xrange(-flood_range_x_even_layer, flood_range_x_even_layer + 1) for y in xrange(-flood_range, flood_range + 1) \
		 						if length_2d((x, y)) > 0.1 and length_2d((x, y)) <= flood_range] + [(0, 0, -1), (0, 0, 1)], \
							[(x, y, 0) for x in xrange(-flood_range, flood_range + 1) for y in xrange(-flood_range_y_odd_layer, flood_range_y_odd_layer + 1) \
								 if length_2d((x, y)) > 0.1 and length_2d((x, y)) <= flood_range] + [(0, 0, -1), (0, 0, 1)]]

	routing_path_vectors = [[(x, y, 0) for x in xrange(-path_range_x_even_layer, path_range_x_even_layer + 1) for y in xrange(-path_range, path_range + 1) \
		 						if length_2d((x, y)) > 0.1 and length_2d((x, y)) <= path_range] + [(0, 0, -1), (0, 0, 1)], \
							[(x, y, 0) for x in xrange(-path_range, path_range + 1) for y in xrange(-path_range_y_odd_layer, path_range_y_odd_layer + 1) \
								 if length_2d((x, y)) > 0.1 and length_2d((x, y)) <= path_range] + [(0, 0, -1), (0, 0, 1)]]

	dfunc = [manhattan_distance, squared_euclidean_distance, euclidean_distance, \
				chebyshev_distance, reciprical_distance, random_distance][args.d[0]]

	dimensions = literal_eval(args.infile.readline().strip())
	pcb = router.Pcb(dimensions, routing_flood_vectors, routing_path_vectors, dfunc, args.r[0], args.v[0], args.g[0])
	for line in args.infile:
		track = literal_eval(line.strip())
		if not track:
			break
		pcb.pcb_add_track(track)
	args.infile.close()

	pcb.pcb_print()
	best_cost = None
	best_pcb = None
	for i in xrange(args.s[0]):
		if not pcb.pcb_route(args.t[0]):
			pcb.pcb_shuffle_netlist()
			continue
		cost = pcb.pcb_cost()
		if best_cost == None or cost < best_cost:
			best_cost = cost
			best_pcb = deepcopy(pcb)
		pcb.pcb_shuffle_netlist()
	if best_pcb != None:
		best_pcb.pcb_print_netlist()
	else:
		print []

if __name__ == '__main__':
	main()
