import time
from projectmir.xmldocument_1 import XMLDocument


def find_identifier_definition(document_path):
    start_time = time.time()
    doc = XMLDocument(document_path)
    print(
        "elapsed time : {0:.7f} seconds ---".format(time.time() - start_time))

    doc.processor()
    print(
        "elapsed time : {0:.7f} seconds ---".format(time.time() - start_time))

    doc.extract_identifiers()
    print(
        "elapsed time : {0:.7f} seconds ---".format(time.time() - start_time))

    doc.extract_sentences()
    print(
        "elapsed time : {0:.7f} seconds ---".format(time.time() - start_time))

    doc.POS_tagging()
    print(
        "elapsed time : {0:.7f} seconds ---".format(time.time() - start_time))

    doc.extract_noun_phrases()
    print("extract_noun_phrases",
          "elapsed time : {0:.7f} seconds ---".format(time.time() - start_time),
          sep="\n")

    doc.pattern_based_extract_description()
    print(
        "elapsed time : {0:.7f} seconds ---".format(time.time() - start_time))

    return doc


def find_definition_candidates(doc):
    identifiers = doc.identifiers
