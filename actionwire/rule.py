from actionwire.action import Action, PrintAction


class KeyRule:
    def __init__(self, keywords: list[str]):
        self.keywords = keywords

    def satisfies(self, input: str) -> Action | None:
        for keyword in self.keywords:
            if input.find(keyword) != -1:
                return PrintAction(keyword)
        return None


# rules = [
#     KeyRule(
#         keywords=["喝茶"],
#         OnOffEvent(),
#         actions=[
#             SeekAction("00:24")
#         ]
#     )
# ]
