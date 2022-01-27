# Copyright (c) 2020 5@xes.
# Cura is released under the terms of the AGPLv3 or higher.

from . import ProfilAnalyser

from UM.i18n import i18nCatalog
catalog = i18nCatalog("cura")

def getMetaData():
    return {
        "view": {
            "name": "ProfilAnalyser",
            "weight": 1
        }
    }

def register(app):
    return {"extension": ProfilAnalyser.ProfilAnalyser()}
