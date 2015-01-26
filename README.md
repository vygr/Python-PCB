Python-PCB
==========

Python PCB router and viewer.

There are two viewer apps, view.py requires aggDraw module to be installed, view_mpl.py
requires matplotlib module to be installed. The matplotlib viwer is much more heavyweight
than the former.

Example command line would be:

pypy pcb.py --v 1 netlist.pcb | python view.py

You can drop the output to a file and view it as an animation with:

pypy pcb.py --v 1 netlist.pcb > anim
python view.py anim

-h or --help for help on either app.

Format of .pcb input file or stdin is:

[width, height, depth]
[track_radius, via_radius, gap_width, [(terminal_radius, terminal_gap, (x, y, z), [(x, y), ...]), ...]...]

You can stop a netlist early by just putting:

[]

For example:

[width, height, depth]
[track_radius, via_radius, track_gap, [(terminal_radius, terminal_gap, (x, y, z), [(x, y), ...]), ...]...]
[track_radius, via_radius, track_gap, [(terminal_radius, terminal_gap, (x, y, z), [(x, y), ...]), ...]...]
[]
[track_radius, via_radius, track_gap, [(terminal_radius, terminal_gap, (x, y, z), [(x, y), ...]), ...]...]
[track_radius, via_radius, track_gap, [(terminal_radius, terminal_gap, (x, y, z), [(x, y), ...]), ...]...]

Format of the view.py input is similar but has the track paths appended:

[width, height, depth]
[track_radius, via_radius, track_gap, [(terminal_radius, terminal_gap, (x, y, z), [(x, y), ...]), ...]...], [(x, y, z), ...]]
