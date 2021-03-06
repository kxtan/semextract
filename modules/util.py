import pandas as pd
import re
from nltk.corpus import stopwords
from nltk.stem import PorterStemmer


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


def simple_preprocess(text_list:list) -> list:
    """Performs simple preprocessing on the list of texts

    Args:
        text_list (list): list of texts

    Returns:
        list: list of preprocessed texts in tokens format
    """
    text_list = [x.lower() for x in text_list]
    text_list = [re.sub(r'[^\w]', ' ', x) for x in text_list]
    text_list = [x.split() for x in text_list]

    return text_list


def tokens_intersect(id_list:list, source_tokens_list:list, target_tokens_list:list, threshold=3) -> list:
    """Check if source tokens (to extract semantic triples from) has sufficient amount of 
    matching tokens from the target (extract "gold standard")

    Args:
        id_list (list): list of id
        source_tokens_list (list): source tokens
        target_tokens_list (list): target tokens
        threshold (int, optional): valid threshold. Defaults to 3.

    Returns:
        list: list of valid ids
    """

    valid_id_list = []

    for _id, source_tokens, target_tokens in zip(id_list, source_tokens_list, target_tokens_list):

        #make tokens unique:
        uniq_source_tokens = list(set(source_tokens))
        uniq_target_tokens = list(set(target_tokens))

        count = 0

        for source_token in uniq_source_tokens:
            if source_token in uniq_target_tokens:
                count += 1
            if count > threshold:
                valid_id_list.append(_id)
                break
    
    return valid_id_list


def remove_stopwords(tokens_list:list) -> list:
    """Remove stopwords from list of tokens. 

    Args:
        tokens_list (list): list containing token lists

    Returns:
        list: list of token lists with stop words removed
    """
    return_lst = []
    stopw = stopwords.words('english')

    for lst in tokens_list:
        return_lst.append([word for word in lst if word not in stopw])

    return return_lst


def remove_numbers(tokens_list:list) -> list:
    """Remove numbers from list of tokens.

    Args:
        tokens_list (list): list of tokens

    Returns:
        list: list of tokens with numbers removed
    """
    return_lst = []

    for lst in tokens_list:
        return_lst.append([s for s in lst if not s.isdigit()])

    return return_lst


def remove_single_character(tokens_list:list) -> list:
    """Remove single characters from list of tokens

    Args:
        tokens_list (list): list of tokens

    Returns:
        list: list of tokens with single characters removed
    """
    return_lst = []

    for lst in tokens_list:
        return_lst.append([s for s in lst if len(s) > 1])

    return return_lst


def stem_words(tokens_list:list) -> list:
    """Stem words from list of tokens

    Args:
        tokens_list (list): list of tokens

    Returns:
        list: list of tokens with stemmed words
    """
    return_lst = []
    stemmer = PorterStemmer()

    for lst in tokens_list:
        return_lst.append([stemmer.stem(s) for s in lst])

    return return_lst


def stem_triples(df:pd.DataFrame, id_col="id", 
    sbj_col="subject", pred_col="predicate", 
    obj_col="object", negation="!") -> pd.DataFrame:
    """Stem words from triples df

    Args:
        df (pd.DataFrame): semantic triples dataframe
        id_col (str, optional): id column of df. Defaults to "id".
        sbj_col (str, optional): subject column of df. Defaults to "subject".
        pred_col (str, optional): predicate column of df. Defaults to "predicate".
        obj_col (str, optional): object column of df. Defaults to "object".
        negation (str, optional): negation substring in predicate. Defaults to "!".

    Returns:
        pd.DataFrame: [description]
    """

    stemmer = PorterStemmer()
    sbj_lst = df[sbj_col].tolist()
    predicate_lst = df[pred_col].tolist()
    obj_lst = df[obj_col].tolist() 
    
    stem_sbj_lst = []
    stem_predicate_lst = []
    stem_obj_lst = [] 
    
    for sbj, pred, obj in zip(sbj_lst, predicate_lst, obj_lst):
        negation_removed = False
        if negation in pred:
            pred = pred.replace(negation,'')
            negation_removed = True

        stemmed_pred = stemmer.stem(pred)
        if negation_removed:
            stemmed_pred = f"{negation}{stemmed_pred}"
        stem_predicate_lst.append(stemmer.stem(stemmed_pred))
        
        stem_sbj_lst.append(stemmer.stem(sbj))
        stem_obj_lst.append(stemmer.stem(obj))
        
    output_df = pd.DataFrame(
        {
            id_col : df[id_col].tolist(),
            sbj_col : stem_sbj_lst,
            pred_col : stem_predicate_lst,
            obj_col : stem_obj_lst,
        }
    )
    
    return output_df