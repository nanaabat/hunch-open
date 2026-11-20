# hunch

the feeling + thinking machine. sense. understand. anticipate.

hunch predicts how a space tends to feel from its geometry, materials, light and climate.

## what is here

packages/hunch-interface  the provider protocol hosts use to ask hunch for a goal, a guard against claims about reading people's emotions, a deterministic mock, and a mock worker with the same command line as a full service
blender/hunch  the blender panel and the scene snapshot code. these are the public host-side files. they do not include the engine. the full in-tool experience, including the feel loop, ships with tingle.

the mock is labelled as a mock. you can wire a host and run a pass without the engine.

## what is not here

the hunch engine, trained weights, training code and data, feature extraction and scoring internals, and run data.

## try it

```
python -m venv .venv
.venv/bin/pip install pytest
.venv/bin/pip install -e packages/hunch-interface
.venv/bin/python -m pytest
.venv/bin/python -m hunch_adapter.worker --input snap.json --output result.json
```

wink uses this same interface (see the wink repo). tingle embeds the blender panel.

## status

experimental and early. expect rough edges and changes, and check every result yourself. no trained weights ship with this repo, so the mock is what runs out of the box. the interface, mock and snapshot code are usable. a trained engine is not part of this repo.

## family

hunch is one of three. tinker is the learning + doing machine. wink brings them together. tingle puts all three in one panel inside the 3D tools you already use.

## licence

mit, copyright aprewaturkson inc. see LICENSE.
