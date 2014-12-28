# -*- coding: utf-8 -*-
#Copyright (C) 2014 Chris Hinsley All Rights Reserved

import math, random, itertools

#generic distance metric stuff

def manhattan_distance(p1, p2):
	return sum(abs(x - y) for x, y in itertools.izip(p1, p2))

def euclidean_distance(p1, p2):
	return math.sqrt(sum((x - y) ** 2 for x, y in itertools.izip(p1, p2)))

def squared_euclidean_distance(p1, p2):
	return sum((x - y) ** 2 for x, y in itertools.izip(p1, p2))

def chebyshev_distance(p1, p2):
	return max(abs(x - y) for x, y in itertools.izip(p1, p2))

def reciprical_distance(p1, p2):
	d = manhattan_distance(p1, p2)
	return 1.0 / d if d != 0 else 1.0

def random_distance(p1, p2):
	return random.random()

#generic vector stuff

def sign(x):
	if x == 0:
		return 0
	if x < 0:
		return -1
	return 1

def equal(p1, p2):
	return manhattan_distance(p1, p2) == 0.0

def add(p1, p2):
	return tuple(x + y for x, y in itertools.izip(p1, p2))

def sub(p1, p2):
	return tuple(x - y for x, y in itertools.izip(p1, p2))

def scale(p, s):
	return tuple(x * s for x in p)

def dot(p1, p2):
	return sum(x * y for x, y in itertools.izip(p1, p2))

def length(p):
	return math.sqrt(dot(p, p))

def distance(p1, p2):
	return length(sub(p2, p1))

def distance_squared(p1, p2):
	p = sub(p2, p1)
	return dot(p, p)

def norm(p):
	l = length(p)
	if l == 0:
		return scale(p, 0)
	l = 1.0 / l
	return scale(p, l)

def distance_to_line(p, p1, p2):
	lv = sub(p2, p1)
	pv = sub(p, p1)
	c1 = dot(pv, lv)
	if c1 <= 0:
		return distance(p, p1)
	c2 = dot(lv, lv)
	if c2 <= c1:
		return distance(p, p2)
	return distance(p, add(p1, scale(lv, c1 / float(c2))))

def distance_squared_to_line(p, p1, p2):
	lv = sub(p2, p1)
	pv = sub(p, p1)
	c1 = dot(pv, lv)
	if c1 <= 0:
		return distance_squared(p, p1)
	c2 = dot(lv, lv)
	if c2 <= c1:
		return distance_squared(p, p2)
	return distance_squared(p, add(p1, scale(lv, c1 / float(c2))))

#specific vector stuff

def add_2d(p1, p2):
	x1, y1 = p1
	x2, y2 = p2
	return x1 + x2, y1 + y2

def add_3d(p1, p2):
	x1, y1, z1 = p1
	x2, y2, z2 = p2
	return x1 + x2, y1 + y2, z1 + z2

def sub_2d(p1, p2):
	x1, y1 = p1
	x2, y2 = p2
	return x1 - x2, y1 - y2

def sub_3d(p1, p2):
	x1, y1, z1 = p1
	x2, y2, z2 = p2
	return x1 - x2, y1 - y2, z1 - z2

def scale_2d(p, s):
	x, y = p
	return x * s, y * s

def scale_3d(p, s):
	x, y, z = p
	return x * s, y * s, z * s

def perp_2d(p):
	x, y = p
	return y, -x

def cross_3d(p1, p2):
	x1, y1, z1 = p1
	x2, y2, z2 = p2
	return (y1 * z2 - z1 * y2, z1 * x2 - x1 * z2, x1 * y2 - y1 * x2)

def dot_2d(p1, p2):
	x1, y1 = p1
	x2, y2 = p2
	return x1 * x2 + y1 * y2

def dot_3d(p1, p2):
	x1, y1, z1 = p1
	x2, y2, z2 = p2
	return x1 * x2 + y1 * y2 + z1 * z2

def length_2d(p):
	return math.sqrt(dot_2d(p, p))

def length_3d(p):
	return math.sqrt(dot_3d(p, p))

def norm_2d(p):
	l = length_2d(p)
	if l == 0:
		return (0, 0)
	x, y = p
	return (x / l, y / l)

def norm_3d(p):
	l = length_3d(p)
	if l == 0:
		return (0, 0, 0)
	x, y, z = p
	return (x / l, y / l, z / l)

def distance_2d(p1, p2):
	return length_2d(sub_2d(p2 - p1))

def distance_3d(p1, p2):
	return length_3d(sub_3d(p2 - p1))

def distance_squared_2d(p1, p2):
	x1, y1 = p1
	x2, y2 = p2
	p = x2 - x1, y2 - y1
	return dot_2d(p, p)

def distance_squared_3d(p1, p2):
	x1, y1, z1 = p1
	x2, y2, z2 = p2
	p = x2 - x1, y2 - y1, z2 - z1
	return dot_3d(p, p)

def distance_to_line_2d(p, p1, p2):
	lv = sub_2d(p2, p1)
	pv = sub_2d(p, p1)
	c1 = dot_2d(pv, lv)
	if c1 <= 0:
		return distance_2d(p, p1)
	c2 = dot_2d(lv, lv)
	if c2 <= c1:
		return distance_2d(p, p2)
	return distance_2d(p, add_2d(p1, scale_2d(lv, c1 / float(c2))))

def distance_to_line_3d(p, p1, p2):
	lv = sub_3d(p2, p1)
	pv = sub_3d(p, p1)
	c1 = dot_3d(pv, lv)
	if c1 <= 0:
		return distance_3d(p, p1)
	c2 = dot_3d(lv, lv)
	if c2 <= c1:
		return distance_3d(p, p2)
	return distance_3d(p, add_3d(p1, scale_3d(lv, c1 / float(c2))))

def distance_squared_to_line_2d(p, p1, p2):
	lv = sub_2d(p2, p1)
	pv = sub_2d(p, p1)
	c1 = dot_2d(pv, lv)
	if c1 <= 0:
		return distance_squared_2d(p, p1)
	c2 = dot_2d(lv, lv)
	if c2 <= c1:
		return distance_squared_2d(p, p2)
	return distance_squared_2d(p, add_2d(p1, scale_2d(lv, c1 / float(c2))))

def distance_squared_to_line_3d(p, p1, p2):
	lv = sub_3d(p2, p1)
	pv = sub_3d(p, p1)
	c1 = dot_3d(pv, lv)
	if c1 <= 0:
		return distance_squared_3d(p, p1)
	c2 = dot_3d(lv, lv)
	if c2 <= c1:
		return distance_squared_3d(p, p2)
	return distance_squared_3d(p, add_3d(p1, scale_3d(lv, c1 / float(c2))))

def collide_lines_2d(l1_p1, l1_p2, l2_p1, l2_p2):
	l1_x1, l1_y1 = l1_p1
	l1_x2, l1_y2 = l1_p2
	l2_x1, l2_y1 = l2_p1
	l2_x2, l2_y2 = l2_p2
	ax = l1_x2 - l1_x1
	ay = l1_y2 - l1_y1
	bx = l2_x1 - l2_x2
	by = l2_y1 - l2_y2
	cx = l1_x1 - l2_x1
	cy = l1_y1 - l2_y1
	an = by * cx - bx * cy
	ad = ay * bx - ax * by
	bn = ax * cy - ay * cx
	bd = ay * bx - ax * by
	if (ad == 0 or bd == 0):
		return False
	else:
		if (ad > 0):
			if (an < 0 or an > ad):
				return False
		else:
			if (an > 0 or an < ad):
				return False;
		if (bd > 0):
			if (bn < 0 or bn > bd):
				return False
		else:
			if (bn > 0 or bn < bd):
				return False
	return True

def collide_thick_lines_2d(tl1_p1, tl1_p2, tl2_p1, tl2_p2, tl1_r, tl2_r):
	if collide_lines_2d(tl1_p1, tl1_p2, tl2_p1, tl2_p2):
		return True
	radius_squared = (tl1_r + tl2_r) ** 2
	if distance_squared_to_line_2d(tl2_p1, tl1_p1, tl1_p2) <= radius_squared:
		return True
	if distance_squared_to_line_2d(tl2_p2, tl1_p1, tl1_p2) <= radius_squared:
		return True
	if distance_squared_to_line_2d(tl1_p1, tl2_p1, tl2_p2) <= radius_squared:
		return True
	if distance_squared_to_line_2d(tl1_p2, tl2_p1, tl2_p2) <= radius_squared:
		return True
	return False

#generic path stuff

def thicken_path_2d(points, radius, capstyle, joinstyle):
	if radius == 0:
		return points[:] + points[::-1]
	index = 0
	step = 1
	out_points = []
	resolution = int(math.pi * radius) + 1
	while True:
		p1 = points[index]; index += step
		p2 = points[index]; index += step
		l2_v = sub_2d(p2, p1)
		l2_pv = perp_2d(l2_v)
		l2_npv = norm_2d(l2_pv)
		rv = scale_2d(l2_npv, radius)
		if capstyle == 0:
			#butt cap
			out_points.append(sub_2d(p1, rv))
			out_points.append(add_2d(p1, rv))
		elif capstyle == 1:
			#square cap
			p0 = add_2d(p1, perp_2d(rv))
			out_points.append(sub_2d(p0, rv))
			out_points.append(add_2d(p0, rv))
		elif capstyle == 2:
			#triangle cap
			out_points.append(sub_2d(p1, rv))
			out_points.append(add_2d(p1, perp_2d(rv)))
			out_points.append(add_2d(p1, rv))
		elif capstyle == 3:
			#round cap
			rvx, rvy = rv
			for i in xrange(resolution + 1):
				angle = (i * math.pi) / resolution
				s = math.sin(angle)
				c = math.cos(angle)
				rv = rvx * c - rvy * s, rvx * s + rvy * c
				out_points.append(sub_2d(p1, rv))
		while index != -1 and index != len(points):
			p1, l1_v, l1_npv = p2, l2_v, l2_npv
			p2 = points[index]; index += step
			l2_v = sub_2d(p2, p1)
			l2_pv = perp_2d(l2_v)
			l2_npv = norm_2d(l2_pv)
			nbv = norm_2d(scale_2d(add_2d(l1_npv, l2_npv), 0.5))
			c = dot_2d(nbv, norm_2d(l1_v))
			if c <= 0 or joinstyle == 0:
				#mitre join
				s = math.sin(math.acos(c))
				bv = scale_2d(nbv, radius / s)
				out_points.append(add_2d(p1, bv))
			elif joinstyle == 1:
				#bevel join
				out_points.append(add_2d(p1, scale_2d(l1_npv, radius)))
				out_points.append(add_2d(p1, scale_2d(l2_npv, radius)))
			elif joinstyle == 2:
				#round join
				rvx, rvy = scale_2d(l1_npv, radius)
				theta = math.acos(dot_2d(l1_npv, l2_npv))
				segs = int((theta / math.pi) * resolution) + 1
				for i in xrange(segs + 1):
					angle = (i * theta) / segs
					s = math.sin(angle)
					c = math.cos(angle)
					rv = rvx * c - rvy * s, rvx * s + rvy * c
					out_points.append(add_2d(p1, rv))
		if step < 0:
			break
		step = -step; index += step
	return out_points
