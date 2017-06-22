from karura.core.insight import InsightIndex


class ModelStore():

    def __init__(self, path, model_name):
        self.path = path
        self.model_name = model_name
    
    def save_model(self, insights, tag_order):
        orderd_insights = []
        for t in tag_order:
            t_insights = InsightIndex.query(insights, tag=t)
            for i in t_insights:
                orderd_insights.append(t_insights)
        
        pass

    def activate(self, model_name):
        pass

    def deactivate(self, model_name):
        pass

    def load_model(self):
        pass
