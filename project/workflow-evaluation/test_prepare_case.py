"""评估输入准备测试：验证不覆盖工作与不泄露评分答案。"""

import json
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from prepare_case import materialize


class PrepareCaseTests(unittest.TestCase):
    """验证生成输入及真实场景目录的安全边界。"""

    def test_all_scenarios_prepare_without_rubrics(self):
        path = Path(__file__).parent / "scenarios" / "cases.json"
        cases = json.loads(path.read_text(encoding="utf-8"))
        self.assertEqual(len({case["id"] for case in cases}), len(cases))
        with TemporaryDirectory() as base:
            for case in cases:
                with self.subTest(scenario=case["id"]):
                    output = Path(base) / case["id"]
                    materialize(case, output)
                    expected = {"CASE.md", *case["files"]}
                    actual = {str(p.relative_to(output)) for p in output.rglob("*") if p.is_file()}
                    self.assertEqual(actual, expected)
                    for name, content in case["files"].items():
                        self.assertEqual((output / name).read_text(encoding="utf-8"), content)

    def test_existing_work_not_overwritten(self):
        with TemporaryDirectory() as base:
            output = Path(base)
            original = output / "page.tsx"
            original.write_text("unfinished design", encoding="utf-8")
            with self.assertRaises(ValueError):
                materialize({"id": "X", "prompt": "X", "files": {"page.tsx": "replacement"}}, output)
            self.assertEqual(original.read_text(encoding="utf-8"), "unfinished design")

    def test_traversal_absolute_and_reserved_names_rejected_before_writing(self):
        for name in ("../outside", "/outside", "CASE.md", "a\\b", "."):
            with self.subTest(name=name), TemporaryDirectory() as base:
                output = Path(base) / "new"
                with self.assertRaises(ValueError):
                    materialize({"id": "X", "prompt": "X", "files": {name: "bad"}}, output)
                self.assertFalse(output.exists())


if __name__ == "__main__":
    unittest.main()
