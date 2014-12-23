# -*- coding: utf-8 -*-
#Copyright (C) 2014 Chris Hinsley All Rights Reserved

import math, mymath

class Layer():
	def __init__(self, dimensions, scale):
		self.width, self.height = dimensions
		self.scale = scale
		self.buckets = [[] for x in xrange(self.width * self.height)]
		self.test = 0

	def aabb(self, line):
		x1, y1, x2, y2, r = line
		if x1 > x2:
			x1, x2 = x2, x1
		if y1 > y2:
			y1, y2 = y2, y1
		minx = int(math.floor((x1 - r) * self.scale))
		miny = int(math.floor((y1 - r) * self.scale))
		maxx = int(math.ceil((x2 + r) * self.scale))
		maxy = int(math.ceil((y2 + r) * self.scale))
		if maxx - minx > self.width:
			maxx = minx + self.width
		if maxy - miny > self.height:
			maxy = miny + self.height
		return (minx, miny, maxx, maxy)

	def all_buckets(self, aabb):
		x1, y1, x2, y2 = aabb
		for y in xrange(y1, y2):
			for x in xrange(x1, x2):
				yield self.buckets[y * self.width + x]

	def all_not_empty_buckets(self, aabb):
		x1, y1, x2, y2 = aabb
		for y in xrange(y1, y2):
			for x in xrange(x1, x2):
				bucket = self.buckets[y * self.width + x]
				if bucket:
					yield bucket

	def add_line(self, line):
		new_record = [0, line]
		for bucket in self.all_buckets(self.aabb(line)):
			found = False
			for record in bucket:
				if record[1] == line:
					found = True
					break
			if not found:
				bucket.append(new_record)

	def sub_line(self, line):
		for bucket in self.all_not_empty_buckets(self.aabb(line)):
			for i in xrange(len(bucket) - 1, -1, -1):
				if bucket[i][1] == line:
					del bucket[i]

	def hit_line(self, line):
		self.test += 1
		for bucket in self.all_not_empty_buckets(self.aabb(line)):
			for record in bucket:
				if record[0] != self.test:
					record[0] = self.test
					l1_p1x, l1_p1y, l1_p2x, l1_p2y, l1_r = line
					l2_p1x, l2_p1y, l2_p2x, l2_p2y, l2_r = record[1]
					if mymath.collide_thick_lines_2d((l1_p1x, l1_p1y), (l1_p2x, l1_p2y), (l2_p1x, l2_p1y), (l2_p2x, l2_p2y), l1_r, l2_r):
						return True
		return False

class Layers():
	def __init__(self, dimensions, scale):
		width, height, self.depth = dimensions
		self.layers = [Layer((width, height), scale) for z in xrange(self.depth)]

	def all_layers(self, z1, z2):
		if z1 != z2:
			for z in xrange(self.depth):
				yield self.layers[z]
		else:
			yield self.layers[z1]

	def add_line(self, p1, p2, r):
		x1, y1, z1 = p1
		x2, y2, z2 = p2
		for layer in self.all_layers(z1, z2):
			layer.add_line((x1, y1, x2, y2, r))

	def sub_line(self, p1, p2, r):
		x1, y1, z1 = p1
		x2, y2, z2 = p2
		for layer in self.all_layers(z1, z2):
			layer.sub_line((x1, y1, x2, y2, r))

	def hit_line(self, p1, p2, r):
		x1, y1, z1 = p1
		x2, y2, z2 = p2
		for layer in self.all_layers(z1, z2):
			if layer.hit_line((x1, y1, x2, y2, r)):
				return True
		return False
