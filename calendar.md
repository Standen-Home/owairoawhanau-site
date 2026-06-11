---
layout: page
title: "Maramataka"
title_en: "Calendar"
permalink: /calendar/
---

{% assign events = site.data.calendar_events | sort: "start" %}

<p class="lede">Upcoming practices, hui, and performances.</p>

{% if events and events.size > 0 %}
  {% capture known_locations %}|{% endcapture %}
  {% capture known_months %}|{% endcapture %}

  <div class="calendar-shell" aria-label="Calendar">
    <div class="calendar-header">
      <div>
        <div class="calendar-title">Maramataka</div>
        <div class="calendar-sub">Upcoming events</div>
      </div>
      <div class="calendar-actions">
        <a class="btn" href="https://calendar.google.com/calendar/embed?src=c_135be84f9af8db2cf3f25fad81c2cebeae12b25e8281480aa737a95ce54f54c0@group.calendar.google.com&ctz=Pacific%2FAuckland&mode=MONTH&showTitle=0&showPrint=0&showTabs=0&showCalendars=0&showTz=0" target="_blank" rel="noopener">Month view</a>
        <a class="btn btn-ghost" href="https://calendar.google.com/calendar/u/0?cid=c_135be84f9af8db2cf3f25fad81c2cebeae12b25e8281480aa737a95ce54f54c0@group.calendar.google.com" target="_blank" rel="noopener">Open in Google</a>
      </div>
    </div>

    <form class="calendar-filters" data-calendar-filters>
      <div class="field">
        <label for="calendar-search">Search</label>
        <input id="calendar-search" type="search" placeholder="Search events or locations" data-calendar-search>
      </div>
      <div class="field">
        <label for="calendar-month">Month</label>
        <select id="calendar-month" data-calendar-month>
          <option value="">All months</option>
          {% for event in events %}
            {% assign month_key = event.start | date: "%Y-%m" %}
            {% assign month_label = event.start | date: "%B %Y" %}
            {% capture month_token %}|{{ month_key }}|{% endcapture %}
            {% unless known_months contains month_token %}
              <option value="{{ month_key }}">{{ month_label }}</option>
              {% capture known_months %}{{ known_months }}{{ month_key }}|{% endcapture %}
            {% endunless %}
          {% endfor %}
        </select>
      </div>
      <div class="field">
        <label for="calendar-location">Location</label>
        <select id="calendar-location" data-calendar-location>
          <option value="">All locations</option>
          {% for event in events %}
            {% if event.location %}
              {% assign location_value = event.location | strip %}
              {% capture location_token %}|{{ location_value }}|{% endcapture %}
              {% unless known_locations contains location_token %}
                <option value="{{ location_value | downcase }}">{{ location_value }}</option>
                {% capture known_locations %}{{ known_locations }}{{ location_value }}|{% endcapture %}
              {% endunless %}
            {% endif %}
          {% endfor %}
        </select>
      </div>
    </form>

    <p class="calendar-results" data-calendar-results>{{ events.size }} upcoming events</p>

    <div class="calendar-list" data-calendar-list>
      {% for event in events %}
        {% assign search_blob = event.summary | append: " " | append: event.location | append: " " | append: event.description %}
        <article
          class="calendar-event"
          data-calendar-event
          data-month="{{ event.start | date: '%Y-%m' }}"
          data-location="{{ event.location | downcase | escape }}"
          data-search="{{ search_blob | strip_newlines | downcase | escape }}">
          <div class="calendar-event-head">
            <h2>{{ event.summary }}</h2>
            <time datetime="{{ event.start }}">{{ event.start | date: "%a %d %b %Y, %l:%M %p" }}</time>
          </div>
          {% if event.location %}
            <p class="event-note">{{ event.location }}</p>
          {% endif %}
          {% if event.description %}
            <p>{{ event.description | newline_to_br }}</p>
          {% endif %}
          {% if event.url %}
            <p><a class="event-link" href="{{ event.url }}" target="_blank" rel="noopener">View details</a></p>
          {% endif %}
        </article>
      {% endfor %}
    </div>

    <p class="note calendar-empty" data-calendar-empty hidden>No events match the current filters.</p>
  </div>

  <script src="{{ '/assets/js/calendar-filter.js' | relative_url }}" defer></script>
{% else %}
  <div class="card">
    <p class="muted">No upcoming events were available from the calendar feed.</p>
  </div>
{% endif %}
