# Copyright (c) 2023 5@xes.
# Cura is released under the terms of the AGPLv3 or higher.

from . import ProfilAnalyser

from UM.i18n import i18nCatalog
catalog = i18nCatalog("profilanalyser")

def getMetaData():
    return {
        "view": {
            "name": catalog.i18nc("@label", "ProfilAnalyser"),
            "description": catalog.i18nc("@info:tooltip", "Analyser for Cura Profiles"),
            "weight": 1
        }
    }

def register(app):
    return {"extension": ProfilAnalyser.ProfilAnalyser()}
