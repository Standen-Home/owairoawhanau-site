# Owairoa Whānau — Website (GitHub Pages)

This repo is a simple Jekyll site designed so whānau can add waiata and pānui easily.

## Editing content (the common tasks)

### Add a new waiata
1. Create a new Markdown file in `_waiata/` (copy `_waiata/sample-waiata.md`).
2. Fill in the front matter fields at the top.
3. Add lyrics and notes in the body.
4. (Optional) Upload files:
   - audio → `assets/audio/`
   - PDFs → `assets/pdfs/`
   - images → `assets/images/waiata/`
5. Commit and push.

**Tip:** set `public: true` to show it on the Waiata list page. If `public: false`, it will be hidden from the list.

### Add a pānui (news post)
1. Add a file to `_posts/` named like `YYYY-MM-DD-title.md`.
2. Include front matter like:

```yaml
---
title: "Practice update"
date: 2026-03-20
---
```

3. Write your update and commit.

### Edit navigation
Edit `_data/navigation.yml`.

## Waiata fields
Each waiata supports front matter like:

```yaml
---
layout: waiata
title: "Toia Mai"
slug: toia-mai
category: waiata-tira
tags:
  - beginner
composer: ""
featured: false
public: true
audio: "/assets/audio/toia-mai.mp3"
pdf: "/assets/pdfs/toia-mai.pdf"
video_url: ""
image: ""
order: 10
---
```

## Local preview (optional)
If you have Ruby/Jekyll installed:

```bash
bundle exec jekyll serve
```

(If you don’t, you can still edit files directly on GitHub and let Pages build it.)
