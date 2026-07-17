---
layout: page
title: "Maramataka"
title_en: "Calendar"
permalink: /calendar/
---

{% assign events = site.data.calendar_events | sort: "start" %}

<p class="lede">Upcoming practices, hui, and performances.</p>

{% if events and events.size > 0 %}
  <div class="calendar-shell" aria-label="Calendar" data-calendar-tabs>
    <div class="calendar-header">
      <div>
        <div class="calendar-title">Maramataka</div>
        <div class="calendar-sub">Upcoming events</div>
      </div>
      <div class="calendar-actions">
        <button class="btn btn-primary" type="button" data-calendar-tab-button="list" aria-pressed="true">Upcoming events</button>
        <button class="btn" type="button" data-calendar-tab-button="month" aria-pressed="false">Month view</button>
        <a class="btn" href="{{ '/calendar/featured-events/' | relative_url }}">Featured events</a>
        <a class="btn btn-ghost" href="https://calendar.google.com/calendar/u/0?cid=c_135be84f9af8db2cf3f25fad81c2cebeae12b25e8281480aa737a95ce54f54c0@group.calendar.google.com" target="_blank" rel="noopener">Open in Google</a>
      </div>
    </div>

    <div class="calendar-panel" data-calendar-panel="list">
      {% include calendar-upcoming.html %}
    </div>

    <div class="calendar-panel" data-calendar-panel="month" hidden>
      <div class="calendar-embed">
        <iframe
          title="Owairoa Whanau month calendar"
          src="https://calendar.google.com/calendar/embed?src=c_135be84f9af8db2cf3f25fad81c2cebeae12b25e8281480aa737a95ce54f54c0@group.calendar.google.com&ctz=Pacific%2FAuckland&mode=MONTH&showTitle=0&showPrint=0&showTabs=0&showCalendars=0&showTz=0"
          loading="lazy"
          referrerpolicy="no-referrer-when-downgrade"
          frameborder="0"
          scrolling="no"></iframe>
      </div>
      <p class="note calendar-panel-note">Month view is embedded here. Use "Open in Google" only if you need Google Calendar controls.</p>
    </div>
  </div>

  <script src="{{ '/assets/js/calendar-tabs.js' | relative_url }}" defer></script>
{% else %}
  {% include calendar-upcoming.html %}
{% endif %}
