#!/opt/local/bin/python -tt
# -*- coding: utf-8 -*-
#Copyright (C) 2014 Chris Hinsley All Rights Reserved

import os, sys, argparse, select, Tkinter, aggdraw
from ast import literal_eval
from itertools import izip, islice, chain
from PIL import Image, ImageTk
from mymath import *

MARGIN = 2

args = None
photo = None
image = None

def split_paths(paths):
	new_paths = []
	for path in paths:
		new_path = []
		for a, b in izip(path, islice(path, 1, None)):
			_, _, za = a
			_, _, zb = b
			if za != zb:
				if new_path:
					new_path.append(a)
					new_paths.append(new_path)
				new_paths.append([a, b])
				new_path = []
			else:
				new_path.append(a)
		if new_path:
			new_path.append(path[-1])
			new_paths.append(new_path)
	return new_paths

def scale_and_split_tracks(tracks, scale):
	for track in tracks:
		track[0] *= scale
		track[1] *= scale
		track[3] = split_paths(track[3])
		for i in xrange(len(track[2])):
			r, (x, y, z), s = track[2][i]
			track[2][i] = r * scale, ((x + MARGIN) * scale, (y + MARGIN) * scale, z), [(cx * scale, cy * scale) for cx, cy in s]
		for path in track[3]:
			for i in xrange(len(path)):
				x, y, z = path[i]
				path[i] = (x + MARGIN) * scale, (y + MARGIN) * scale, z

def get_tracks():
	tracks = []
	while True:
		line = args.infile.readline()
		if not line:
			tracks = []
			break
		track = literal_eval(line.strip())
		if not track:
			break
		tracks.append(track)
	return tracks

def doframe(dimensions, root, canvas, poll):
	global photo, image

	tracks = get_tracks()
	if poll:
		while poll.poll(1):
			new_tracks = get_tracks()
			if not new_tracks:
				break
			tracks = new_tracks
	if not tracks:
		return

	pcb_width, pcb_height, pcb_depth = dimensions
	scale = args.s[0]
	scale_and_split_tracks(tracks, scale)
	pcb_width += MARGIN * 2; pcb_height += MARGIN * 2
	img_width = int(pcb_width * scale)
	if args.o[0] == 0:
		img_height = int(pcb_height * scale)
	else:
		img_height = int(pcb_height * pcb_depth * scale)

	canvas.delete("all")
	image = Image.new("RGB", (img_width, img_height), "black")
	ctx = aggdraw.Draw(image)
	black_brush = aggdraw.Brush('black', opacity = 255)
	white_brush = aggdraw.Brush('white', opacity = 255)
	red_brush = aggdraw.Brush('red', opacity = 255)

	if args.o[0] == 0:
		colors = ['red', 'green', 'blue', 'yellow', 'fuchsia', 'aqua']
		for depth in xrange(pcb_depth - 1, -1, -1):
			brush = aggdraw.Brush(colors[depth % len(colors)], opacity = 128)
			for track in tracks:
				radius, via, terminals, paths = track
				for path in paths:
					if path[0][2] == path[-1][2] == depth:
						points = list(chain.from_iterable(thicken_path_2d([(x, y) for x, y, _ in path], radius, 3, 2)))
						ctx.polygon(points, brush)
		for track in tracks:
			radius, via, terminals, paths = track
			for path in paths:
				if path[0][2] != path[-1][2]:
					x, y, _ = path[0]
					ctx.ellipse((x - via, y - via, x + via, y + via), white_brush)
			for r, (x, y, _), s in terminals:
				if not s:
					ctx.ellipse((x - r, y - r, x + r, y + r), white_brush)
					ctx.ellipse((x - r * 0.5, y - r * 0.5, x + r * 0.5, y + r * 0.5), black_brush)
				else:
					if r != 0:
						points = list(chain.from_iterable(thicken_path_2d([(cx + x, cy + y) for cx, cy in s], r, 3, 2)))
						ctx.polygon(points, white_brush)
						points = list(chain.from_iterable(thicken_path_2d([(cx + x, cy + y) for cx, cy in s], r * 0.5, 3, 2)))
						ctx.polygon(points, black_brush)
					else:
						points = list(chain.from_iterable([(cx + x, cy + y) for cx, cy in s]))
						ctx.polygon(points, white_brush)
						points = list(chain.from_iterable([(cx * 0.5 + x, cy * 0.5 + y) for cx, cy in s]))
						ctx.polygon(points, black_brush)
	else:
		for depth in xrange(pcb_depth):
			for track in tracks:
				radius, via, terminals, paths = track
				for path in paths:
					if path[0][2] == path[-1][2] == depth:
						points = list(chain.from_iterable(thicken_path_2d([(x, y + depth * pcb_height * scale) for x, y, _ in path], radius, 3, 2)))
						ctx.polygon(points, red_brush)
			for track in tracks:
				radius, via, terminals, paths = track
				for path in paths:
					if path[0][2] != path[-1][2]:
						x, y, _ = path[0]
						y += depth * pcb_height * scale
						ctx.ellipse((x - via, y - via, x + via, y + via), white_brush)
				for r, (x, y, _), s in terminals:
					y += depth * pcb_height * scale
					if not s:
						ctx.ellipse((x - r, y - r, x + r, y + r), white_brush)
						ctx.ellipse((x - r * 0.5, y - r * 0.5, x + r * 0.5, y + r * 0.5), black_brush)
					else:
						if r != 0:
							points = list(chain.from_iterable(thicken_path_2d([(cx + x, cy + y) for cx, cy in s], r, 3, 2)))
							ctx.polygon(points, white_brush)
							points = list(chain.from_iterable(thicken_path_2d([(cx + x, cy + y) for cx, cy in s], r * 0.5, 3, 2)))
							ctx.polygon(points, black_brush)
						else:
							points = list(chain.from_iterable([(cx + x, cy + y) for cx, cy in s]))
							ctx.polygon(points, white_brush)
							points = list(chain.from_iterable([(cx * 0.5 + x, cy * 0.5 + y) for cx, cy in s]))
							ctx.polygon(points, black_brush)
	ctx.flush()
	photo = ImageTk.PhotoImage(image)
	canvas.create_image(0, 0, image = photo, anchor = Tkinter.NW)
	root.update()
	root.after(0, doframe, dimensions, root, canvas, poll)

def about_menu_handler():
	pass

def main():
	global args, image

	parser = argparse.ArgumentParser(description = 'Pcb layout viewer.')
	parser.add_argument('infile', nargs = '?', type = argparse.FileType('r'), default = sys.stdin, help = 'filename, default stdin')
	parser.add_argument('--s', nargs = 1, type = int, default = [9], help = 'scale factor, default 9')
	parser.add_argument('--f', nargs = 1, type = float, default = [100.0], help = 'framerate, default 100.0')
	parser.add_argument('--i', nargs = 1, default = ['pcb.png'], help = 'filename, default pcb.png')
	parser.add_argument('--o', nargs = 1, type = int, default = [0], choices=range(0, 2), help = 'overlay modes 0..1, default 0')
	args = parser.parse_args()

	poll = 0
	if os.name != 'nt':
		if args.infile == sys.stdin:
			poll = select.poll()
			poll.register(args.infile, select.POLLIN)

	dimensions = literal_eval(args.infile.readline().strip())
	pcb_width, pcb_height, pcb_depth = dimensions
	pcb_width += MARGIN * 2; pcb_height += MARGIN * 2
	scale = args.s[0]
	pcb_width = int(pcb_width * scale)
	if args.o[0] == 0:
		pcb_height = int(pcb_height * scale)
	else:
		pcb_height = int(pcb_height * pcb_depth * scale)

	root = Tkinter.Tk()
	root.maxsize(pcb_width, pcb_height)
	root.minsize(pcb_width, pcb_height)
	root.title("PCB Veiwer")
	menu_bar = Tkinter.Menu(root)
	sub_menu = Tkinter.Menu(menu_bar)
	menu_bar.add_cascade(label = 'Help', menu = sub_menu)
	sub_menu.add_command(label = 'About', command = about_menu_handler)
	root['menu'] = menu_bar
	canvas = Tkinter.Canvas(root, width = pcb_width, height = pcb_height)
	canvas['background'] = 'black'
	canvas.pack()

	root.after(0, doframe, dimensions, root, canvas, poll)
	root.mainloop()
	image.save(args.i[0])	

if __name__ == '__main__':
	main()
