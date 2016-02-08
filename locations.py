import os.path
import xml.etree.ElementTree as etree
import xml.parsers.expat.errors
import logging

logger=logging.getLogger(__file__)

class Landscape(object):
    def __init__(self):
        pass

    def from_naadsm_file(self, root, ns):
        self.farms=list()
        for unit in root.findall("herd", ns):
            unit_name=unit.find("id").text
            f=Farm(unit_name)
            unit_type=unit.find("production-type").text
            f.production_type=unit_type
            unit_size=int(unit.find("size").text)
            f.size=unit_size
            location=unit.find("location")
            lat=float(location.find("latitude").text)
            lon=float(location.find("longitude").text)
            f.latlon=np.array([lat, lon])
            status=unit.find("status").text
            f.status=status
            self.farms.append(f)
        self.farm_locations=np.array([x.latlon for x in self.farms])
        self.distances=distance.squareform(
            distance.pdist(self.farm_locations, util.distancekm))
        logger.debug("found {0} farms".format(len(self.farms)))

def load_naadsm_herd(herd_filename):
    ns={"naadsm" : "http://www.naadsm.org/schema",
        "xsd" : "http://www.w3.org/2001/XMLSchema",
        "xml" : "http://www.w3.org/XML/1998/namespace",
        "gml" : "http://www.opengis.net/gml",
        "xsi" : "http://www.w3.org/2001/XMLSchema-instance"}
    try:
        hxml=etree.parse(herd_filename)
    except etree.ParseError as err:
        logger.error("Could not parse {0} at line {1} with error {2}".format(
            herd_filename, err.position,
            xml.parsers.expat.errors.messages[err.code]))
    
    landscape=Landscape()
    landscape.from_naadsm_file(hxml, ns)
    return landscape

def load_herd_locations(herd_filename):
    return load_naadsm_herd(herd_filename).farm_locations
