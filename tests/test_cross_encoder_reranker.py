import asyncio

from mcp.tool_manager import MCPToolManager


class FakeCrossEncoder:
    def __init__(self):
        self.pairs = []

    def predict(self, pairs, **kwargs):
        self.pairs = pairs
        return [0.1, 0.95, 0.4]


def test_cross_encoder_reranks_by_relevance_score():
    manager = MCPToolManager(api_key="test")
    reranker = FakeCrossEncoder()
    manager._reranker = reranker
    items = [
        {"title": "登录说明", "content": "如何登录账号"},
        {"title": "退款政策", "content": "商品签收后 7 天内可申请退款"},
        {"title": "物流说明", "content": "物流单号查询"},
    ]

    result = asyncio.run(manager._rerank("如何申请退款", items, top_k=2))

    assert [item["title"] for item in result] == ["退款政策", "物流说明"]
    assert reranker.pairs[1] == (
        "如何申请退款",
        "退款政策\n商品签收后 7 天内可申请退款",
    )


def test_cross_encoder_failure_falls_back_to_recall_order():
    manager = MCPToolManager(api_key="test")

    class BrokenCrossEncoder:
        def predict(self, pairs, **kwargs):
            raise RuntimeError("inference failed")

    manager._reranker = BrokenCrossEncoder()
    items = [{"content": "first"}, {"content": "second"}]

    result = asyncio.run(manager._rerank("query", items, top_k=1))

    assert result == items[:1]
