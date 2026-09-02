import importlib.util
import tempfile
import unittest
from pathlib import Path

MODULE_PATH = Path(__file__).resolve().parents[1] / "scripts" / "import_notion_waiata.py"
spec = importlib.util.spec_from_file_location("import_notion_waiata", MODULE_PATH)
assert spec is not None and spec.loader is not None
notion_waiata = importlib.util.module_from_spec(spec)
spec.loader.exec_module(notion_waiata)


class NotionWaiataTests(unittest.TestCase):
    def test_split_front_matter_preserves_markdown_body(self):
        metadata, body = notion_waiata.split_front_matter(
            "---\ntitle: He hōnore\npublic: true\n---\n\n## Kupu\nKia ora\n"
        )
        self.assertEqual(metadata["title"], "He hōnore")
        self.assertTrue(metadata["public"])
        self.assertEqual(body, "\n\n## Kupu\nKia ora\n")

    def test_page_properties_map_site_fields_and_chunk_long_body(self):
        record = {
            "title": "Test waiata",
            "slug": "test-waiata",
            "public": True,
            "featured": True,
            "order": 7,
            "category": "waiata",
            "tags": ["beginner"],
            "composer": "A Composer",
            "source": "Local",
            "audio": "/audio/test.mp3",
            "pdf": "/pdf/test.pdf",
            "video_url": "https://youtu.be/example",
            "image": "/images/test.jpg",
            "_path": Path("/_waiata/test-waiata.md"),
            "_repo_root": Path("/"),
            "_body": "x" * 4000,
        }
        properties = notion_waiata.page_properties(record)
        self.assertEqual(properties["Name"]["title"][0]["text"]["content"], "Test waiata")
        self.assertTrue(properties["Public"]["checkbox"])
        self.assertEqual(properties["Video URL"]["url"], "https://youtu.be/example")
        self.assertGreater(len(properties["Website Body Markdown"]["rich_text"]), 1)
        self.assertEqual(properties["Website Path"]["rich_text"][0]["text"]["content"], "test-waiata.md")

    def test_build_markdown_uses_stable_website_path_and_source_id(self):
        row = {
            "id": "notion-page-123",
            "properties": {
                "Name": {"type": "title", "title": [{"plain_text": "He hōnore"}]},
                "Website Slug": {"type": "rich_text", "rich_text": [{"plain_text": "he-honore"}]},
                "Website Path": {"type": "rich_text", "rich_text": [{"plain_text": "he-honore.md"}]},
                "Public": {"type": "checkbox", "checkbox": True},
                "Featured": {"type": "checkbox", "checkbox": False},
                "Display Order": {"type": "number", "number": 25},
                "Category": {"type": "select", "select": {"name": "waiata"}},
                "Tags": {"type": "multi_select", "multi_select": [{"name": "beginner"}]},
                "Artist": {"type": "rich_text", "rich_text": []},
                "Source": {"type": "rich_text", "rich_text": []},
                "Audio URL": {"type": "url", "url": None},
                "PDF URL": {"type": "url", "url": None},
                "Video URL": {"type": "url", "url": "https://youtu.be/example"},
                "Image URL": {"type": "url", "url": None},
                "Website Body Markdown": {"type": "rich_text", "rich_text": [{"plain_text": "## Kupu\n\nKia ora\n"}]},
            },
        }
        path, content = notion_waiata.build_markdown(row)
        self.assertEqual(path, Path("_waiata/he-honore.md"))
        self.assertIn('notion_page_id: "notion-page-123"', content)
        self.assertIn('source_of_truth: notion', content)
        self.assertIn("## Kupu\n\nKia ora", content)

    def test_assembled_body_rebuilds_editable_sections(self):
        props = {
            "Kaupapa": {"type": "rich_text", "rich_text": [{"plain_text": "A welcome waiata."}]},
            "Kupu": {"type": "rich_text", "rich_text": [{"plain_text": "Kia ora\nKia ora"}]},
            "Translation": {"type": "rich_text", "rich_text": [{"plain_text": "Hello."}]},
            "Meaning": {"type": "rich_text", "rich_text": [{"plain_text": "Welcome."}]},
            "Notes": {"type": "rich_text", "rich_text": [{"plain_text": "Repeat twice."}]},
        }
        body = notion_waiata.assembled_body(props)
        self.assertIn("## Kaupapa\nA welcome waiata.", body)
        self.assertIn('<pre class="lyrics">\nKia ora\nKia ora\n</pre>', body)
        self.assertIn("## Translation\nHello.", body)
        self.assertIn('<div class="meaning">\nWelcome.\n</div>', body)
        self.assertIn("## Notes\nRepeat twice.", body)

    def test_read_existing_waiata_excludes_sample_and_private_records(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            (root / "_waiata").mkdir()
            (root / "_waiata" / "sample-waiata.md").write_text("---\npublic: true\n---\n", encoding="utf-8")
            (root / "_waiata" / "private.md").write_text("---\ntitle: Private\npublic: false\n---\nbody", encoding="utf-8")
            (root / "_waiata" / "public.md").write_text("---\ntitle: Public\npublic: true\n---\nbody", encoding="utf-8")
            records = notion_waiata.read_existing_waiata(root)
            self.assertEqual([record["title"] for record in records], ["Public"])

    def test_read_existing_waiata_can_include_nested_private_records(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            (root / "_waiata" / "_imports").mkdir(parents=True)
            (root / "_waiata" / "_imports" / "private.md").write_text(
                "---\ntitle: Private\npublic: false\n---\nbody", encoding="utf-8"
            )
            records = notion_waiata.read_existing_waiata(root, public_only=False)
            self.assertEqual([record["title"] for record in records], ["Private"])


if __name__ == "__main__":
    unittest.main()
