from karura.core.analyst import Analyst
import karura.core.insights as I


def make_analyst(df):
    c_insight = I.CategoricalItemInsight()
    na_insight = I.NAFrequencyCheckInsight()
    t_insight = I.TargetConfirmInsight()
    ig_insight = I.ColumnIgnoranceInsight()
    n_insight = I.NumericalScalingInsight()
    c_d_insight = I.CategoricalToDummyInsight()
    f_insight = I.FeatureSelectionInsight()
    m_insight = I.ModelSelectionInsight()
    ay = Analyst(df, [
        c_insight,
        na_insight,
        t_insight,
        ig_insight,
        n_insight,
        c_d_insight,
        f_insight,
        m_insight
        ])
    return ay
