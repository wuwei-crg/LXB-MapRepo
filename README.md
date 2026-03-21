# LXB-MapRepo

Map data repository for LXB route-then-act runtime.

## Layout

- `stable/index.json`: stable lane index (default for clients)
- `candidates/index.json`: candidate lane index (testing lane)
- `stable/maps/<package>/<map_id>/`: stable map artifacts
- `candidates/maps/<package>/<map_id>/`: candidate map artifacts

Each map artifact folder contains:

- `nav_map.json.gz`
- `meta.json`

## Notes

- Stable maps are promoted manually after validation.
- Candidate maps are for testing and debugging.
