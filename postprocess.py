import os
import glob
import jinja2
import json
import requests
import lxml.etree as ET
from acdh_tei_pyutils.tei import TeiReader
from icecream import ic

templateLoader = jinja2.FileSystemLoader(searchpath="./templates")
templateEnv = jinja2.Environment(loader=templateLoader)
template = templateEnv.get_template("tei.j2")


files = glob.glob("./tei/*.xml")
out_dir = "tmp"
os.makedirs(out_dir, exist_ok=True)


for x in files:
    doc = TeiReader(x)
    dr_id = doc.any_xpath(".//tei:title[@type='main']/text()")[0].split(" ")[-1]
    file_name = f"wr_{dr_id}.xml"
    header = (
        ET.tostring(doc.any_xpath(".//tei:teiHeader")[0])
        .decode("utf-8")
        .replace('xmlns="http://www.tei-c.org/ns/1.0"', "")
    )
    facs = (
        ET.tostring(doc.any_xpath(".//tei:facsimile")[0])
        .decode("utf-8")
        .replace('xmlns="http://www.tei-c.org/ns/1.0"', "")
    )
    pages = []
    for i, y in enumerate(doc.any_xpath(".//tei:pb"), start=1):

        facs_id = f"#facs_{i}"
        page = {
            "div_id": f"wr_{dr_id}__{i:0>2}",
            "pb": ET.tostring(y)
            .decode("utf-8")
            .replace('xmlns="http://www.tei-c.org/ns/1.0"', ""),
            "page_id": f"#facs_{i}",
            "abs": [],
        }
        for ab in doc.any_xpath(f".//tei:ab[contains(@facs, '{facs_id}')]"):
            page["abs"].append(
                ET.tostring(ab)
                .decode("utf-8")
                .replace('xmlns="http://www.tei-c.org/ns/1.0"', "")
            )
        pages.append(page)
    with open(f"{os.path.join(out_dir, file_name)}", "w", encoding="utf-8") as f:
        f.write(template.render({"header": header, "facs": facs, "pages": pages}))

for x in glob.glob(f"{out_dir}/*.xml"):
    doc = TeiReader(x)
    doc.tree_to_file(x)
