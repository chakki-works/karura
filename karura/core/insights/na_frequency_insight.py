# -*- coding: utf-8 -*-
from karura.core.insight import Insight
from karura.core.description import Description, ImageFile
import matplotlib.pyplot as plt


class NAFrequencyCheckInsight(Insight):

    def __init__(self, na_rate_border=0.5):
        super().__init__()
        self.na_rate_border = na_rate_border
        self.index.as_column_check()
    
    def is_applicable(self, dfe):
        self.init_description()
        its = self.get_insight_targets(dfe)
        if len(its) > 0:
            na_rates = dfe.df.isnull().sum() / len(dfe.df)  # ignores na.
            pic = ImageFile.create()
            with pic.plot() as fig:
                na_rates.plot.bar()
            
            self.description = {
                "ja": Description("{} は欠損値が多い項目になっています。除外してもよいですか？".format(its), pic),
                "en": Description("{} includes much n/a values. Could I exclude these?".format(its), pic)
            }

            return True
        else:
            return False
    
    def adopt(self, dfe, interpreted=None):
        if isinstance(interpreted, bool) and not interpreted:
            return 0
        self.init_description()
        columns = self.get_insight_targets(dfe)
        dfe.df.drop(columns, inplace=True, axis=1)
        dfe.sync()

    def get_insight_targets(self, dfe):
        na_rates = dfe.df.isnull().sum() / len(dfe.df)  # ignores na.
        na_frequents = na_rates[na_rates >= self.na_rate_border].index.tolist()

        if len(na_frequents) > 0:
            return na_frequents
        else:
            return []
