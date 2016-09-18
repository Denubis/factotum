#!/bin/bash

set -euo pipefail

if [ ! -w mapsettings.json ]; then
cat > mapsettings.json <<- EOM
{
  "_comment": "Sizes can be specified as none, very-low, low, normal, high, very-high",

  "terrain_segmentation": "normal",
  "water": "normal",
  "width": 0,
  "height": 0,
  "starting_area": "very-high",
  "peaceful_mode": false,
  "autoplace_controls":
  {
    "coal": {"frequency": "very-low", "size": "very-high", "richness": "very-high"},
    "copper-ore": {"frequency": "very-low", "size": "very-high", "richness": "very-high"},
    "crude-oil": {"frequency": "very-low", "size": "very-high", "richness": "very-high"},
    "enemy-base": {"frequency": "very-low", "size": "high", "richness": "very-high"},
    "iron-ore": {"frequency": "very-low", "size": "very-high", "richness": "very-high"},
    "stone": {"frequency": "very-low", "size": "very-high", "richness": "very-high"}
  }
}
EOM
fi



mkdir -p factorioSave
/opt/factorio/bin/x64/factorio --create /home/factorio/factorioSave/$(date +%Y%m%d) --map-gen-settings mapsettings.json

