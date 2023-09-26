# Prayers-and-Readings
Capture online content for prayers with bible readings.

Using templates and online content (daily readings and prayers) 
create content using bible readings from a version on my choice.

Currently using NLT - New Living Translation - for the readings.  
Capturing the daily readings and prayers from the Moravian daily prayers.
Capturing the daily readings and meditations from the Northumbrian Community.
Daily office templates based on the Northumbrian Community daily prayers 
with fixed prayers and text "translated" into more contemporary english
and replacing as much as possible with the bible quotes they come from.

Forms the basis of my Daily Office.

## Generating pages

Using templates to generate pages.
* Template File Date
* Current File Date
* Generated File Date - older of:
  * Moravian Date
  * Northumbrian Date

1. If current:
   1. If current < template: generate new
1. Else:
   1. If generated:
      1. If generate >= today: generate new
      1. Else: *don't* generate
   1. Else: generate with now date