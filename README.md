# Profile Analyser
Cura profile analyser ( initialy based on the GodMod Plugin https://github.com/sedwards2009/cura-god-mode-plugin )

Plugin for Cura to analyse the Cura profiles configuration much easier.

This plugins lets you dump the contents of the curent global and extruder settings stacks to an HTML page which opens up in your default browser. There you can inspect the values and also filter the list of settings.

To install just copy the ProfilAnalyser directory into the plugins directory in your Cura plugins directory.

Once Cura is running you can find the plugin in the Extensions menu -> Profil Analyser.

## Cura compatibility

Plugin tested from release 4.8 to 5.1

Plugin partialy tested in release 4.7 works whithout garanty

This plugin doesn't work in 4.6 so I guess for the previous versions.

## Modifications

### Version 1.1.0

Thanks to the csakip contribution (https://github.com/csakip) possibility to show only differents between profiles and select profiles to compare.

### Version 1.1.1

Add Widget unselect all in the compare HTML page.

### Version 1.1.2

Add widget "Show only valued parameters".

### Version 1.1.3

Change text separator for filtering option

### Version 1.2.0

Compatibility Cura 5.0

### Version 1.2.1

Change the name for the generated file to compare two Cura analyse.

## Browser Javascript compatibility

JScript used in the Html page have been succesfuly tested on :
- Google Chrome  (64 bits)
- Microsoft Edge (64 bits)


- IE 11 and previous release ? : not supported
