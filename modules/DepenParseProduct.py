from modules.DepenParseBase import DepenParseBase

class DepenParseProduct(DepenParseBase):
    """Dependancy parsing that is more suited for product based texts

    Args:
        DepenParseBase ([type]): Base class for SVO extraction
    """

    def __init__(self):
        super().__init__()

    def triplets_with_subs_and_objs(self, product, verb, verb_negated, subs, objs):
        res = []
        for sub in subs:
            for obj in objs:
                objNegated = self.is_negated(obj)
                obj_desc_tokens = self.generate_left_right_adjectives(obj)
                sub_compound = self.generate_sub_compound(sub)
                negation = ""
                if verb_negated or objNegated:
                    negation = self.NEGATION
                _subject = " ".join(tok.lower_ for tok in sub_compound)

                predicate = f"{negation}{verb.lower_}"
                if _subject and (not _subject.isspace()): 
                    predicate = f"{_subject} {negation}{verb.lower_}"
                    
                _object = " ".join(tok.lower_ for tok in obj_desc_tokens)
                res.append((product, predicate, _object))
        return res

    def triplets_with_subs(self, product, verb, verb_negated, subs):
        res = []
        for sub in subs:
            subNegated = self.is_negated(sub)
            sub_compound = self.generate_sub_compound(sub)
            _subject = " ".join(tok.lower_ for tok in sub_compound)

            negation = ""
            if verb_negated or subNegated:
                negation = self.NEGATION
            predicate = f"{negation}{verb.lower_}"
            res.append((product, predicate, _subject))
        return res

    def triplets_with_objs(self, product, verb, verb_negated, objs):
        res = []
        for obj in objs:
            objNegated = self.is_negated(obj)
            obj_desc_tokens = self.generate_left_right_adjectives(obj)
            
            negation = ""
            if verb_negated or objNegated:
                negation = self.NEGATION
            predicate = f"{negation}{verb.lower_}"

            _object = " ".join(tok.lower_ for tok in obj_desc_tokens)
            res.append((product, predicate, _object))
        return res

    def triplets_without_verbs(self, product, tokens):
        res = []
        reasons = []
        adjs, nouns = self.chain_adjectives_before_nouns(tokens)
        if adjs and nouns:
            predicate = " ".join(tok.lower_ for tok in adjs)
            _object = " ".join(tok.lower_ for tok in nouns)
            #print(f"case 4 : {(product, predicate, _object)}")
            res.append((product, predicate, _object))
        else:
            reasons.append("missing verbs, adj and nouns")
            
        return res, reasons
    
    def triplets_with_verbs(self, product, verbs):
        res = []
        reasons = []
        for v in verbs:
            subs, verb_negated = self.get_all_subs(v)    
            if subs:
                #subject exists
                v, objs = self.get_all_objs_with_adjectives(v)
                if objs:
                    #subject and object exist
                    res += self.triplets_with_subs_and_objs(product, v, verb_negated, subs, objs)
                else:
                    #only subject exist but not object
                    res += self.triplets_with_subs(product, v, verb_negated, subs)
            else:
                #only object exist but not subject
                _, objs = self.get_all_objs_with_adjectives(v)
                if objs:
                    res += self.triplets_with_objs(product, v, verb_negated, objs)
                else:
                    reasons.append(f"missing object and subject for verb {v}")
        return res, reasons

    def product_triplets(self, product, tokens):
        svos = []
        reasons = []
        verbs = [tok for tok in tokens if tok.pos_ == "VERB"] 
        if verbs:
            svo, reasons = self.triplets_with_verbs(product, verbs)
            svos += svo
        else:
            svo, reasons = self.triplets_without_verbs(product, tokens)
            svos += svo

        return svos, reasons