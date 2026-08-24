import importlib.util
import tempfile
import unittest
from pathlib import Path

MODULE_PATH = Path(__file__).resolve().parents[1] / "scripts" / "import_notion_resources.py"
spec = importlib.util.spec_from_file_location("import_notion_resources", MODULE_PATH)
assert spec is not None and spec.loader is not None
resources = importlib.util.module_from_spec(spec)
spec.loader.exec_module(resources)


class NotionResourceTests(unittest.TestCase):
    def test_read_existing_resources_defaults_to_public(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            (root / "_resources").mkdir()
            (root / "_resources" / "guide.md").write_text(
                "---\ntitle: Guide\ntitle_en: Help\nslug: guide\ntags:\n  - info\nsummary: A guide\n---\n\n## Start\nKia ora\n",
                encoding="utf-8",
            )
            records = resources.read_existing_resources(root)
            self.assertEqual(len(records), 1)
            self.assertTrue(records[0]["public"])
            self.assertEqual(records[0]["_body"], "\n\n## Start\nKia ora\n")

    def test_page_properties_include_resource_metadata_and_full_body(self):
        record = {
            "title": "Guide",
            "title_en": "Help",
            "slug": "guide",
            "tags": ["info"],
            "summary": "A guide",
            "keywords": "guide help",
            "featured": True,
            "public": True,
            "_path": Path("_resources/guide.md"),
            "_body": "x" * 4000,
        }
        properties = resources.page_properties(record)
        self.assertEqual(properties["English Title"]["rich_text"][0]["text"]["content"], "Help")
        self.assertTrue(properties["Featured"]["checkbox"])
        self.assertEqual(properties["Website Path"]["rich_text"][0]["text"]["content"], "guide.md")
        self.assertGreater(len(properties["Website Body Markdown"]["rich_text"]), 1)

    def test_build_markdown_uses_stable_path_and_source_id(self):
        row = {
            "id": "resource-page-123",
            "properties": {
                "Name": {"type": "title", "title": [{"plain_text": "Guide"}]},
                "English Title": {"type": "rich_text", "rich_text": [{"plain_text": "Help"}]},
                "Website Slug": {"type": "rich_text", "rich_text": [{"plain_text": "guide"}]},
                "Website Path": {"type": "rich_text", "rich_text": [{"plain_text": "guide.md"}]},
                "Summary": {"type": "rich_text", "rich_text": [{"plain_text": "A guide"}]},
                "Keywords": {"type": "rich_text", "rich_text": []},
                "Tags": {"type": "multi_select", "multi_select": [{"name": "info"}]},
                "Featured": {"type": "checkbox", "checkbox": True},
                "Public": {"type": "checkbox", "checkbox": True},
                "Display Order": {"type": "number", "number": 1},
                "Website Body Markdown": {"type": "rich_text", "rich_text": [{"plain_text": "\n\n## Start\nKia ora\n"}]},
            },
        }
        path, content = resources.build_markdown(row)
        self.assertEqual(path, Path("_resources/guide.md"))
        self.assertIn('title_en: "Help"', content)
        self.assertIn('notion_page_id: "resource-page-123"', content)
        self.assertIn("## Start\nKia ora", content)


if __name__ == "__main__":
    unittest.main()
