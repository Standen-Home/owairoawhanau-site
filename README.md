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

### Add a featured event page
1. Add a file to `_featured_events/` named like `YYYY-MM-DD-title.md`.
2. Include front matter like:

```yaml
---
title: "Matariki Whakanui"
date: 2026-07-18
calendar_summary: "Matariki O Wairoa Marae"
calendar_start: "2026-07-18"
---
```

3. Write the full event details in the body.
4. If you want the calendar card to link to this page automatically, make sure `calendar_summary` and `calendar_start` match the calendar event, or use `calendar_uid` instead.

### Edit navigation
Edit `_data/navigation.yml`.

## Weekly maintainer checklist

1. Add or update the latest pānui in `_posts/`.
2. Check the public Google Calendar has the next practice/event details.
3. Feature any waiata the group is currently learning by setting `featured: true`.
4. Keep any whānau-only waiata as `public: false`.
5. Push to `main`, then check the GitHub Pages deploy completed successfully.

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

## Calendar events
The site reads the public Google Calendar ICS feed during the Jekyll build using `_plugins/calendar_reader.rb`.

Recurring events are expanded at build time so future instances from repeating calendar entries appear on the home page and calendar page.

## Local preview (optional)
If you have Ruby/Jekyll installed:

```bash
bundle install
bundle exec jekyll serve
```

(If you don’t, you can still edit files directly on GitHub and let Pages build it.)
