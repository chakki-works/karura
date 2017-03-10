from karura.core.analyst import Analyst
import karura.core.insights as I


def make_analyst(df):
    t_insight = I.TargetConfirmInsight()
    ig_insight = I.ColumnIgnoranceInsight()
    na_insight = I.NAFrequencyCheckInsight()
    c_insight = I.CategoricalItemInsight()
    cr_insight = I.CategoryReductionInsight()
    n_insight = I.NumericalScalingInsight()
    c_d_insight = I.CategoricalToDummyInsight()
    f_insight = I.FeatureSelectionInsight()
    m_insight = I.ModelSelectionInsight()
    ay = Analyst(df, [
        t_insight,
        ig_insight,
        na_insight,
        c_insight,
        cr_insight,
        n_insight,
        c_d_insight,
        f_insight,
        m_insight
        ])
    return ay
