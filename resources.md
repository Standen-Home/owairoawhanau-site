---
layout: page
title: "Rauemi"
title_en: "Resources"
permalink: /resources/
---

<div class="two-col">
  <div>

## Waiata Puāwai; Session Flow
A simple outline of how our hui/practice time often runs.
*This can be adapted depending on the kaupapa for the day.*

1. **Karakia tīmatanga** — opening karakia
2. **Whaikōrero** — speech of welcome / kōrero
3. **Waiata tautoko** — supporting waiata for speaker
4. **Whakawhanaungatanga / Pepeha** — new whānau connections and introductions in te reo *(templates below are often on the screen)*
5. **Pānui** — notices and upcoming events
6. **Whakahā** — breathing exercises
7. **Ngā waiata** — songs (learning + practice)
8. **Karakia whakamutunga** — closing karakia

---

## Pepeha
Mix and match what fits for you. It’s okay to keep it simple.

- **Tēnā koutou katoa** — Hello to you all
- **Ko _ te maunga** — is the mountain
- **Ko _ te awa / roto** — is the river / lake
- **Ko _ te waka** — is the waka
- **Ko _ te iwi** — are the tribe
- **Ko _ te hapū** — are the subtribe
- **Ko _ te marae** — is the marae
- **Nō _ ahau** — I’m from
- **Ko _ tōku ingoa** — My name is
- **Tēnā tātou katoa** — Greetings everyone

### Options for Non-Māori
- **Tēnā koutou katoa** — Hello to you all
- **Te whakapaparanga mai _** — is my ancestry *(e.g. Ko Kōtirana — Scotland/Scottish)*
- **Engari** — but, however
- **Ko _ te whenua tupu** — *Placename* is where I grew up.
- **Ko _ te kāinga** — *Place* is my home.
- **Nō _ au** — I'm from *place*.
- **Kei _ au e noho ana** — I am living in *place*.
- **He _ au i _** — I am *job title* at *name of work*.
- **Ko _ au** — I am *Name*.
- **Tēnā tātou katoa** — Greetings everyone

---

## Whakahā (breathing)
A short breathing moment to settle, warm up, and get our voices ready.

- Take 2–3 slow breaths together.
- Relax shoulders/jaw.
- Gentle hum into the first waiata.

  </div>

  <aside class="sidebar" aria-label="Resource library">
    <div class="sidebar-box">
      <h2 style="margin-top:0">Resource library</h2>

      <div class="field">
        <label for="resource-q">Search</label>
        <input id="resource-q" type="search" placeholder="Search resources…" autocomplete="off">
      </div>

      <p class="note" style="margin:.6rem 0 0 0"><span id="resource-count">0</span> resources</p>

      <div class="resource-list">
        {% assign resources_sorted = site.resources | sort: "title" %}
        {% for r in resources_sorted %}
          {% include resource-card.html r=r %}
        {% endfor %}
      </div>

      <script src="{{ '/assets/js/resource-filter.js' | relative_url }}" defer></script>
    </div>
  </aside>
</div>
