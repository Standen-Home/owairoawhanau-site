# Owairoa Whānau — Website (GitHub Pages)

This repo is a simple Jekyll site designed so whānau can add waiata and pānui easily.

## Editing content (the common tasks)

### Waiata source of truth

Public waiata are now maintained in the shared Notion **Waiata Songs** database and
imported into `_waiata/` for the Jekyll build. The generated files retain the Notion
page ID in front matter so records can be matched safely.

To seed or refresh Notion from the existing public Markdown during migration:

```bash
NOTION_API_KEY=... python3 scripts/import_notion_waiata.py --push-existing
```

To pull public Notion records into the repository:

```bash
NOTION_API_KEY=... python3 scripts/import_notion_waiata.py --pull
```

The scheduled GitHub Action requires a repository secret named `NOTION_API_KEY`.
It commits generated changes and dispatches the Pages deployment workflow.

### Resource source of truth

Public resource pages are maintained in the shared Notion **Waiata Resources**
database and imported into `_resources/`:

```bash
NOTION_API_KEY=... python3 scripts/import_notion_resources.py --push-existing
NOTION_API_KEY=... python3 scripts/import_notion_resources.py --pull
```

The resource importer preserves the page body Markdown, website path, and stable
Notion page ID in generated front matter.

### Add a new waiata
1. Create a new row in the Notion **Waiata Songs** database.
2. Set `Public`, `Featured`, category, tags, and display order as needed.
3. Fill the separate content fields: `Kaupapa`, `Kupu`, `Translation`, `Meaning`, and `Notes`.
   `Kupu` is the lyrics field; the importer adds the website formatting around it.
4. Add media URLs in the matching Notion fields:
   - `Audio URL`
   - `PDF URL`
   - `Video URL`
   - `Image URL`
5. Run the Notion import, or wait for the scheduled GitHub Action.

The Markdown files in `_waiata/` and `_resources/` are generated deploy output;
edit the Notion records rather than editing those files directly.

**Tip:** set the Notion `Public` checkbox to show a waiata on the website. Leave it unchecked for whānau-only content.

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
event_date: 2026-07-18
calendar_summary: "Matariki O Wairoa Marae"
calendar_start: "2026-07-18"
---
```

3. Write the full event details in the body.
4. If you want the calendar card to link to this page automatically, make sure `calendar_summary` and `calendar_start` match the calendar event, or use `calendar_uid` instead. For a recurring event that has more than one calendar UID, use:

```yaml
calendar_uids:
  - "first-series-uid@google.com"
  - "next-series-uid@google.com"
```

5. Featured events normally disappear from the Featured Events list and nav after `event_date`. For evergreen/recurring pages, set `event_end_date` to the last date the page should stay listed.
6. Featured event pages automatically show a "Next event" card when their calendar matching fields find an upcoming Google Calendar event.

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
