# -*- coding: utf-8 -*-
from karura.core.insight import Insight


class CategoricalItemInsight(Insight):

    def __init__(self):
        super().__init__()
        self.index.as_column_check()
    
    def is_applicable(self, dfe):
        self.init_description()
        ts = self.get_insight_targets(dfe)
        if len(ts) > 0:
            self.description = {
                "ja": "{} は分類項目のようです。分類項目として処理してよいですか？".format(ts),
                "en": "{} seems to be categorical column. ok?".format(ts)
            }
            return True
        else:
            return False

    def adopt(self, dfe, interpreted=None):
        if isinstance(interpreted, bool) and not interpreted:
            return 0
        targets = self.get_insight_targets(dfe)
        if isinstance(interpreted, list):
            for a in interpreted:
                trimed = [c for c in dfe.df.columns if c in a[1]]
                if a[0]:
                    targets += trimed
                else:
                    targets = [t for t in targets if t not in trimed]

        dfe.to_categorical(targets)
        return True
    
    def get_insight_targets(self, dfe):
        df = dfe.df
        def is_categorical(s):
            if s.dtype == float:
                return False

            c = s.count()
            freq = s.value_counts()

            if len(freq) / c <= 0.5:
                # records have to be accumulated by elements
                return True
            
            return False

        ts = []
        for c in df.columns:
            if is_categorical(df[c]):
                ts.append(c)
        
        return ts

    def interpret(self, reply):
        if isinstance(reply, bool):
            return reply
        
        text = reply.strip()
        p_plus = text.find("+")
        p_minus = text.find("-")
        pos = [p for p in sorted([p_plus, p_minus]) if p > -1]

        strip_split = lambda x: [e.strip() for e in x.split(",") if e.strip()]
        if len(pos) == 0:
            return True
        else:
            sign = True
            if pos[0] == p_minus:
                sign = False
            one = text[pos[0]+1:]
            the_ohter = ""
            if len(pos) == 2:
                one = text[pos[0]+1:pos[1]]
                the_ohter = text[pos[1]+1:]
            
            return [(sign, strip_split(one)), (not sign, strip_split(the_ohter))]
