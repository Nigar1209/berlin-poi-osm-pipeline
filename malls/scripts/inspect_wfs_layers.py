
import xml.etree.ElementTree as ET
import requests
import csv
import json
from pathlib import Path

ENDPOINTS = [
    "https://gdi.berlin.de/services/wfs/alkis_bezirke",
    "https://gdi.berlin.de/services/wfs/alkis_ortsteile",
    "https://fbinter.stadt-berlin.de/fb/wfs/data/senstadt/s_wfs_alkis_ortsteile",
]

def list_layers(url):
    r = requests.get(url, params={"SERVICE":"WFS","REQUEST":"GetCapabilities"}, timeout=60)
    r.raise_for_status()
    root = ET.fromstring(r.content)
    ns = {'wfs': 'http://www.opengis.net/wfs/2.0', 'ows': 'http://www.opengis.net/ows/1.1'}
    layers = []
    for ft in root.findall(".//wfs:FeatureType", ns):
        name = ft.find("wfs:Name", ns)
        title = ft.find("wfs:Title", ns)
        if title is None:
            title = ft.find("ows:Title", ns)
        if name is not None:
            layers.append({
                "endpoint": url,
                "name": name.text,
                "title": title.text if title is not None else ""
            })
    return layers

if __name__ == "__main__":
    all_layers = []
    for ep in ENDPOINTS:
        try:
            layers = list_layers(ep)
            all_layers.extend(layers)
        except Exception as e:
            print("Failed:", ep, e)

    # Write to CSV
    out_dir = Path(__file__).parent.parent / "sources"
    out_dir.mkdir(parents=True, exist_ok=True)
    csv_path = out_dir / "wfs_layers_combined.csv"
    json_path = out_dir / "wfs_layers_combined.json"
    with open(csv_path, "w", newline='', encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["endpoint", "name", "title"])
        writer.writeheader()
        writer.writerows(all_layers)
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(all_layers, f, ensure_ascii=False, indent=2)
    print(f"Wrote {len(all_layers)} layers to {csv_path} and {json_path}")
