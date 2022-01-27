# Copyright (c) 2022 5@xes.
# Cura is released under the terms of the AGPLv3 or higher.

from . import TrackPrint

from UM.i18n import i18nCatalog
catalog = i18nCatalog("cura")

def getMetaData():
    return {
        "view": {
            "name": "TrackPrint",
            "weight": 1
        }
    }

def register(app):
    return {"extension": TrackPrint.TrackPrint()}
