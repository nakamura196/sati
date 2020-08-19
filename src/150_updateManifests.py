import shutil
import requests
import os
import json
import glob
import yaml
import sys
import urllib
import ssl
import csv
import time

path = "../docs/iiif/curation.json"

with open(path) as f:
    curation = json.load(f)

selections = curation["selections"]

label_id_map = {}

for selection in selections:
    members = selection["members"]

    for member in members:
        id = member["@id"]
        label = member["label"]

        label_id_map[label] = id

for selection in selections:
    members = selection["members"]

    for member in members:
        label = member["label"]

        id = label

        path = "data/json/similar_images/"+id+".json"

        if os.path.exists(path):
            with open(path) as f:
                data = json.load(f)

            images = []
            max = 20
            for i in range(0, len(data)):
                id2 = data[i].split("/")[-1].split(".")[0]
                if id2 in label_id_map:
                    images.append(label_id_map[id2])

                if len(images) >= max:
                    break
            member["images"] = images

path = "../docs/iiif/curation.json"
with open(path, 'w') as outfile:
    json.dump(curation, outfile, ensure_ascii=False,
                indent=4, sort_keys=True, separators=(',', ': '))