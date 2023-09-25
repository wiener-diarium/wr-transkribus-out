import glob
import os
import json
from acdh_tei_pyutils.tei import TeiReader
from icecream import ic


files = glob.glob("./tei/*.xml")
ic(len(files))

with open("data.jsonl", "w", encoding="utf-8") as f:
    for x in files:
        _, tail = os.path.split(x)
        item = {}
        doc = TeiReader(x)
        body_node = doc.any_xpath(".//tei:body")[0]
        dr_id = doc.any_xpath(".//tei:title[@type='main']/text()")[0].split(" ")[-1]
        ic(dr_id)
        item["id"] = dr_id
        item["doc_id"] = int(tail.replace(".xml", ""))
        item["text"] = (
            " ".join("".join(body_node.itertext()).split())
            .replace("\n", " ")
            .replace("¬ ", "")
            .replace("= ", "")
        )
        f.write(json.dumps(item, ensure_ascii=False) + "\n")
