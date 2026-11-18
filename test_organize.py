import tempfile
import unittest
from pathlib import Path

import organize


class OrganizeTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        for name in ["a.jpg", "b.pdf", "c.mp4", "d.unknown", "e.py"]:
            (self.root / name).write_text(name)

    def tearDown(self):
        self.tmp.cleanup()

    def test_dry_run_changes_nothing(self):
        organize.main([str(self.root)])
        self.assertTrue((self.root / "a.jpg").exists())

    def test_apply_then_undo(self):
        organize.main([str(self.root), "--apply"])
        self.assertTrue((self.root / "Images" / "a.jpg").exists())
        self.assertTrue((self.root / "Other" / "d.unknown").exists())
        organize.main([str(self.root), "--undo"])
        for name in ["a.jpg", "b.pdf", "c.mp4", "d.unknown", "e.py"]:
            self.assertTrue((self.root / name).exists(), name)
        self.assertFalse((self.root / "Images").exists())

    def test_name_collision_is_not_overwritten(self):
        (self.root / "Images").mkdir()
        (self.root / "Images" / "a.jpg").write_text("existing")
        organize.main([str(self.root), "--apply"])
        self.assertEqual((self.root / "Images" / "a.jpg").read_text(), "existing")
        self.assertTrue((self.root / "Images" / "a (1).jpg").exists())


if __name__ == "__main__":
    unittest.main()
