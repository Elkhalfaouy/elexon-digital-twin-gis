import json
from pathlib import Path

DEFAULTS = {
    "highway_access_score": 0.5,
    "tent_fit": 0,
    "demand_proxy": 0.5,
    "address": "",
    "region": "",
    "corridor_note": "",
    "notes": "",
}

def main():
    path = Path("gis/sites.geojson")
    if not path.exists():
        print("sites.geojson not found at gis/sites.geojson")
        return

    data = json.loads(path.read_text(encoding="utf-8"))
    feats = data.get("features", [])
    updated = 0
    touched = 0

    for feat in feats:
        props = feat.get("properties") or {}
        changed = False
        for k, v in DEFAULTS.items():
            if k not in props:
                props[k] = v
                changed = True
            elif props[k] is None:
                props[k] = v
                changed = True
        if changed:
            feat["properties"] = props
            updated += 1
        touched += 1

    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Processed features: {touched}, updated with defaults: {updated}")
    print(f"Wrote updated file to: {path}")

if __name__ == "__main__":
    main()
