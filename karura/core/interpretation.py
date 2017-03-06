import pandas as pd
from karura.env import get_lang
from karura.core.insight import Insight
from karura.core.dataframe_extension import FType
from karura.core.description import Description, ImageFile


class Interpretation():
    LANG = get_lang()

    def __init__(self):
        self.lang = self.LANG
        self.description = {}
    
    def interpret(self, dfe, insight):
        d = self.make_description(dfe, insight)
        if self.lang in d:
            return d[self.lang]
        elif len(d) > 0:
            return list[d.values()][0]
        else:
            return ""
    
    def make_description(self, dfe, insight):
        raise Exception("You have to implements make_description that returns dictionary of description.")


class ModelInterpretation(Interpretation):

    def __init__(self):
        super().__init__()
        self.description = {}

    def make_description(self, dfe, insight):
        importances = pd.Series(insight.model.feature_importances_, index=dfe.get_features().columns).sort_values(ascending=False)
        pic = ImageFile.create()
        with pic.plot() as plt_fig:
            importances.plot.bar()
        
        score = insight.score
        description = {
            "ja": Description("モデルの精度は{}です。モデルに使われている項目の貢献度は図のようになっています。".format(score), pic),
            "en": Description("The model accuracy is {}. The contributions of each features are here.".format(score), pic)
        }
        return description

