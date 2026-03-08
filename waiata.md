---
layout: page
title: "Waiata"
permalink: /waiata/
---

<div class="waiata-controls">
  <div class="field">
    <label for="waiata-q">Search</label>
    <input id="waiata-q" type="search" placeholder="Search by title, tags…" autocomplete="off">
  </div>

  <div class="field">
    <label for="waiata-category">Category</label>
    <select id="waiata-category">
      <option value="">All</option>
      {% assign cats = site.waiata | where: "public", true | map: "category" | uniq | sort %}
      {% for c in cats %}
        {% if c %}<option value="{{ c }}">{{ c }}</option>{% endif %}
      {% endfor %}
    </select>
  </div>

  <div class="field">
    <label for="waiata-tag">Tag</label>
    <select id="waiata-tag">
      <option value="">All</option>
      {% assign tags = "" | split: "" %}
      {% for w in site.waiata %}
        {% if w.public == true and w.tags %}
          {% assign tags = tags | concat: w.tags %}
        {% endif %}
      {% endfor %}
      {% assign tags = tags | uniq | sort %}
      {% for t in tags %}
        <option value="{{ t }}">{{ t }}</option>
      {% endfor %}
    </select>
  </div>

  <div class="field">
    <label>Total</label>
    <div><span id="waiata-count">0</span> waiata</div>
  </div>
</div>

<div class="waiata-list">
  {% assign waiata_public = site.waiata | where: "public", true | sort: "order" %}
  {% for waiata in waiata_public %}
    {% include waiata-card.html waiata=waiata %}
  {% endfor %}
</div>

<script src="{{ '/assets/js/waiata-filter.js' | relative_url }}" defer></script>
