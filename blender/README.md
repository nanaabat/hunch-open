# blender host files

hunch_scene.py builds a snapshot of the current blender scene (rooms, glazing, a viewpoint) for a hunch provider.

hunch_panel.py is the blender ui for site, room, viewpoint, and a run. it talks to `python -m hunch_adapter.worker`. with this repo that worker is the mock. if you also have tingle installed, the panel is shown inside the tingle add-on, which supplies the feel loop and scene looks.

these files do not include the hunch engine.
