# Copyright (c) 2016 Ultimaker B.V.
# Cura is released under the terms of the AGPLv3 or higher.
# Initial source code cura-god-mode-plugin from sedwards2009
# https://github.com/sedwards2009/cura-god-mode-plugin
#
# 5Axes  limit analyse to user Profil debuging
#
from UM.Settings.DefinitionContainer import DefinitionContainer
from UM.Settings.SettingDefinition import SettingDefinition
from UM.Extension import Extension
from UM.Application import Application
from UM.Settings.ContainerRegistry import ContainerRegistry

from cura.CuraApplication import CuraApplication


from UM.Logger import Logger
from UM.Message import Message

from PyQt5.QtCore import QObject, QUrl
from PyQt5.QtGui import QDesktopServices

import os.path
import tempfile
import html
import json
import re

encode = html.escape

class ProfilAnalyser(Extension, QObject):
    def __init__(self, parent = None):
        QObject.__init__(self, parent)
        Extension.__init__(self)

        self.addMenuItem("View Active Configuration", viewAll)
        self.addMenuItem("View All Profiles", viewAllQualityChanges)
        self.addMenuItem("View All Current Printer Profiles", viewAllPrinterQualityChanges)
        self.addMenuItem("View All User Containers", viewAllUserContainers)

def viewAll():
    openHtmlPage("cura_settings.html", htmlPage())

def htmlPage():
    html = getHtmlHeader()

    # Menu creation
    html += "<div class='menu'>\n"
    html += "<ul>"
    
    html += "<li><a href='#global_stack'>Global Stack</a>"
    html += formatContainerStackMenu(Application.getInstance().getGlobalContainerStack())
    html += "</li>\n"

    html += "<li><a href='#extruder_stacks'>Extruder Stacks</a>\n"
    html += formatExtruderStacksMenu()
    html += "</li>\n"

    html += "</ul>\n"
    
    # Java script filter function
    html += keyFilterWidget()
    html += "</div>"

    # Contents creation
    html += "<div class='contents'>"
    html += "<h2 id='global_stack'>Global Stack</h2>"
    html += formatContainerStack(Application.getInstance().getGlobalContainerStack())

    html += formatExtruderStacks()

    html += "</div>"

    html += htmlFooter
    return html
    
def viewAllUserContainers():
    openHtmlPage("cura_user_containers.html", containersOfTypeHtmlPage("User Containers", "user"))

def viewAllPrinterQualityChanges():
    #stack = Application.getInstance().getGlobalContainerStack()
    machine_manager = Application.getInstance().getMachineManager()
    global_stack = machine_manager.activeMachine
    machine_id=global_stack.quality.getMetaData().get("definition", "")    
    Logger.log('d', 'viewAllPrinterQualityChanges : ' + machine_id )
    openHtmlPage("cura_quality_changes.html", containersOfTypeHtmlPage2("Printer Quality Changes", "quality_changes", machine_id ))
    
def viewAllQualityChanges():
    openHtmlPage("cura_quality_changes.html", containersOfTypeHtmlPage("Quality Changes", "quality_changes"))

# name header et Type
def containersOfTypeHtmlPage(name, type_):
    html = getHtmlHeader(name)

    html += "<div class='menu'>\n"
    html += "<ul>"
    
    # find Instance Containers according to type=type_
    containers = ContainerRegistry.getInstance().findInstanceContainers(type=type_)
    
    # Sort containers Order
    containers.sort(key=lambda x: x.getName())
    
    # Menu creation
    for container in containers:
        # Logger.log('d', 'getName : ' + container.getName() )
        if container.getName() == 'empty' :
            html += "<li><a href='#"+ str(id(container)) + "'>"+encode(container.getId())+"</a></li>\n"
        else :
            html += "<li><a href='#"+ str(id(container)) + "'>"+encode(container.getName())+"</a></li>\n"   
            
    html += "</ul>"

    # Java script filter function
    html += keyFilterWidget()
    html += "</div>"

    html += "<div class='contents'>"
    html += formatAllContainersOfType(name, type_)
    html += "</div>"

    html += htmlFooter
    return html

def formatAllContainersOfType(name, type_):
    html = "<h2>" + name + "</h2>\n"

    #if type_ == "machine":
    #    containers = ContainerRegistry.getInstance().findDefinitionContainers()
    #else:
    
    # type "quality_changes" or "user"
    containers = ContainerRegistry.getInstance().findInstanceContainers(type=type_)

    containers.sort(key=lambda x: x.getName())
    
    for container in containers:
        html += formatContainer(container)
    return html

# name header et Type
def containersOfTypeHtmlPage2(name, type_ ,machine_id_):
    html = getHtmlHeader(name)
    
    
    html += "<div class='menu'>\n"
    html += "<ul>"
    
    # find Instance Containers according to type=type_  (quality_changes)  and definition
    containers = ContainerRegistry.getInstance().findInstanceContainers(definition = machine_id_, type=type_)
    
    # Sort containers Order
    containers.sort(key=lambda x: x.getName())
    
    # Menu creation
    for container in containers:
        # Logger.log('d', 'containersOfTypeHtmlPage2 : ' + str(container) )
        if container.getName() == 'empty' :
            html += "<li><a href='#"+ str(id(container)) + "'>"+encode(container.getId())+"</a></li>\n"
        else :
            html += "<li><a href='#"+ str(id(container)) + "'>"+encode(container.getName())+"</a></li>\n"
        
    html += "</ul>"

    # Java script filter function
    html += keyFilterWidget()
    html += "</div>"

    html += "<div class='contents'>"
    html += formatAllContainersOfType2(name, type_, machine_id_)
    html += "</div>"

    html += htmlFooter
    return html

def formatAllContainersOfType2(name, type_, machine_id_):
    html = "<h2>" + name + "</h2>\n"

    #if type_ == "machine":
    #    containers = ContainerRegistry.getInstance().findDefinitionContainers()
    #else:
    
    # type "quality_changes" or "user"
    containers = ContainerRegistry.getInstance().findInstanceContainers(definition = machine_id_, type=type_)

    containers.sort(key=lambda x: x.getName())
    
    for container in containers:
        html += formatContainer(container)
    return html
    
def formatContainer(container, name="Container", short_value_properties=False, show_keys=True):
    html = ""
    html += "<a id='" + str(id(container)) + "' ></a>"
    #
    if safeCall(container.getName) == 'empty' :
        html += tableHeader(name + ": " + safeCall(container.getId))
    else :
        html += tableHeader(name + ": " + safeCall(container.getName))
    html += formatContainerMetaDataRows(container)

    if show_keys:
        key_properties = ["value", "resolve"] if short_value_properties else setting_prop_names
        key_properties.sort()

        # hasattr() method returns true if an object has the given named attribute and false if it does not
        if hasattr(container, "getAllKeys"):
            keys = list(container.getAllKeys())
            keys.sort()
            for key in keys:
                html += formatSettingsKeyTableRow(key, formatSettingValue(container, key, key_properties))

    html += tableFooter()
    return html    

def formatContainerMetaDataRows(def_container):
    html = ""
    try:
        # Logger.log('d', 'quality_type : ' + safeCall(def_container.getMetaDataEntry("quality_type")))
        # html += formatKeyValueTableRow("<type>", type(def_container), extra_class="metadata")
        # html += formatKeyValueTableRow("<id>", def_container, extra_class="metadata")
        html += formatKeyValueTableRow("id", safeCall(def_container.getId), extra_class="metadata")
        html += formatKeyValueTableRow("name", safeCall(def_container.getName), extra_class="metadata")
        html += formatKeyValueTableRow("definition", safeCall(def_container.getDefinition), extra_class="metadata")
        html += formatStringTableRow("type", safeCall(def_container.getType), extra_class="metadata")
        # hasattr() method returns true if an object has the given named attribute and false if it does not
        if hasattr(def_container, "_getDefinition"):
           html += formatKeyValueTableRow("definition", safeCall(def_container._getDefinition), extra_class="metadata")
        html += formatKeyValueTableRow("read only", safeCall(def_container.isReadOnly), extra_class="metadata")
        html += formatKeyValueTableRow("path", safeCall(def_container.getPath), extra_class="metadata")
        # html += formatKeyValueTableRow("metadata", safeCall(def_container.getMetaData), extra_class="metadata")
    except:
        pass

    return html
    
def formatExtruderStacks():
    html = ""
    html += "<h2 id='extruder_stacks'>Extruder Stacks</h2>"
    machine = Application.getInstance().getMachineManager().activeMachine
    for position, extruder_stack in sorted([(int(p), es) for p, es in machine.extruders.items()]):
        position = str(position)
        html += "<h3 id='extruder_index_" + position + "'>Index " + position + "</h3>"
        html += formatContainerStack(extruder_stack)
    return html

def formatExtruderStacksMenu():
    html = ""
    html += "<ul>"
    machine = Application.getInstance().getMachineManager().activeMachine
    for position, extruder_stack in sorted([(int(p), es) for p, es in machine.extruders.items()]):
        html += "<li>"
        html += "<a href='#extruder_index_" + str(position) + "'>Index " + str(position) + "</a>\n"
        html += formatContainerStackMenu(extruder_stack)
        html += "</li>"
    html += "</ul>"
    return html

def formatContainerStack(stack, show_stack_keys=True):
    html = "<div class='container_stack'>\n"
    html += formatContainer(stack, name="Container Stack", short_value_properties=True)
    html += "<div class='container_stack_containers'>\n"
    html += "<h3>Containers</h3>\n"
    for container in stack.getContainers():
        html += formatContainer(container, show_keys=show_stack_keys)
    html += "</div>\n"
    html += "</div>\n"
    return html

def formatContainerStackMenu(stack):
    html = ""
    html += "<a href='#" + str(id(stack)) + "'></a><br />\n"
    html += "<ul>\n"
    for container in stack.getContainers():
        #
        if container.getName() == 'empty' :
            html += "<li><a href='#" + str(id(container)) + "'>" + encode(container.getId()) + "</a></li>"
        else:
            html += "<li><a href='#" + str(id(container)) + "'>" + encode(container.getName()) + "</a></li>"
    html += "</ul>\n"
    return html

setting_prop_names = SettingDefinition.getPropertyNames()
def formatSettingValue(container, key, properties=None):
    if properties is None:
        properties = setting_prop_names

    value = "<ul class=\"property_list\">\n"
    comma = ""
    properties.sort()
    for prop_name in properties:
        prop_value = container.getProperty(key, prop_name)
        if prop_value is not None:
            if prop_name=="value" :
                # repr() function returns a printable representation of the given object
                print_value = repr(prop_value)
                if print_value.find("UM.Settings.SettingFunction") > 0 :
                    # Logger.log('d', 'print_value : ' + print_value)
                    strtok_value = print_value.split("=",1)
                    # Logger.log('d', 'print_value : ' + str(strtok_value[1]))
                    final_value = "=" + strtok_value[1].replace(" >","")
                else :
                    final_value = print_value
                    
                value += "  <li>\n"
                # value += "    <span class='prop_name'>" + encode(prop_name) + ":</span> " + encode(final_value)
                value += encode(final_value)
                value += "  </li>\n"
    value += "</ul>\n"

    return RawHtml(value)

def safeCall(callable):
    try:
        result = callable()
        return result
    except Exception as ex:
        return ex

def tableHeader(title):
    return """<table class="key_value_table">
    <thead><tr><th colspan="2">""" + encode(title) + """</th></tr></thead>
    <tbody>
"""

def tableFooter():
    return "</tbody></table>"

def formatStringTableRow(key, value, extra_class=""):
    clazz = ""
    formatted_value = encode(str(value))
    formatted_key = encode(str(key))

    return "<tr class='" + extra_class + " " + clazz + "'><td class='key'>" + formatted_key + "</td><td class='value'>" + formatted_value + "</td></tr>\n"
    
def formatKeyValueTableRow(key, value, extra_class=""):
    clazz = ""
    if isinstance(value, Exception):
        clazz = "exception"

    if isinstance(value, RawHtml):
        formatted_value = value.value
    elif isinstance(value, dict):
        formatted_value = encode(json.dumps(value, sort_keys=True, indent=4))
        clazz += " preformat"
    elif isinstance(value, DefinitionContainer):
        formatted_value = encode(value.getId() + " " + str(value))
    else:
        formatted_value = encode(str(value))

    if isinstance(key, RawHtml):
        formatted_key = key.value
    else:
        formatted_key = encode(str(key))

    return "<tr class='" + extra_class + " " + clazz + "'><td class='key'>" + formatted_key + "</td><td class='value'>" + formatted_value + "</td></tr>\n"

def formatSettingsKeyTableRow(key, value):
    clazz = ""
    # Test if type Exception
    if isinstance(value, Exception):
        clazz = "exception"

    # Test if type RawHtml
    if isinstance(value, RawHtml):
        formatted_value = value.value
        Display_Key = "&#x1f511; "
    else:
        formatted_value = encode(str(value))
        Display_Key = "&#x1F527; "

    formatted_key = encode(str(key))
    # &#x1f511;  => Key symbole
    return "<tr class='" + clazz + "' --data-key='" + formatted_key + "'><td class='key'>" + Display_Key + formatted_key + "</td><td class='value'>" + formatted_value + "</td></tr>\n"

def keyFilterJS():
    return """
    function initKeyFilter() {
      var filter = document.getElementById('key_filter');
      filter.addEventListener('change', function() {
        var filterValue = filter.value;

        if (filterValue === "") {
          document.body.classList.add('show_metadata');
          document.body.classList.remove('hide_metadata');
        } else {
          document.body.classList.remove('show_metadata');
          document.body.classList.add('hide_metadata');
        }

        var filterRegexp = new RegExp(filterValue, 'i');

        var allKeys = document.querySelectorAll('[--data-key]');
        var i;
        for (i=0; i<allKeys.length; i++) {
          var keyTr = allKeys[i];
          var key = keyTr.getAttribute('--data-key');
          if (filterRegexp.test(key)) {
            keyTr.classList.remove('key_hide');
          } else {
            keyTr.classList.add('key_hide');
          }
        }
      });
    }
    """

def keyFilterWidget():
    html = """
    <div class='key_filter'>
    &#x1F50E; filter regex: <input type='text' id='key_filter' />
    </div>
    """
    return html

def openHtmlPage(page_name, html_contents):
    target = os.path.join(tempfile.gettempdir(), page_name)
    with open(target, "w", encoding="utf-8") as fhandle:
        fhandle.write(html_contents)
    QDesktopServices.openUrl(QUrl.fromLocalFile(target))

def getHtmlHeader(page_name="Cura Settings"):
    return """<!DOCTYPE html><html>
<head>
<meta charset="UTF-8">
<title>""" + encode(page_name) + """</title>
<script>
""" + keyFilterJS() + """
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

div.menu {
  position: fixed;
  padding: 4px;
  left: 0px;
  width: 25em;
  top: 0px;
  height: 100%;
  box-sizing: border-box;
  overflow: auto;
}

div.contents {
  padding-left: 25em;
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

table.key_value_table th, table.key_value_table td {
  padding: 4px;
}

table.key_value_table > thead th {
  width: 65em;
  text-align: left;
  background-color: #428bca;
  color: #ffffff;
  border-top-left-radius: 4px;
  border-top-right-radius: 4px;
}

table.key_value_table > tbody > tr:nth-child(even) {
  background-color: #e0e0e0;
}

table.key_value_table > tbody > tr.exception {
  background-color: #e08080;
}
table.key_value_table td.key {
  width: 25em;
  font-weight: bold;
  font-weight: bold;
}

table.key_value_table tr.preformat td.value {
  white-space: pre;
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
</style>
</head>
<body onload='initKeyFilter();'>
"""

htmlFooter = """</body>
</html>
"""
class RawHtml:
    def __init__(self, value):
        self.value = value
