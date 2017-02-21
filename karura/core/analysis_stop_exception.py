class AnalysisStopException(Exception):

    def __init__(self, insight):
        self.insight = insight
