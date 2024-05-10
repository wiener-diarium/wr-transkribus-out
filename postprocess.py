import os
import glob
# import jinja2
import json
# import lxml.etree as ET
from acdh_tei_pyutils.tei import TeiReader
# from icecream import ic
from tqdm import tqdm
import zipfile

# templateLoader = jinja2.FileSystemLoader(searchpath="./templates")
# templateEnv = jinja2.Environment(loader=templateLoader)
# template = templateEnv.get_template("tei.j2")


# files = glob.glob("./tei/*.xml")
input_dir = "tei"
out_dir = "html"
# os.makedirs(out_dir, exist_ok=True)


# print(f"upconverting {len(files)} transkribus export TEIs and saving them into {out_dir}")
# for x in tqdm(files, total=len(files)):
#     doc = TeiReader(x)
#     dr_id = doc.any_xpath(".//tei:title[@type='main']/text()")[0].split(" ")[-1]
#     file_name = f"wr_{dr_id}.xml"
#     header = (
#         ET.tostring(doc.any_xpath(".//tei:teiHeader")[0])
#         .decode("utf-8")
#         .replace('xmlns="http://www.tei-c.org/ns/1.0"', "")
#     )
#     facs = (
#         ET.tostring(doc.any_xpath(".//tei:facsimile")[0])
#         .decode("utf-8")
#         .replace('xmlns="http://www.tei-c.org/ns/1.0"', "")
#     )
#     pages = []
#     for i, y in enumerate(doc.any_xpath(".//tei:pb"), start=1):

#         facs_id = f"#facs_{i}"
#         page = {
#             "div_id": f"wr_{dr_id}__{i:0>2}",
#             "pb": ET.tostring(y)
#             .decode("utf-8")
#             .replace('xmlns="http://www.tei-c.org/ns/1.0"', ""),
#             "page_id": f"#facs_{i}",
#             "abs": [],
#         }
#         for ab in doc.any_xpath(f".//tei:ab[contains(@facs, '{facs_id}')]"):
#             page["abs"].append(
#                 ET.tostring(ab)
#                 .decode("utf-8")
#                 .replace('xmlns="http://www.tei-c.org/ns/1.0"', "")
#             )
#         pages.append(page)
#     with open(f"{os.path.join(out_dir, file_name)}", "w", encoding="utf-8") as f:
#         f.write(template.render({"header": header, "facs": facs, "pages": pages}))

# for x in glob.glob(f"{out_dir}/*.xml"):
#     doc = TeiReader(x)
#     doc.tree_to_file(x)

data_save_path = os.path.join(out_dir, "data.jsonl")
print(f"creating JSONL for each page from upconverted teis and saving it as {data_save_path}")
counter = 0
with open(data_save_path, "w", encoding="utf-8") as f:
    for x in tqdm(glob.glob(f"{input_dir}/*.xml")):
        _, tail = os.path.split(x)
        item = {}
        doc = TeiReader(x)
        date = doc.any_xpath(".//tei:title[@type='main']/text()")[0].split(" ")[-1]
        pb = doc.any_xpath(".//tei:pb")
        dr_id = f"wr_{date}__01"
        full_text = doc.any_xpath(".//tei:body/tei:div")
        item["id"] = dr_id
        item["text"] = (
            " ".join(" ".join("".join(p.itertext()).split()) for p in full_text)
            .replace("\n", " ")
            .replace("¬ ", "")
            .replace("= ", "")
            .replace("=", "")
        )
        counter += 1
        f.write(json.dumps(item, ensure_ascii=False) + "\n")
        # for page in pb:
        #     facs = page.attrib["facs"]
        #     nr = page.attrib["n"]
        #     dr_id = f"wr_{date}__{nr:0>2}"
        #     full_text = doc.any_xpath(".//tei:body/tei:div[tei:*[contains(@facs, '{}')]]".format(facs))
        #     item["id"] = dr_id
        #     item["text"] = (
        #         " ".join(" ".join("".join(p.itertext()).split()) for p in full_text)
        #         .replace("\n", " ")
        #         .replace("¬ ", "")
        #         .replace("= ", "")
        #         .replace("=", "")
        #     )
        #     counter += 1
        #     f.write(json.dumps(item, ensure_ascii=False) + "\n")

print(f"done, created {data_save_path} for {counter} pages. Creating zip archive...")

with zipfile.ZipFile("html/data.zip", "w", zipfile.ZIP_DEFLATED) as z:
    z.write(data_save_path, arcname=os.path.basename(data_save_path))
print(f"done, created html/data.zip for {data_save_path}")
os.remove(data_save_path)
print(f"removed {data_save_path}")
