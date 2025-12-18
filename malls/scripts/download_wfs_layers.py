import requests
import json
from pathlib import Path

# Load layers from the combined JSON file
data_path = Path(__file__).parent.parent / "sources" / "wfs_layers_combined.json"
with open(data_path, encoding="utf-8") as f:
    layers = json.load(f)

# Output directory for GeoJSON files
out_dir = Path(__file__).parent.parent / "sources" / "wfs_downloads"
out_dir.mkdir(parents=True, exist_ok=True)

def download_layer(layer):
    url = layer["endpoint"]
    typename = layer["name"]
    params = {
        "SERVICE": "WFS",
        "VERSION": "2.0.0",
        "REQUEST": "GetFeature",
        "TYPENAMES": typename,
        "OUTPUTFORMAT": "text/xml; subtype=gml/3.2"
    }
    print(f"Downloading {typename} from {url} ...")
    try:
        r = requests.get(url, params=params, timeout=120)
        r.raise_for_status()
        out_path = out_dir / f"{typename.replace(':', '_')}.gml"
        with open(out_path, "w", encoding="utf-8") as f:
            f.write(r.text)
        print(f"Saved to {out_path}")
    except Exception as e:
        print(f"Failed to download {typename} with OUTPUTFORMAT: {e}")
        if 'r' in locals():
            print(f"Server response (first 500 chars):\n{r.text[:500]}")
        # Try again without OUTPUTFORMAT
        print(f"Retrying {typename} without OUTPUTFORMAT...")
        params2 = {
            "SERVICE": "WFS",
            "VERSION": "2.0.0",
            "REQUEST": "GetFeature",
            "TYPENAMES": typename
        }
        try:
            r2 = requests.get(url, params=params2, timeout=120)
            r2.raise_for_status()
            out_path = out_dir / f"{typename.replace(':', '_')}_default.gml"
            with open(out_path, "w", encoding="utf-8") as f:
                f.write(r2.text)
            print(f"Saved to {out_path}")
        except Exception as e2:
            print(f"Failed to download {typename} without OUTPUTFORMAT: {e2}")
            if 'r2' in locals():
                print(f"Server response (first 500 chars):\n{r2.text[:500]}")

if __name__ == "__main__":
    for layer in layers:
        # Skip fis:s_wfs_alkis_ortsteile
        if layer["name"] == "fis:s_wfs_alkis_ortsteile":
            print(f"Skipping {layer['name']}")
            continue
        download_layer(layer)
