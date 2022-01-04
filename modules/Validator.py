class Meta:

    def __init__(self, identifier:str, source_tokens:list, triples_list:list) -> None:
        """Contructor for validation meta class

        Args:
            identifier (str): identifier for validation
            source_tokens (list): source tokens to compare against
            triples_list (list): list of semantic triples
        """
        self.identifier = identifier
        self.source_tokens = source_tokens
        self.triples_list = triples_list
    
    def count_match(self) -> int:
        """count matching tokens between semantic triples and source tokens

        Returns:
            int: amount of matches
        """

        self.matching_counts = 0
        
        for triples in self.triples_list:
            for item in triples:
                if item in self.source_tokens:
                    self.matching_counts += 1

        return self.matching_counts 
    
    def generate_match_pct(self) -> float:
        """Generate matching percentage between triples and source

        Returns:
            float: matching percentage
        """
        source_len = len(self.source_tokens)
        if source_len > 0: #division by zero check
            self.match_pct = self.matching_counts/source_len
        return self.match_pct


class TriplesValidator:
    """Validation class for knowledge graphs
    """

    def naive_validation(triples_dict:dict, source_dict:dict) -> dict: 
        """Naive validation of semantic triples

        Args:
            triples_dict (dict): [description]
            source_dict (dict): [description]

        Returns:
            dict: [description]
        """

        results_collection = []

        for triples_key, triples_lst in triples_dict.items():
            #Assumption: one key might have many triples
            if triples_key in source_dict:
                meta = Meta(triples_key, source_dict[triples_key], triples_lst)
                meta.count_match()

                results_collection.append(meta)

        return results_collection

        