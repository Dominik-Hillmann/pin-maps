# pin-maps
A program that places pins on a map to create posters.

## Usage
This example will show you the most likely usage of the program.
```sh
cd pin-maps
python pin_maps\pin_maps.py --country de --heading "This is the heading" --towns "Rüsselsheim, Wolfsburg, Dresden, Zwickau, Stuttgart, München, Emden, Ingolstadt" --body "This the Wolfsburg body which can display Rüsselsheim am Main coats of arms of the (München) towns provided. Emden, Stuttgart." --ribbons --superscale
```
![Example](output/read-me-example.png)
The following example shows which parameters you must provide:
```sh
cd pin-maps
python pin_maps/pin_maps.py --country de --heading "This is the heading" --body "These are the undertitles/body with smaller font"
```
Aside from these, optional command line parameters are:
* `--towns`: The cities which you want to see on the map. Example usage is for example: `--towns "Ingolstadt, Stuttgart, Wolfsburg, München, Zwickau"`.
* `--marker`: The image that will be display at the location of the chosen cities. Available options can be seen in the `config.json` under `"markers"`.
* `--fonts`: The name of the fonts used. The first one is the font of the heading. Available fonts can be found in the `config.json` under `"fonts"`.
* `--ribbons`: If set will include the ribbon with the town's name over the marker.
* `--notextcoats`: If set will not include any coat of arms in the undertitle.
* `--noborder`: If set will not draw a border around the complete image.
* `--nologo`: If set will not draw the logo at the poster's bottom.
* `--superscale`: Will scale the complete image by a factor of 4 if set.
* TODO noch erwähnen, dass `\n` im Text Zeilenumbruch verursacht

## Configuration
You can configure the program over all runs in the `config.json`.

### Markers
```json
"markers": {
    "heraldry": "heraldry",
    "white": "white-shade.png"
}
```
This section contains all available markers. The keyword is the key and the value 
is the image the image that will be shown. 
You can add new ones freely by inserting the image into `data/img/` and providing
a key for the command line here.
`heraldry` is a special case that should not be changed.

### Fonts
```json
"fonts": {
    "crimson": "crimson.ttf"
}
```
In this section you can add new fonts the same way you add new markers.

### General settings
```json
"general": {    
    "height-text-space": 930,
    "added-frame-px": 150,
    "undertitle-line-spacing": 30,
    "logo-height": 30
}
```
* `height-text-space`: The space added under the map to provide space for the
heading and undertitles.
* `added-frame-px`: Number of pixels added as frame afterwards.
* `undertitle-line-spacing`: Spacing between lines in the undertitles.
* `logo-height`: Height of the logo at the bottom of the poster.

### Country settings
```json
"countries": {
    "de": {
        "shapefile": "de-neg.shp",
        "aspect-ratio": 1.2,
        "wallpapers": {
            "old-topo": {
                "filename": "old-topo.png",
                "extent": [5.82, 15.12, 47.19, 55.31],
                "shaped": false
            }
        }
    }
}
```
If you want to add a new country, provide a new key like `it` for Italy and
provide the same data as here.
* `shapefile`: The name of the country's shapefile.
* `aspect-ratio`: The country's aspect ratio so that it looks natural.
* `wallpapers`: Provide a background by key with the following data.
    * `filename`: File name of the background.
    * `extent`: Extent by coordinates of the country.
    * `shaped`: Whether it is shaped like the country. (Controls whether it will overimpose the shape of the country afterwards.)

## Installation
TBD