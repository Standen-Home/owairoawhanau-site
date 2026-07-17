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
<div class="featured-events-grid">
  {% for event in events %}
    {% assign event_ts = event.date | date: "%s" | plus: 0 %}
    {% if event_ts >= now_ts %}
      {% assign matched_calendar = nil %}
      {% for calendar_event in site.data.calendar_events %}
        {% assign summary_match = event.calendar_summary | to_s | strip %}
        {% assign start_match = event.calendar_start | to_s | strip %}
        {% assign uid_match = event.calendar_uid | to_s | strip %}
        {% if uid_match != "" and calendar_event.uid == uid_match %}
          {% assign matched_calendar = calendar_event %}
          {% break %}
        {% endif %}
        {% if summary_match != "" and start_match != "" and calendar_event.summary == summary_match and calendar_event.start == start_match %}
          {% assign matched_calendar = calendar_event %}
          {% break %}
        {% endif %}
      {% endfor %}
      <article class="featured-event-card">
        {% if matched_calendar and matched_calendar.image %}
          <figure class="calendar-event-media">
            <img src="{{ matched_calendar.image }}" alt="{{ matched_calendar.image_alt | default: event.title }}">
          </figure>
        {% endif %}
        <div class="featured-event-head">
          <h2><a href="{{ event.url | relative_url }}">{{ event.title }}</a></h2>
          {% if matched_calendar and matched_calendar.display_time != blank %}
            <p class="featured-event-time">{{ matched_calendar.display_time }}</p>
          {% else %}
            <p class="featured-event-time">{{ event.date | date: "%a %d %b %Y" }}</p>
          {% endif %}
        </div>
        {% if matched_calendar and matched_calendar.location %}
          <p class="featured-event-location">{{ matched_calendar.location }}</p>
        {% endif %}
        {% if matched_calendar and matched_calendar.teaser %}
          <p>{{ matched_calendar.teaser }}</p>
        {% else %}
          <p>{{ event.excerpt | strip_html | truncate: 180 }}</p>
        {% endif %}
        <p><a class="btn" href="{{ event.url | relative_url }}">Open event page</a></p>
      </article>
    {% endif %}
  {% endfor %}
</div>
{% else %}
<p>No featured events yet.</p>
{% endif %}
