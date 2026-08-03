import hashlib
import importlib.util
import sys
import tempfile
import unittest
from pathlib import Path

MODULE_PATH = Path(__file__).resolve().parents[1] / "scripts" / "import_klaviyo_panui.py"
spec = importlib.util.spec_from_file_location("import_klaviyo_panui", MODULE_PATH)
assert spec is not None
assert spec.loader is not None
import_klaviyo_panui = importlib.util.module_from_spec(spec)
sys.modules["import_klaviyo_panui"] = import_klaviyo_panui
spec.loader.exec_module(import_klaviyo_panui)


class ImportKlaviyoPanuiTests(unittest.TestCase):
    def test_slugify_handles_macrons_and_punctuation(self):
        self.assertEqual(import_klaviyo_panui.slugify("Pānui o te Wiki! 15 June"), "panui-o-te-wiki-15-june")

    def test_existing_import_index_dedupes_by_campaign_message_and_hash(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            repo_root = Path(temp_dir)
            post = repo_root / "_posts" / "2026-06-15-panui.md"
            post.parent.mkdir()
            post.write_text(
                "---\n"
                "title: Existing\n"
                "klaviyo_campaign_id: camp_123\n"
                "klaviyo_message_id: msg_456\n"
                "klaviyo_content_hash: abc123\n"
                "---\n"
                "Body\n",
                encoding="utf-8",
            )

            index = import_klaviyo_panui.load_existing_import_index(repo_root)

            self.assertIn("camp_123", index.campaign_ids)
            self.assertIn("msg_456", index.message_ids)
            self.assertIn("abc123", index.content_hashes)

    def test_rewrite_images_downloads_meaningful_images_and_skips_tracking(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            tmp_path = Path(temp_dir)
            downloads = {}

            def fake_download(url):
                downloads[url] = downloads.get(url, 0) + 1
                return b"image-bytes", "image/jpeg"

            html = (
                '<p>Kia ora</p>'
                '<img src="https://example.com/photo.jpg" alt="Whānau photo">'
                '<img src="https://example.com/pixel.gif" width="1" height="1">'
            )

            rewritten = import_klaviyo_panui.rewrite_images(
                html,
                assets_dir=tmp_path / "assets" / "images" / "panui" / "camp_123",
                public_prefix="/assets/images/panui/camp_123",
                download=fake_download,
            )

            self.assertNotIn("https://example.com/photo.jpg", rewritten)
            self.assertIn("/assets/images/panui/camp_123/", rewritten)
            self.assertNotIn("pixel.gif", downloads)
            self.assertEqual(downloads["https://example.com/photo.jpg"], 1)

    def test_build_post_uses_date_slug_and_front_matter(self):
        content_hash = hashlib.sha256(b"<p>Hello</p>").hexdigest()
        post = import_klaviyo_panui.ImportedPost(
            title="Pānui o te Wiki",
            date="2026-06-15",
            body_html="<p>Hello</p>",
            campaign_id="camp_123",
            message_id="msg_456",
            content_hash=content_hash,
            klaviyo_web_url="https://example.com/web-view",
        )

        path, text = import_klaviyo_panui.build_post_file(post)

        self.assertEqual(path, Path("_posts/2026-06-15-panui-o-te-wiki.md"))
        self.assertIn('title: "Pānui o te Wiki"', text)
        self.assertIn('klaviyo_campaign_id: "camp_123"', text)
        self.assertIn('klaviyo_message_id: "msg_456"', text)
        self.assertIn('klaviyo_web_url: "https://example.com/web-view"', text)
        self.assertIn("<p>Hello</p>", text)

    def test_import_posts_uses_stable_campaign_field_names(self):
        captured = {}

        def fake_paginated_api_get(path, api_key, revision, query):
            captured["path"] = path
            captured["query"] = query
            return []

        original = import_klaviyo_panui.paginated_api_get
        import_klaviyo_panui.paginated_api_get = fake_paginated_api_get
        try:
            with tempfile.TemporaryDirectory() as temp_dir:
                import_klaviyo_panui.import_posts(Path(temp_dir), "key", "2026-07-15", "panui", dry_run=True)
        finally:
            import_klaviyo_panui.paginated_api_get = original

        self.assertEqual(captured["path"], "/api/campaigns")
        self.assertEqual(
            captured["query"]["fields[campaign]"],
            "created_at,updated_at,name,status,send_time,scheduled_at,archived",
        )
        self.assertEqual(captured["query"]["filter"], "equals(messages.channel,'email')")
        self.assertNotIn("definition", captured["query"]["fields[campaign]"])

    def test_is_sent_campaign_rejects_drafts(self):
        self.assertTrue(import_klaviyo_panui.is_sent_campaign({"attributes": {"status": "Sent"}}))
        self.assertTrue(import_klaviyo_panui.is_sent_campaign({"attributes": {"send_time": "2026-06-15T10:00:00Z"}}))
        self.assertFalse(import_klaviyo_panui.is_sent_campaign({"attributes": {"status": "Draft"}}))


if __name__ == "__main__":
    unittest.main()
