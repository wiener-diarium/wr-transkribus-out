import os
import glob
import requests
from icecream import ic
from saxonche import PySaxonProcessor
from transkribus_utils.transkribus_utils import ACDHTranskribusUtils

url = "https://wiener-diarium.github.io/wr-status/data.json"
user = os.environ.get("TR_USER")
pw = os.environ.get("TR_PW")
XSLT = "https://csae8092.github.io/page2tei/page2tei-0.xsl"
METS_DIR = "./mets"
TEI_DIR = "./tei"
os.makedirs(METS_DIR, exist_ok=True)
os.makedirs(TEI_DIR, exist_ok=True)

transkribus_client = ACDHTranskribusUtils(
    user=user,
    password=pw,
    transkribus_base_url="https://transkribus.eu/TrpServer/rest"
)

data = requests.get(url).json()

ids = set()
for x in data:
    if x["doc_transcribed"]:
        ids.add(x["col_id"])
ids = list(ids)
ic(ids)
ic(len(ids))

for y in ids:
    col_id = y
    print(f"processing collection: {col_id}")
    mpr_docs = transkribus_client.collection_to_mets(col_id,
                                                     file_path="./mets")
    ic(f"{METS_DIR}/{col_id}*.xml")
    files = glob.glob(f"{METS_DIR}/{col_id}/*_mets.xml")
    for x in files:
        tail = os.path.split(x)[-1]
        doc_id = tail.split("_")[0]
        tei_file = f"{doc_id}.xml"
        ic(f"transforming mets: {x} to {tei_file}")
        with PySaxonProcessor(license=False) as proc:
            xsltproc = proc.new_xslt30_processor()
            xsltproc.set_parameter("combine",
                                   proc.make_boolean_value(True))
            xsltproc.set_parameter("ab", proc.make_boolean_value(True))
            document = proc.parse_xml(xml_file_name=x)
            executable = xsltproc.compile_stylesheet(stylesheet_file=XSLT)
            output = executable.transform_to_string(xdm_node=document)
            output = output.replace(' type=""', "")
            with open(os.path.join(TEI_DIR, tei_file), "w") as f:
                f.write(output)
