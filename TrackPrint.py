#-----------------------------------------------------------------------------------------------------------------------------
# Copyright (c) 2022 5@xes
# Cura is released under the terms of the AGPLv3 or higher.
#
# 29/01/2022 New Prototype
#
#-----------------------------------------------------------------------------------------------------------------------------
import os
import platform
import os.path
import tempfile
import html
import json
import re

from datetime import datetime
from typing import cast, Dict, List, Optional, Tuple, Any, Set
from cura.CuraApplication import CuraApplication
from UM.Workspace.WorkspaceWriter import WorkspaceWriter
from UM.Settings.InstanceContainer import InstanceContainer
from UM.Settings.ContainerRegistry import ContainerRegistry
from UM.Qt.Duration import DurationFormat
from UM.Preferences import Preferences

from cura.CuraVersion import CuraVersion  # type: ignore
from UM.Version import Version

from UM.Settings.DefinitionContainer import DefinitionContainer
from UM.Settings.SettingDefinition import SettingDefinition
from UM.Extension import Extension
from UM.Application import Application

from UM.Logger import Logger
from UM.Message import Message

from PyQt5.QtCore import QObject, QUrl
from PyQt5.QtGui import QDesktopServices

from UM.i18n import i18nCatalog
i18n_cura_catalog = i18nCatalog('cura')
i18n_catalog = i18nCatalog('fdmprinter.def.json')
i18n_extrud_catalog = i18nCatalog('fdmextruder.def.json')


encode = html.escape

class TrackPrint(Extension, QObject):
    def __init__(self, parent = None):
        QObject.__init__(self, parent)
        Extension.__init__(self)

        self.addMenuItem('Add Current Print', addPrint)
        self.addMenuItem('View Impression', viewAll)

def addPrint():
    openHtmlPage('cura_settings.html', htmlPage('cura_settings.html'))
    
def viewAll():
    viewHtmlPage('cura_settings.html')

    
def htmlPage(page_name):

    path = os.path.join(tempfile.gettempdir(), page_name)
    
    result = os.path.isfile(path)
    
    if result == False :
        Logger.log("d", "Fichier : " + path)
        html = getHtmlHeader()
    
    # os.path.abspath(stream.name)
   
    html = tableHeader("Name")
    # File
    # self._WriteTd(stream,"File",os.path.abspath(stream.name))
    # Date
    cDa = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    html += writeTd("Date",cDa)
        # platform
    pLatf = str(platform.system()) + " " + str(platform.version())
    html += writeTd("Os",pLatf)
        
    # html += '<h2 id="global_stack">Global Stack</h2>'
    # html += formatContainerStack(Application.getInstance().getGlobalContainerStack())
    
    html += tableFooter()

    html += htmlFooter
    return html
 
def writeTd(Key,ValStr):

    html_td = "<tr>"
    html_td += "<td class='w-50'>" 
    html_td += Key
    html_td += "</td>"
    html_td += "<td colspan='2'>"
    html_td += str(ValStr) 
    html_td += "</td>"
    html_td +="</tr>\n"
    return html_td
   
def formatContainer(container, name='Container', short_value_properties=False, show_keys=True):
    html = ''
    html += '<a id="' + str(id(container)) + '" ></a>'
    #
    if safeCall(container.getName) == "empty" :
        html += tableHeader(name + ': ' + safeCall(container.getId))
    else :
        html += tableHeader(name + ': ' + safeCall(container.getName))
    
    html += formatContainerMetaDataRows(container)

    if show_keys:
        key_properties = ['value', 'resolve'] if short_value_properties else setting_prop_names
        key_properties.sort()

        # hasattr() method returns true if an object has the given named attribute and false if it does not
        if hasattr(container, 'getAllKeys'):
            keys = list(container.getAllKeys())
            for key in keys:
                html += formatSettingsKeyTableRow(key, formatSettingValue(container, key, key_properties))

    html += tableFooter()
    return html    

def formatContainerMetaDataRows(def_container):
    html = ''
    try:
        # Logger.log("d", "quality_type : " + safeCall(def_container.getMetaDataEntry('quality_type')))
        html += formatKeyValueTableRow('type', def_container.getMetaDataEntry('type'), extra_class='metadata') 
        # html += formatKeyValueTableRow('<type>', type(def_container), extra_class='metadata')
        # html += formatKeyValueTableRow('<id>', def_container, extra_class='metadata')
        html += formatKeyValueTableRow('id', safeCall(def_container.getId), extra_class='metadata')
        html += formatKeyValueTableRow('name', safeCall(def_container.getName), extra_class='metadata')
 
        MetaData_definition = def_container.getMetaDataEntry('definition')
        if MetaData_definition is not None:
            html += formatKeyValueTableRow('definition', MetaData_definition, extra_class='metadata')
        MetaData_quality_type = def_container.getMetaDataEntry('quality_type')
        if MetaData_quality_type is not None:
            html += formatKeyValueTableRow('quality_type', MetaData_quality_type, extra_class='metadata')  
            
        # hasattr() method returns true if an object has the given named attribute and false if it does not
        html += formatKeyValueTableRow('read only', safeCall(def_container.isReadOnly), extra_class='metadata')
        if hasattr(def_container, 'getPath'):
            html += formatKeyValueTableRowFile('path', safeCall(def_container.getPath), extra_class='metadata')
        if hasattr(def_container, 'getType'):
            html += formatStringTableRow('type', safeCall(def_container.getType), extra_class='metadata')

    except:
        pass

    return html
    



setting_prop_names = SettingDefinition.getPropertyNames()
def formatSettingValue(container, key, properties=None):
    if properties is None:
        properties = setting_prop_names

    #value = '<ul class=\'property_list\'>\n'
    value = ''
    comma = ''
    properties.sort()
    for prop_name in properties:
        prop_value = container.getProperty(key, prop_name)
        if prop_value is not None:
            if prop_name=='value' :
                # repr() function returns a printable representation of the given object
                print_value = repr(prop_value)
                if print_value.find('UM.Settings.SettingFunction') > 0 :
                    # Logger.log("d", "print_value : " + print_value)
                    strtok_value = print_value.split('=',1)
                    # Logger.log("d", "print_value : " + str(strtok_value[1]))
                    final_value = '=' + strtok_value[1].replace(' >','')
                else :
                    final_value = print_value
                    
                #value += '  <li>\n'
                # value += '    <span class="prop_name">' + encode(prop_name) + ':</span> ' + encode(final_value)
                value += encode(final_value)
                # value += '  </li>\n'
    #value += '</ul>\n'
    value += '\n'

    return RawHtml(value)
    
def safeCall(callable):
    try:
        result = callable()
        return result
    except Exception as ex:
        return ex

def tableHeader(title):
    return '''<table class='key_value_table'>
    <thead><tr><th colspan='2'>''' + encode(title) + '''</th></tr></thead>
    <tbody>
'''

def tableFooter():
    return '</tbody></table>\n'

def formatStringTableRow(key, value, extra_class=''):
    clazz = ''
    formatted_value = encode(str(value))
    formatted_key = encode(str(key))

    return '<tr class="' + extra_class + ' ' + clazz + '"><td class="key">' + formatted_key + '</td><td class="value">' + formatted_value + '</td></tr>\n'
    
def formatKeyValueTableRow(key, value, extra_class=''):
    clazz = ''
    if isinstance(value, Exception):
        clazz = 'exception'

    if isinstance(value, RawHtml):
        formatted_value = value.value
    elif isinstance(value, dict):
        formatted_value = encode(json.dumps(value, sort_keys=True, indent=4))
        clazz += ' preformat'
    elif isinstance(value, DefinitionContainer):
        formatted_value = encode(value.getId() + ' ' + str(value))
    else:
        formatted_value = encode(str(value))

    if isinstance(key, RawHtml):
        formatted_key = key.value
    else:
        formatted_key = encode(str(key))

    return '<tr class="' + extra_class + ' ' + clazz + '"><td class="key">' + formatted_key + '</td><td class="value">' + formatted_value + '</td></tr>\n'
    
def formatKeyValueTableRowFile(key, value, extra_class=''):
    clazz = ''
    if isinstance(value, Exception):
        clazz = 'exception'

    if isinstance(value, RawHtml):
        formatted_value = value.value
    elif isinstance(value, dict):
        formatted_value = encode(json.dumps(value, sort_keys=True, indent=4))
        clazz += ' preformat'
    elif isinstance(value, DefinitionContainer):
        formatted_value = encode(value.getId() + ' ' + str(value))
    else:
        formatted_value = encode(str(value))

    if isinstance(key, RawHtml):
        formatted_key = key.value
    else:
        formatted_key = encode(str(key))

    return '<tr class="' + extra_class + ' ' + clazz + '"><td class="CellWithComment">' + formatted_key + '</td><td class="value"><a href="' + formatted_value + '">' + formatted_value + '</a></td></tr>\n'

def formatSettingsKeyTableRow(key, value):

    Cstack = CuraApplication.getInstance().getGlobalContainerStack()
    
    clazz = ''
    # Test if type Exception
    if isinstance(value, Exception):
        clazz = 'exception'

    # Test if type RawHtml
    if isinstance(value, RawHtml):
        formatted_value = value.value
        Display_Key = '&#x1f511; '
    else:
        formatted_value = encode(str(value))
        Display_Key = '&#x1F527; '

    formatted_key = encode(str(key))
    
    Ckey=str(key)
    
    untranslated_label=str(Cstack.getProperty(Ckey, 'label'))
    definition_key=Ckey + ' label'
    translated_label=i18n_catalog.i18nc(definition_key, untranslated_label)
    untranslated_description=str(Cstack.getProperty(Ckey, 'description'))
    description_key=Ckey + ' description'
    translated_description=i18n_catalog.i18nc(description_key, untranslated_description)
    
    # &#x1f511;  => Key symbole
    return '<tr class="' + clazz + '" --data-key="' + translated_label + '"><td class="CellWithComment">' + Display_Key + translated_label +  '<span class="CellComment">' + translated_description + '</span></td><td class="value">' + formatted_value + '</td></tr>\n'

 
def openHtmlPage(page_name, html_contents):
    target = os.path.join(tempfile.gettempdir(), page_name)
    with open(target, 'a', encoding='utf-8') as fhandle:
        fhandle.write(html_contents)
    QDesktopServices.openUrl(QUrl.fromLocalFile(target))

def viewHtmlPage(page_name):
    target = os.path.join(tempfile.gettempdir(), page_name)
    QDesktopServices.openUrl(QUrl.fromLocalFile(target))
    
def getHtmlHeader(page_name='Cura Settings'):
    return '''<!DOCTYPE html><html>
<head>
<meta charset='UTF-8'>
<title>''' + encode(page_name) + '''</title>
<script>
</script>
<style>
html {
  font-family: sans-serif;
  font-size: 11pt;
}

a, a:visited {
  color: #0000ff;
  text-decoration: none;
}

ul {
  padding-left: 1em;
}


table.key_value_table {
  border-collapse: separate;
  border: 1px solid #e0e0e0;
  margin-top: 16px;
  border-top-left-radius: 5px;
  border-top-right-radius: 5px;
  border-bottom-left-radius: 4px;
  border-bottom-right-radius: 4px;
  border-spacing: 0px;
}

table.key_value_table_extruder > thead th {
  text-align: left;
  background-color: #428000;
  color: #ffffff;
}

table.key_value_table th, table.key_value_table td {
  padding: 4px;
}

table.key_value_table > thead th {
  text-align: left;
  background-color: #428bca;
  color: #ffffff;
  border-top-left-radius: 4px;
  border-top-right-radius: 4px;
}

table.key_value_table > tbody > tr:nth-child(even) {
  background-color: #e0e0e0;
}

table.key_value_table_extruder > tbody > tr:nth-child(even) {
  background-color: #e0f0f0;
}

table.key_value_table > tbody > tr.exception {
  background-color: #e08080;
}

table.key_value_table td.key {
  font-weight: bold;
}

table.key_value_table tr.preformat td.value {
  white-space: pre;
}

table.key_value_table tr.preformat td.value_extruder {
  white-space: pre;
  background-color: #e0f0f0;
}

div.container_stack {
  padding: 8px;
  border: 2px solid black;
  border-radius: 8px;
}

div.container_stack > table.key_value_table > thead th {
  background-color: #18294D;
}

div.container_stack_containers {
  margin: 4px;
  padding: 4px;
  border: 1px dotted black;
  border-radius: 4px;
}

td.CellWithComment{
  white-space: pre;
  font-weight: bold;
  position:relative;
}

.CellComment{
  display:none;
  position:absolute; 
  z-index:100;
  border:1px;
  background-color:white;
  border-style:solid;
  border-width:1px;
  border-color:blue;
  padding:3px;
  color:blue; 
  top:30px; 
  left:20px;
  font-weight: lighter;
}

td.CellWithComment:hover span.CellComment{
  display:block;
}

tr.key_hide {
  display: none;
}

body.hide_metadata tr.metadata {
  display: none;
}

ul.property_list {
  list-style: none;
  padding-left: 0;
  margin-left: 0;
}

span.prop_name {
  font-weight: bold;
}
tr.hidden, td.hidden, th.hidden {
  display: none;
}
</style>
</head>
<body onload="initKeyFilter();">
'''

htmlFooter = '''</body>
</html>
'''
class RawHtml:
    def __init__(self, value):
        self.value = value
