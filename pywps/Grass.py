"""
Module is here for work with GRASS GIS environment varibales and
locations and mapsets
"""
# Author:	Jachym Cepicky
#        	http://les-ejk.cz
# Lince: 
# 
# Web Processing Service implementation
# Copyright (C) 2006 Jachym Cepicky
# 
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
# 
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301  USA

import os
import time, shutil, tempfile
import sys

class Grass:
    """
    GRASS initialization interface
    """

    locationDir = ""
    locationName = ""
    mapsetDir = ""
    mapsetName = ""
    gisbase = ""

    def  __init__(self,executeRequest):
        """ Initalization of GRASS environment variables (except GISRC).  """

        self.executeRequest = executeRequest
        self.wps = self.executeRequest.wps
        self.envs = {
                "path":"PATH",
                "addonPath":"GRASS_ADDONS_PATH",
                "version":"GRASS_VERSION",
                "gui":"GRASS_GUI",
                "gisbase": "GISBASE",
                "ldLibraryPath": "LD_LIBRARY_PATH"
        }

        # put env
        for key in self.envs.keys():
            try:
                self.setEnv(self.envs[key],self.wps.getConfigValue("grass",key))
            except :
                pass

        # GIS_LOCK
        self.setEnv('GIS_LOCK',str(os.getpid()))
        
    def mkMapset(self,location=None):
        """
        Create GRASS mapset in current directory. Mapsets name is 'mapset'.
        At the end, GRASS will beleve, it was runned correctly.

        Returns name of new created mapset. location!=None, this mapset
        should be deleted!

        Argumnets:
            location     -  Should the new mapset be created in the some old
                            location, which is allread on this server?
                            Default: only mapset within
                            /tmp/grasstmpSOMEHTIN/
                            will be created
        """

        self.locationDir = location

        if not self.locationDir:
            self.locationDir = self.executeRequest.workingDir

        self.mapsetDir = tempfile.mkdtemp(prefix="pywps",dir=self.locationDir)
        self.mapsetName = os.path.split(self.mapsetDir)[1]
        self.locationName = os.path.split(self.locationDir)[1]

        if location == self.wps.workingDir:
            # create new WIND file
            self._windFile(self.mapsetName)

            # create mapset PERMANENT
            os.mkdir("PERMANENT")
            self._windFile("PERMANENT")

            self.gisdbase = os.path.split(os.path.abspath(os.path.curdir))[0]

        # location is here, we justhave to use it
        else:
            self.executeRequest.dirsToBeRemoved.append(os.path.abspath(self.mapsetDir))

            # copy
            shutil.copy(os.path.join(
                self.locationDir,"PERMANENT","DEFAULT_WIND"),
                os.path.join(self.mapsetDir,"WIND"))

            # export env. vars
            (self.gisdbase,location) = os.path.split(self.locationDir)
             

        self.setEnv('MAPSET', self.mapsetName)
        self.setEnv('LOCATION_NAME',self.locationName)
        self.setEnv('GISDBASE', self.gisdbase)

        # gisrc
        gisrc = open(os.path.join(self.locationDir,"grassrc"),"w")
        gisrc.write("LOCATION_NAME: %s\n" % self.locationName)
        gisrc.write("MAPSET: %s\n" % self.mapsetName)
        gisrc.write("DIGITIZER: none\n")
        gisrc.write("GISDBASE: %s\n" % self.gisdbase)
        gisrc.write("OVERWRITE: 1\n")
        gisrc.write("GRASS_GUI: text\n")
        gisrc.close()

        self.setEnv("GISRC",os.path.join(self.executeRequest.workingDir,"grassrc"))

        return self.mapsetName

    def _windFile(self,mapset):
        """ Create default WIND file """

        if mapset == "PERMANENT":
            windname = "DEFAULT_WIND"
        else:
            windname = "WIND"

        wind =open(
                os.path.join(
                    os.path.abspath(self.executeRequest.workingDir),mapset,windname),"w")
        wind.write("""proj:       0\n""")
        wind.write("""zone:       0\n""")
        wind.write("""north:      1000\n""")
        wind.write("""south:      0\n""")
        wind.write("""east:       1000\n""")
        wind.write("""west:       0\n""")
        wind.write("""cols:       1000\n""")
        wind.write("""rows:       1000\n""")
        wind.write("""e-w resol:  1\n""")
        wind.write("""n-s resol:  1\n""")
        wind.close()
        return

    def setEnv(self,key,value):
        """Set GRASS environment variables """

        origValue = os.getenv(key)
        if origValue:
            value  += ":"+origValue
        os.putenv(key,value)
        os.environ[key] = value
        return
