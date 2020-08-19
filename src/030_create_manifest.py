import urllib.request
from bs4 import BeautifulSoup
import csv
from time import sleep
import pandas as pd
import json
import urllib.request
import os
from PIL import Image
import yaml
import requests

def getCanvases(manifest):
    mdata = requests.get(manifest).json()
    canvases = mdata["sequences"][0]["canvases"]

    map = {}
    for i in range(len(canvases)):
        canvas = canvases[i]
        map[canvas["images"][0]["resource"]["service"]["@id"]] = canvas["@id"]

    return {
        "canvases": map, 
        "label": mdata["label"]
    }

path = "data/sati_20200324.xlsx"

df_item = pd.read_excel(path, sheet_name="Sheet2", header=None, index_col=None)

r_count = len(df_item.index)

label_map = {}

for i in range(0, 20):
    label = df_item.iloc[0, i]
    label_map[i] = label

selections = {}

for j in range(1, r_count):

    print(str(j)+"/"+str(r_count))

    metadata = []    

    for i in range(1, 20):
        value = df_item.iloc[j, i]

        if not pd.isnull(value) and value != 0:
            label = label_map[i]
            values = value.split(";")
            for value in values:
                value = str(value).strip()
                if value != "":
                    metadata.append({
                        "label" : label,
                        "value" : value
                    })

    image_uri = df_item.iloc[j, 21]

    image_api = image_uri.split(".tif")[0]+".tif"

    i_sp = image_uri.split("/")

    id = i_sp[5]
    xywh = i_sp[7]

    manifest = "https://dzkimgs.l.u-tokyo.ac.jp/iiif/zuzoubu/"+id+"/manifest.json"

    if manifest not in selections:
        mr_data = getCanvases(manifest)
        selections[manifest] = {
            "members" : [],
            "canvases" : mr_data["canvases"],
            "label" : mr_data["label"],
        }

    selection = selections[manifest]

    member = {
        "@id" : selection["canvases"][image_api] + "#xywh="+xywh,
        "@type" : "sc:Canvas",
        "label" : df_item.iloc[j, 0],
        "metadata" : metadata,
        "thumbnail" : image_uri
    }

    selection["members"].append(member)

new_ss = []

count = 1
for manifest in selections:
    selection = selections[manifest]

    new_s = {
        "@id" : "https://nakamura196.github.io/sati/iiif/curaiton.json/range"+str(count),
        "@type": "sc:Range",
        "members" : selection["members"],
        "within" : {
            "@id" : manifest,
            "@type" : "sc:Manifest",
            "label" : selection["label"]
        }
    }

    new_ss.append(new_s)

    count += 1

curation = {
    "@context": [
        "http://iiif.io/api/presentation/2/context.json",
        "http://codh.rois.ac.jp/iiif/curation/1/context.json"
    ],
    "@type": "cr:Curation",
    "@id": "https://nakamura196.github.io/sati/iiif/curaiton.json",
    "label" : "SAT大正蔵図像DB",
    "selections" : new_ss,
    "viewingHint" : "grid",
    "description" : "SAT大正蔵図像DB・機械学習用データセット",
    "thumbnail" : "https://21dzk.l.u-tokyo.ac.jp/SAT/image/image01.jpg"
}

f2 = open("../docs/iiif/curation.json", 'w')
json.dump(curation, f2, ensure_ascii=False, indent=4,
            sort_keys=True, separators=(',', ': '))
