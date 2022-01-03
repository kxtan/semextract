from DepenParseBase import DepenParseBase
import spacy
import subprocess

class Triples:
    """Extract semantic triples for knowledge graph construction
    """

    def __init__(self, trained_model="en_core_web_sm") -> None:
        """Constructor

        Args:
            trained_model (str, optional): trained model to load from spacy. Defaults to "en_core_web_sm".
        """
        self.load_spacy_model(trained_model)

    def load_spacy_model(self, trained_model:str) -> None:
        """Loads trained spacy model

        Args:
            trained_model (str): model to load from spacy (https://spacy.io/usage/models)
        """

        if not spacy.util.is_package(trained_model):
            subprocess.run([f"python -m spacy download {trained_model}"])

        self.nlp_model = spacy.load(trained_model)

    def semantic_triples(self, identifier_lst:list, text_lst:list) -> dict:
        """Generate semantic triples from unstructured texts

        Args:
            identifier_lst (list): identifier to individual texts
            text_lst (list): texts to extract semantic triples

        Returns:
            dict: dictionary of identifiers(key) and semantic triples(values)
        """

        parser = DepenParseBase()
        output_dict = {}

        for identifier, text in zip(identifier_lst, text_lst):
            if text is not None:
                tokens = self.nlp_model(text)
                svo_lst = parser.find_svos(tokens)
                output_dict[identifier] = svo_lst

        return output_dict