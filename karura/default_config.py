from karura.core.analyst import Analyst
from karura.core.auto_run import AutoRun
import karura.core.insights as I


def make_analyst(df, feature_type_estimation=True):
    insights = []
    insights.append(I.TargetConfirmInsight())
    insights.append(I.ColumnIgnoranceInsight())
    insights.append(I.NAFrequencyCheckInsight())
    if feature_type_estimation:
        insights.append(I.CategoricalItemInsight())
    insights.append(I.CategoryReductionInsight())
    insights.append(I.NumericalScalingInsight())
    insights.append(I.DatetimeToCategoricalInsight())
    insights.append(I.CategoricalToDummyInsight())
    insights.append(I.FeatureSelectionInsight())
    insights.append(I.ModelSelectionInsight())

    ay = Analyst(df, insights)
    return ay


def make_autorun(df, feature_type_estimation=True):
    insights = []
    insights.append(I.NAFrequencyCheckInsight())
    if feature_type_estimation:
        insights.append(I.CategoricalItemInsight())
    insights.append(I.CategoryReductionInsight())
    insights.append(I.NumericalScalingInsight())
    insights.append(I.DatetimeToCategoricalInsight())
    insights.append(I.CategoricalToDummyInsight())
    insights.append(I.FeatureSelectionInsight())
    insights.append(I.ModelSelectionInsight())

    ar = AutoRun(df, insights)
    return ar

