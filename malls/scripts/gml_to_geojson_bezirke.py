import xml.etree.ElementTree as ET
import json
from shapely.geometry import Polygon, mapping, MultiPolygon
from pathlib import Path

# File paths
infile = Path(__file__).parent.parent / "sources" / "wfs_downloads" / "alkis_bezirke_bezirksgrenzen.gml"
outfile = Path(__file__).parent.parent / "sources" / "wfs_downloads" / "alkis_bezirke_bezirksgrenzen.geojson"

# GML and custom namespaces
ns = {
    'gml': 'http://www.opengis.net/gml/3.2',
    'alkis': 'alkis_bezirke'
}

# Parse GML
root = ET.parse(infile).getroot()
features = []

for member in root.findall('.//{http://www.opengis.net/wfs/2.0}member'):
    f = member.find('alkis:bezirksgrenzen', ns)
    if f is None:
        continue
    props = {
        'name': f.findtext('alkis:name', default='', namespaces=ns),
        'gem': f.findtext('alkis:gem', default='', namespaces=ns),
        'namgem': f.findtext('alkis:namgem', default='', namespaces=ns),
        'namlan': f.findtext('alkis:namlan', default='', namespaces=ns),
        'lan': f.findtext('alkis:lan', default='', namespaces=ns)
    }
    # Geometry: MultiSurface > surfaceMember > Polygon > exterior > LinearRing > posList
    geom = f.find('.//gml:MultiSurface', ns)
    polygons = []
    if geom is not None:
        for surf in geom.findall('.//gml:surfaceMember', ns):
            poly = surf.find('.//gml:Polygon', ns)
            if poly is not None:
                ring = poly.find('.//gml:exterior/gml:LinearRing/gml:posList', ns)
                if ring is not None:
                    coords = [float(x) for x in ring.text.strip().split()]
                    # GML posList is flat: x1 y1 x2 y2 ...
                    points = [(coords[i], coords[i+1]) for i in range(0, len(coords), 2)]
                    polygons.append(Polygon(points))
    if polygons:
        geometry = mapping(MultiPolygon(polygons) if len(polygons) > 1 else polygons[0])
    else:
        geometry = None
    features.append({
        'type': 'Feature',
        'properties': props,
        'geometry': geometry
    })

geojson = {
    'type': 'FeatureCollection',
    'features': features
}

with open(outfile, 'w', encoding='utf-8') as f:
    json.dump(geojson, f, ensure_ascii=False, indent=2)

print(f"Wrote {len(features)} features to {outfile}")
