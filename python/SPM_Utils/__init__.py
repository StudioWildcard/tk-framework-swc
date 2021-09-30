import xml.etree.ElementTree as ET
from os import path
import sys, base64, gzip, io

def SPMWriteThumbnail(in_path,out_path):
    """
    Writes a .SPM file's thumbnail to disk.

    SpeedTree stores jpeg asset thumbnails in .SPM files as base64 encoded binary data.
    We can get this data from the Thumbnail tag's text after we decompress the .SPM.
    """
    xmlContent = None
    # Unzip the .SPM
    with gzip.open(in_path, 'rb') as ip:
        with io.TextIOWrapper(ip, encoding='utf-8') as decoder:
            xmlContent = decoder.read()

    # Find the Thumbnail, decode it, and write the bytes to disk
    if xmlContent:
        tree = ET.ElementTree(ET.fromstring(xmlContent))
        root = tree.getroot()
        thumbnail = root.find("Thumbnail").text
        decodeT = base64.b64decode( thumbnail )
        f = open(path.join(path.dirname(in_path), out_path),"wb")
        f.write(decodeT)
        return True