import pickle
import xml.etree.ElementTree as ET

from hippogym_app.preprocess import get_one_pair_regresor_data


# def get_score_change(minutiae_file_path, output_file):
def get_score_change(minutiae_file_path):
    data, minutiae = get_one_pair_regresor_data(minutiae_file_path)
    with open("regresor.pkl", "rb") as regresor_file:
        clf = pickle.load(regresor_file)
    rv = list(zip(minutiae, clf.predict(data)))
    # export_xml(minutiae_file_path, output_file, rv)
    return rv


def export_xml(source_file, output_file, data):
    root = ET.Element("MinutiaeListWithScoreChange", {"source_file": source_file})

    for m, sc in data:
        file_root = ET.Element(
            "Minutia",
            {
                "X": str(m[0]),
                "Y": str(m[1]),
                "Angle": m[2],
                "Type": m[3],
                "score_change": str(sc),
            },
        )
        root.append(file_root)

    ET.indent(root, space="\t")
    ET.ElementTree(root).write(output_file)
