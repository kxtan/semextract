import pandas as pd

def df_from_triples_dict(triples_dict:dict) -> pd.DataFrame:
    """Converts triples dictionary to pandas dataframe

    Args:
        triples_dict (dict): triples dictionary

    Returns:
        pd.DataFrame: pandas dataframe of semantic triples
    """

    key_lst = []
    subject_lst = []
    predicate_lst = []
    object_lst = []

    for key, triples_lst in triples_dict.items():

        for triples in triples_lst:
            key_lst.append(key)
            subject_lst.append(triples[0])
            predicate_lst.append(triples[1])
            object_lst.append(triples[2])

    dct = {
        "id" : key_lst,
        "subject" : subject_lst,
        "predicate" : predicate_lst,
        "object" : object_lst
    }

    return pd.DataFrame.from_dict(dct)