class Insight():

    def __init__(self, lang="ja"):
        self.lang = lang
        self.advice = {}
        self.index = InsightIndex()
        self.automatic = False
    
    def describe(self):
        if self.lang in self.advice:
            return self.advice[self.lang]
        elif len(self.advice) > 0:
            return list[self.advice.values()][0]
        else:
            return ""
    
    def is_invoked_by(self, dfe):
        its = self.get_insight_targets(dfe)
        if len(its) > 0:
            return True
        else:
            return False

    def adopt(self, dfe):
        raise Exception("You have to implements apply method")
    
    def get_insight_targets(self, dfe):
        raise Exception("You have to implements get_insight_targets method")
        


class InsightIndex():
    COLUMN_CHECK_TAG = "column_check"

    def __init__(self, done=False, tags=()):
        self.done = done
        self.tags = [] if len(tags) == 0 else tags
    
    def as_column_check(self):
        self.append_tag(self.COLUMN_CHECK_TAG)
    
    @classmethod
    def query_column_checks(cls, insights, done=False):
        return cls.query(insights, done, cls.COLUMN_CHECK_TAG)

    def append_tag(self, tag_name):
        if tag_name not in self.tags:
            self.tags.append(tag_name)

    @classmethod
    def query(cls, insights, is_done=None, tag=""):
        done_criteria = lambda x: True if is_done is None or x.index.done == is_done else False
        tag_criteria = lambda x: True if tag == "" or tag in x.index.tags else False
        items = [i for i in insights if done_criteria(i) and tag_criteria(i)]
        return items
