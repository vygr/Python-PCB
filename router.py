# -*- coding: utf-8 -*-
#Copyright (C) 2014 Chris Hinsley All Rights Reserved

import sys, time
from array import array
from itertools import islice, izip, groupby
from random import shuffle
from mymath import *
from layer import *

def shift(l, n):
	n = n % len(l)
	head = l[:n]
	del l[:n]
	l.extend(head)
	return l

def optimise_paths(paths):
	opt_paths = []
	for path in paths:
		opt_path = []
		d = (0, 0, 0)
		for a, b in izip(path, islice(path, 1, None)):
			d1 = norm_3d(sub_3d(b, a))
			if d1 != d:
				opt_path.append(a)
				d = d1
		opt_path.append(path[-1])
		opt_paths.append(opt_path)
	return opt_paths

class Pcb():
	def __init__(self, dimensions, routing_flood_vectors, routing_path_vectors, dfunc, resolution, verbosity, trackgap):
		self.trackgap = trackgap
		self.dfunc = dfunc
		self.verbosity = verbosity
		self.routing_flood_vectors = routing_flood_vectors
		self.routing_path_vectors = routing_path_vectors
		self.layers = Layers(dimensions, 1.0 / resolution)
		self.width, self.height, self.depth = dimensions
		self.resolution = resolution
		self.width *= resolution
		self.height *= resolution
		self.stride = self.width * self.height
		self.nodes = array('i', [0 for x in xrange(self.stride * self.depth)])
		self.netlist = []

	def set_node(self, node, value):
		self.nodes[(self.stride * node[2]) + (node[1] * self.width) + node[0]] = value

	def get_node(self, node):
		return self.nodes[(self.stride * node[2]) + (node[1] * self.width) + node[0]]

	def all_nodes(self, vectors, node):
		x, y, z = node
		for dx, dy, dz in vectors[z % 2]:
			nx = x + dx; ny = y + dy; nz = z + dz
			if (0 <= nx < self.width) and (0 <= ny < self.height) and (0 <= nz < self.depth):
				yield (nx, ny, nz)

	def all_marked(self, vectors, node):
		for node in self.all_nodes(vectors, node):
			mark = self.get_node(node)
			if mark != 0:
				yield (mark, node)

	def all_not_marked(self, vectors, node):
		for node in self.all_nodes(vectors, node):
			if self.get_node(node) == 0:
				yield node

	def all_nearer_sorted(self, vectors, node, goal, func):
		distance = self.get_node(node)
		nodes = [(func(marked[1], goal), marked[1]) \
					for marked in self.all_marked(vectors, node) \
					if (distance - marked[0]) > 0]
		nodes.sort()
		for node in nodes:
			yield node[1]

	def all_not_shorting(self, gather, params, node, radius):
		for new_node in gather(*params):
			if not self.layers.hit_line(node, new_node, radius):
				yield new_node

	def mark_distances(self, vectors, radius, starts, ends = []):
		distance = 1
		nodes = list(starts)
		for node in nodes:
			self.set_node(node, distance)
		while nodes:
			distance += 1
			new_nodes = []
			for node in nodes:
				for new_node in self.all_not_shorting(self.all_not_marked, (vectors, node), node, radius):
					self.set_node(new_node, distance)
					new_nodes.append(new_node)
			nodes = new_nodes
			if 0 not in [self.get_node(node) for node in ends]:
				break

	def unmark_distances(self):
		self.nodes = array('i', [0 for x in xrange(self.stride * self.depth)])

	def add_track(self, track):
		radius, net = track
		self.netlist.append(Net(net, radius, self))

	def route(self, timeout):
		self.remove_netlist()
		self.unmark_distances()
		now = time.time()
		self.netlist.sort(key = lambda i: i.radius, reverse = True)
		index = 0
		while index < len(self.netlist):
			if self.netlist[index].route():
				index += 1
			else:
				while True:
					self.netlist[index].reset_topology()
					if index == 0:
						self.shuffle_netlist()
						break
					else:
						index -= 1
						self.netlist[index].remove()
						if self.netlist[index].next_topology():
							break
						else:
							self.netlist.insert(0, self.netlist.pop(index + 1))
							while index != 0:
								self.netlist[index].remove()
								self.netlist[index].reset_topology()
								index -= 1
							break
			if time.time() - now > timeout:
				return False
			if self.verbosity >= 1:
				self.print_netlist()
		return True

	def cost(self):
		return sum(len(path) for net in self.netlist for path in net.paths)

	def shuffle_netlist(self):
		for net in self.netlist:
			net.remove()
			net.shuffle_topology()
		shuffle(self.netlist)

	def remove_netlist(self):
		for net in self.netlist:
			net.remove()

	def print_netlist(self):
		for net in self.netlist:
			net.print_net()
		print []
		sys.stdout.flush()

	def print_pcb(self):
		scale = 1.0 / self.resolution
		print [self.width * scale, self.height * scale, self.depth]
		sys.stdout.flush()

class Net():
	def __init__(self, terminals, radius, pcb):
		self.pcb = pcb
		self.terminals = [(r * pcb.resolution, (x * pcb.resolution, y * pcb.resolution, z)) for r, (x, y, z) in terminals]
		self.radius = radius * pcb.resolution
		self.shift = 0
		self.paths = []
		self.remove()

	def next_topology(self):
		self.shift += 1
		shift(self.terminals, 1)
		if self.shift == len(self.terminals):
			self.shift = 0
			return False
		return True

	def reset_topology(self):
		shift(self.terminals, -self.shift)
		self.shift = 0

	def shuffle_topology(self):
		shuffle(self.terminals)

	def add_paths_collision_lines(self):
		for path in self.paths:
			for a, b in izip(path, islice(path, 1, None)):
				self.pcb.layers.add_line(a, b, self.radius)

	def sub_paths_collision_lines(self):
		for path in self.paths:
			for a, b in izip(path, islice(path, 1, None)):
				self.pcb.layers.sub_line(a, b, self.radius)

	def add_terminal_collision_lines(self):
		for node in self.terminals:
			r, (x, y, _) = node
			self.pcb.layers.add_line((x, y, 0), (x, y, self.pcb.depth - 1), r)

	def sub_terminal_collision_lines(self):
		for node in self.terminals:
			r, (x, y, _) = node
			self.pcb.layers.sub_line((x, y, 0), (x, y, self.pcb.depth - 1), r)

	def remove(self):
		self.sub_paths_collision_lines()
		self.sub_terminal_collision_lines()
		self.paths = []
		self.add_terminal_collision_lines()

	def route(self):
		try:
			self.paths = []
			self.sub_terminal_collision_lines()
			radius = self.radius + (self.pcb.trackgap * self.pcb.resolution)
			visited = set()
			for index in xrange(1, len(self.terminals)):
				visited |= set([(self.terminals[index - 1][1][0], self.terminals[index - 1][1][1], z) for z in xrange(self.pcb.depth)])
				ends = [(self.terminals[index][1][0], self.terminals[index][1][1], z) for z in xrange(self.pcb.depth)]
				self.pcb.mark_distances(self.pcb.routing_flood_vectors, radius, visited, ends)
				ends = [(self.pcb.get_node(node), node) for node in ends]
				ends.sort()
				_, end = ends[0]
				path = [end]
				dv = (0, 0, 0)
				while path[-1] not in visited:
					nearer_nodes = self.pcb.all_not_shorting(self.pcb.all_nearer_sorted, \
								(self.pcb.routing_path_vectors, path[-1], end, self.pcb.dfunc), path[-1], radius)
					next_node = next(nearer_nodes)
					if next_node not in visited:
						for node in nearer_nodes:
							if node in visited:
								next_node = node
								break
							if dv == norm_3d(sub_3d(node, path[-1])):
								next_node = node
					dv = norm_3d(sub_3d(next_node, path[-1]))
					path.append(next_node)
				visited |= set(path)
				self.paths.append(path)
				self.pcb.unmark_distances()
			self.paths = optimise_paths(self.paths)
			self.add_paths_collision_lines()
			self.add_terminal_collision_lines()
			return True
		except StopIteration:
			self.pcb.unmark_distances()
			self.remove()
			return False

	def print_net(self):
		scale = 1.0 / self.pcb.resolution
		print [self.radius * scale, \
				[(r * scale, (x * scale, y * scale, z)) for r, (x, y, z) in self.terminals], \
				[[(x * scale, y * scale, z) for x, y, z in path] for path in self.paths]]
