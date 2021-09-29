# Copyright (c) 2013 Shotgun Software Inc.
#
# CONFIDENTIAL AND PROPRIETARY
#
# This work is provided "AS IS" and subject to the Shotgun Pipeline Toolkit
# Source Code License included in this distribution package. See LICENSE.
# By accessing, using, copying or modifying this work you indicate your
# agreement to the Shotgun Pipeline Toolkit Source Code License. All rights
# not expressly granted therein are reserved by Shotgun Software Inc.

import xml.etree.ElementTree as ET
from os import path
import sys, base64, gzip, io

import sgtk

logger = sgtk.platform.get_logger(__name__)

def WriteThumbnail(in_path,out_path):
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

class SwcFramework(sgtk.platform.Framework):
    def init_framework(self):
        """
        Implemented by deriving classes in order to initialize the app.
        Called by the engine as it loads the framework.
        """
        self.log_debug("%s: Initializing..." % self)


    def destroy_framework(self):
        """
        Implemented by deriving classes in order to tear down the framework.
        Called by the engine as it is being destroyed.
        """
        self.log_debug("%s: Destroying..." % self)

