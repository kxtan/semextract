from typing import Tuple
from spacy import Token

class DepenParseBase:
    """Base Class for dependency parsing
    """

    def __init__(self):
        """Contructor
        """
        self.initialize_vars()

    def initialize_vars(self):
        """Inititialize object variables
        """
        self.NEGATION = "not "
        self.SUBJECTS = ["nsubj", "nsubjpass", "csubj", "csubjpass", "agent", "expl"]
        self.OBJECTS = ["dobj", "dative", "attr", "oprd"]
        self.ADJECTIVES = [
            "acomp", "advcl", "advmod", "amod", 
            "appos", "nn", "nmod", "ccomp", "complm",
            "hmod", "infmod", "xcomp", "rcmod", "poss","possessive"
        ]
        self.COMPOUNDS = ["compound"]
        self.PREPOSITIONS = ["prep"]

    def get_subs_from_conjunctions(self, subs:list) -> list:
        """Search for more subjects given list of subjects

        Args:
            subs (list): list of identified subjects

        Returns:
            list: list of expanded subjects
        """
        
        moreSubs = []

        for sub in subs:

            rights = list(sub.rights)
            rightDeps = {tok.lower_ for tok in rights}
            if "and" in rightDeps:
                moreSubs.extend([
                    tok for tok in rights if tok.dep_ in self.SUBJECTS or tok.pos_ == "NOUN"
                ])
                if len(moreSubs) > 0:
                    moreSubs.extend(self.get_subs_from_conjunctions(moreSubs))

        return moreSubs

    def get_objs_from_conjunctions(self, objs:list) -> list:
        """Search for more objects given list of objects

        Args:
            objs (list): list of identified objects

        Returns:
            list: list of expanded objects
        """

        moreObjs = []
        
        for obj in objs:

            rights = list(obj.rights)
            rightDeps = {tok.lower_ for tok in rights}
            if "and" in rightDeps:
                moreObjs.extend([
                    tok for tok in rights if tok.dep_ in self.OBJECTS or tok.pos_ == "NOUN"
                ])
                if len(moreObjs) > 0:
                    moreObjs.extend(self.get_objs_from_conjunctions(moreObjs))
        
        return moreObjs

    def get_verbs_from_conjunctions(self, verbs:list) -> list:
        """Search for more verbs given list of verbs

        Args:
            verbs (list): list of identified verbs

        Returns:
            list: list of expanded verbs
        """
        
        moreVerbs = []

        for verb in verbs:

            rightDeps = {tok.lower_ for tok in verb.rights}
            if "and" in rightDeps:
                moreVerbs.extend([tok for tok in verb.rights if tok.pos_ == "VERB"])
                if len(moreVerbs) > 0:
                    moreVerbs.extend(self.get_verbs_from_conjunctions(moreVerbs))

        return moreVerbs

    def find_subs(self, tok:Token) -> Tuple[list, bool]:
        """Find subjects from given token

        Args:
            tok (Token): input spacy token

        Returns:
            Tuple[list, bool]: list of subjects, bool representing if verb is negated
        """

        head = tok.head

        while head.pos_ != "VERB" and head.pos_ != "NOUN" and head.head != head:
            head = head.head

        if head.pos_ == "VERB":
            subs = [tok for tok in head.lefts if tok.dep_ == "SUB"]
            if len(subs) > 0:
                verbNegated = self.is_negated(head)
                subs.extend(self.get_subs_from_conjunctions(subs))
                return subs, verbNegated
            elif head.head != head:
                return self.find_subs(head)
        elif head.pos_ == "NOUN":
            return [head], self.is_negated(tok)
        
        return [], False

    def is_negated(self, tok:Token) -> bool:
        """Determine if token is being negated

        Args:
            tok (Token): spacy token

        Returns:
            bool: if the token is negated
        """

        negations = {"no", "not", "n't", "never", "none"}

        for dep in list(tok.lefts) + list(tok.rights):
            if dep.lower_ in negations:
                return True

        return False

    def find_sv(self, tokens:list) -> list:
        """find subject, verb pairs given a list of tokens

        Args:
            tokens (list): list of spacy tokens

        Returns:
            list: list of subject verb pairs
        """

        svs = []
        verbs = [tok for tok in tokens if tok.pos_ == "VERB"]

        for v in verbs:
            subs, verbNegated = self.get_all_subs(v)
            if len(subs) > 0:
                for sub in subs:
                    svs.append((sub.orth_, "!" + v.orth_ if verbNegated else v.orth_))

        return svs

    def get_objs_from_prepositions(self, deps:list) -> list:
        """find objects to the right of given prepositions

        Args:
            deps (list): list of prepositions

        Returns:
            list: objects to the right of given prepositions
        """

        objs = []
        for dep in deps:
            if dep.pos_ == "ADP" and dep.dep_ == "prep":
                objs.extend(
                    [tok for tok in dep.rights if tok.dep_  in self.OBJECTS or 
                    (tok.pos_ == "PRON" and tok.lower_ == "me")]
                )
        return objs

    def get_adjectives(self, toks:list) -> list:
        """find tokens with adjectives in the given list of tokens

        Args:
            toks (list): list of spacy tokens

        Returns:
            list: return list of tokens with adjectives
        """

        toks_with_adjectives = []
        
        for tok in toks:
            adjs = [left for left in tok.lefts if left.dep_ in self.ADJECTIVES]
            adjs.append(tok)
            adjs.extend([right for right in tok.rights if tok.dep_ in self.ADJECTIVES])
            #tok_with_adj = " ".join([adj.lower_ for adj in adjs])
            toks_with_adjectives.extend(adjs)

        return toks_with_adjectives

    def get_objs_from_attrs(self, deps:list) -> Tuple[Token, list]:
        """Obtain objects to the right of verbs

        Args:
            deps (list): list of dependencies/attrs

        Returns:
            Tuple[Token, list]: verb, list of objects the verb is addressing
        """
        
        for dep in deps:
        
            if dep.pos_ == "NOUN" and dep.dep_ == "attr":

                verbs = [tok for tok in dep.rights if tok.pos_ == "VERB"]
        
                if len(verbs) > 0:

                    for v in verbs:
                        rights = list(v.rights)
                        objs = [tok for tok in rights if tok.dep_ in self.OBJECTS]
                        objs.extend(self.get_objs_from_prepositions(rights))
                        if len(objs) > 0:
                            return v, objs
        
        return None, None

    def get_obj_from_xcomp(self, deps):
        for dep in deps:
            if dep.pos_ == "VERB" and dep.dep_ == "xcomp":
                v = dep
                rights = list(v.rights)
                objs = [tok for tok in rights if tok.dep_ in self.OBJECTS]
                objs.extend(self.get_objs_from_prepositions(rights))
                if len(objs) > 0:
                    return v, objs
        return None, None

    def get_all_subs(self, v):
        verbNegated = self.is_negated(v)
        subs = [tok for tok in v.lefts if tok.dep_ in self.SUBJECTS and tok.pos_ != "DET"]
        if len(subs) > 0:
            subs.extend(self.get_subs_from_conjunctions(subs))
        else:
            foundSubs, verbNegated = self.find_subs(v)
            subs.extend(foundSubs)
        return subs, verbNegated

    def get_all_objs_from_adj(self, adj):
        left_rights = list(adj.rights) + list(adj.lefts)
        objs = [tok for tok in left_rights if tok.dep_ in self.OBJECTS]

        return objs

    def chain_adjectives_before_nouns(self, toks):
        adjs = []
        nouns = []
        final_adj_pos = 0

        for i in range(len(toks)):
            if toks[i].pos_ == "ADJ":
                adjs.append(toks[i])
                final_adj_pos = i
        
        for i in range(final_adj_pos, len(toks)):
            if toks[i].pos_ == "NOUN":
                nouns.append(toks[i])

        return adjs, nouns 

    def get_all_objs(self, v):
        # rights is a generator
        rights = list(v.rights)
        objs = [tok for tok in rights if tok.dep_ in self.OBJECTS]
        objs.extend(self.get_objs_from_prepositions(rights))

        potentialNewVerb, potentialNewObjs = self.get_obj_from_xcomp(rights)
        if potentialNewVerb is not None and potentialNewObjs is not None and len(potentialNewObjs) > 0:
            objs.extend(potentialNewObjs)
            v = potentialNewVerb
        if len(objs) > 0:
            objs.extend(self.get_objs_from_conjunctions(objs))
        return v, objs

    def get_all_objs_with_adjectives(self, v):
        # rights is a generator
        rights = list(v.rights)
        objs = [tok for tok in rights if tok.dep_ in self.OBJECTS]

        if len(objs)== 0:
            objs = [tok for tok in rights if tok.dep_ in self.ADJECTIVES]

        objs.extend(self.get_objs_from_prepositions(rights))

        potentialNewVerb, potentialNewObjs = self.get_obj_from_xcomp(rights)
        if potentialNewVerb is not None and potentialNewObjs is not None and len(potentialNewObjs) > 0:
            objs.extend(potentialNewObjs)
            v = potentialNewVerb
        if len(objs) > 0:
            objs.extend(self.get_objs_from_conjunctions(objs))
        return v, objs

    def find_svos(self, tokens):
        svos = []
        verbs = [tok for tok in tokens if tok.pos_ == "VERB" and tok.dep_ != "aux"]
        for v in verbs:
            subs, verbNegated = self.get_all_subs(v)
            # hopefully there are subs, if not, don't examine this verb any longer
            if len(subs) > 0:
                v, objs = self.get_all_objs(v)
                for sub in subs:
                    for obj in objs:
                        objNegated = self.is_negated(obj)
                        svos.append(
                            (sub.lower_, "!" + v.lower_ if verbNegated or objNegated 
                            else v.lower_, obj.lower_)
                        )
        return svos

    def find_svaos(self, tokens):
        svos = []
        verbs = [tok for tok in tokens if tok.pos_ == "VERB"] 
        
        for v in verbs:
            subs, verbNegated = self.get_all_subs(v)
            # hopefully there are subs, if not, don't examine this verb any longer
            if len(subs) > 0:
                v, objs = self.get_all_objs_with_adjectives(v)
                for sub in subs:
                    for obj in objs:
                        objNegated = self.is_negated(obj)
                        obj_desc_tokens = self.generate_left_right_adjectives(obj)
                        sub_compound = self.generate_sub_compound(sub)
                        svos.append((" ".join(tok.lower_ for tok in sub_compound), 
                        "!" + v.lower_ if verbNegated or objNegated else v.lower_, 
                        " ".join(tok.lower_ for tok in obj_desc_tokens)))
        return svos

    def generate_sub_compound(self, sub):
        sub_compunds = []
        for tok in sub.lefts:
            if tok.dep_ in self.COMPOUNDS:
                sub_compunds.extend(self.generate_sub_compound(tok))
        sub_compunds.append(sub)
        for tok in sub.rights:
            if tok.dep_ in self.COMPOUNDS:
                sub_compunds.extend(self.generate_sub_compound(tok))
        return sub_compunds

    def generate_left_right_adjectives(self, obj):
        obj_desc_tokens = []
        for tok in obj.lefts:
            if tok.dep_ in self.ADJECTIVES:
                obj_desc_tokens.extend(self.generate_left_right_adjectives(tok))
        obj_desc_tokens.append(obj)

        for tok in obj.rights:
            if tok.dep_ in self.ADJECTIVES:
                obj_desc_tokens.extend(self.generate_left_right_adjectives(tok))
        return obj_desc_tokens