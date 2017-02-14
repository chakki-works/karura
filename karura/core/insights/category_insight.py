from karura.core.insight import Insight


class CategoryInsight(Insight):

    def __init__(self, lang="ja"):
        super().__init__(lang)
        self.index.as_column_check()
    
    def adopt(self, dfe):
        targets = self.get_insight_targets(dfe)
        dfe.to_categorical(targets)
    
    def get_insight_targets(self, dfe):
        df = dfe.df
        def is_categorical(s):
            if s.dtype == float:
                return False

            c = s.count()
            freq = s.value_counts()

            if len(freq) / c <= 0.5:
                # records is accumulated by elements
                return True
            
            return False

        ts = []
        for c in df.columns:
            if is_categorical(df[c]):
                ts.append(c)
        
        if len(ts) > 0:
            self.advice = {
                "ja": "{} seems to be categorical column. ok?".format(ts)
            }

        return ts


