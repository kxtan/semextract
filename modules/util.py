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


def triples_dict_from_df(triples_df:pd.DataFrame, 
        identifier="id",
        subject="subject",
        predicate="predicate",
        obj="object"
    ) -> dict:
    """Converts semantic triples (ST) df to dictionary representation

    Args:
        triples_df (pd.DataFrame): pandas dataframe of ST
        identifier (str, optional): identifier for ST. Defaults to "id".
        subject (str, optional): subject of ST. Defaults to "subject".
        predicate (str, optional): predicate of ST. Defaults to "predicate".
        obj (str, optional): object of ST. Defaults to "object".

    Returns:
        dict: dictionary representation of semantic triples
    """

    triples_dict = {}

    id_lst = triples_df[identifier].values
    subject_lst = triples_df[subject].values
    predicate_lst = triples_df[predicate].values
    obj_lst = triples_df[obj].values

    zipped = zip(id_lst, subject_lst, predicate_lst, obj_lst)

    for id_value, sub, pred, obj in zipped:
        
        triples = (sub, pred, obj)

        if id_value in triples_dict:
            triples_dict[id_value].append(triples)
        else:
            triples_dict[id_value] = [triples]

    return triples_dict