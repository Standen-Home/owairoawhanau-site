---
layout: page
title: "Featured Events"
title_en: "Upcoming Events"
permalink: /calendar/featured-events/
---

{% assign now_ts = site.time | date: "%s" | plus: 0 %}
{% assign events = site.featured_events | sort: "date" %}
{% assign has_upcoming = false %}

{% for event in events %}
  {% assign event_ts = event.date | date: "%s" | plus: 0 %}
  {% if event_ts >= now_ts %}
    {% assign has_upcoming = true %}
    {% break %}
  {% endif %}
{% endfor %}

{% if has_upcoming %}
<ul>
  {% for event in events %}
    {% assign event_ts = event.date | date: "%s" | plus: 0 %}
    {% if event_ts >= now_ts %}
    <li>
      <a href="{{ event.url | relative_url }}">{{ event.title }}</a>
      <span class="badge">{{ event.date | date: "%d %b %Y" }}</span>
    </li>
    {% endif %}
  {% endfor %}
</ul>
{% else %}
<p>No featured events yet.</p>
{% endif %}
