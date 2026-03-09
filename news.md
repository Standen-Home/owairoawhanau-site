---
layout: page
title: "Pānui"
title_en: "News"
permalink: /news/
---

{% if site.posts.size > 0 %}
<ul>
  {% for post in site.posts %}
    <li>
      <a href="{{ post.url | relative_url }}">{{ post.title }}</a>
      <span class="badge">{{ post.date | date: "%d %b %Y" }}</span>
    </li>
  {% endfor %}
</ul>
{% else %}
<p>No pānui yet.</p>
{% endif %}
