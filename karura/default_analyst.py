from karura.core.analyst import Analyst
import karura.core.insights as I
from karura.env import get_lang


def make_analyst(df):
    lang = get_lang()
    c_insight = I.CategoricalItemInsight(lang=lang)
    ay = Analyst(df, [c_insight])
    return ay
