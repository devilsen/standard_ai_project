"""评分工具行为测试：防止高均分掩盖致命问题、低维度分数和缺失评分。"""

import copy
import unittest

from score import WEIGHTS, evaluate


def complete_card():
    """构造明确标记的合成评分，不作为Agent运行证据。"""
    return {
        "scenario_id": "SYNTHETIC",
        "run_id": "unit-test",
        "skill_revision": "synthetic",
        "conditions": "synthetic test fixture",
        "reviewer": "unit-test",
        "ratings": {
            key: {"applicable": True, "score": 4, "evidence": ["synthetic"]}
            for key in WEIGHTS
        },
        "fatal_issues": [],
    }


class ScoreTests(unittest.TestCase):
    """验证计算和不完整输入处理，不验证Skill内容。"""

    def test_fatal_cannot_be_hidden_by_perfect_average(self):
        card = complete_card()
        card["fatal_issues"] = [{"issue": "overwrite", "evidence": "synthetic diff"}]
        result = evaluate(card)
        self.assertEqual(result["score"], 100)
        self.assertEqual(result["status"], "fatal")

    def test_missing_evidence_is_incomplete_not_zero_or_pass(self):
        card = complete_card()
        card["ratings"]["scope"]["evidence"] = []
        result = evaluate(card)
        self.assertEqual(result["status"], "incomplete")
        self.assertIsNone(result["score"])

    def test_low_dimension_fails_even_with_high_average(self):
        card = complete_card()
        card["ratings"]["scope"]["score"] = 2
        result = evaluate(card)
        self.assertEqual(result["score"], 92.5)
        self.assertEqual(result["status"], "needs_improvement")

    def test_not_applicable_normalizes_only_remaining_weights(self):
        card = complete_card()
        card["ratings"]["scope"] = {"applicable": False, "reason": "synthetic scenario"}
        result = evaluate(card)
        self.assertEqual(result["applicable_weight"], 85)
        self.assertEqual(result["score"], 100)
        self.assertEqual(result["status"], "candidate")

    def test_boolean_and_out_of_range_are_not_valid_scores(self):
        for value in (True, -1, 5, 3.5):
            with self.subTest(value=value):
                card = complete_card()
                card["ratings"]["scope"]["score"] = value
                with self.assertRaises(ValueError):
                    evaluate(card)

    def test_missing_dimension_and_all_na_are_incomplete(self):
        card = complete_card()
        del card["ratings"]["scope"]
        self.assertEqual(evaluate(card)["status"], "incomplete")
        card["ratings"] = {
            key: {"applicable": False, "reason": "synthetic"} for key in WEIGHTS
        }
        self.assertEqual(evaluate(card)["status"], "incomplete")

    def test_ordinary_lower_scores_and_invalid_na(self):
        card = complete_card()
        for item in card["ratings"].values():
            item["score"] = 3
        self.assertEqual(evaluate(card)["score"], 75)
        self.assertEqual(evaluate(card)["status"], "needs_improvement")
        invalid = copy.deepcopy(card)
        invalid["ratings"]["scope"] = {"applicable": False}
        with self.assertRaises(ValueError):
            evaluate(invalid)


if __name__ == "__main__":
    unittest.main()
