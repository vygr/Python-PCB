Python-PCB
==========

Python PCB router and viewer

The viewer requires aggDraw module to be installed.

Example command line would be:

pypy pcb.py netlist.ncb --v 1 | python view.py

You can drop the output to a file and view it as an animation with:

pypy pcb.py netlist.ncb --v 1 > anim
python view.py anim

-h or --help for help on either app.
