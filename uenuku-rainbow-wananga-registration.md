---
layout: page
title: "Uenuku Rainbow Wānanga Registration"
title_en: "Register interest"
permalink: /uenuku-rainbow-wananga/register/
---

<p class="lede">Register your interest for the Uenuku Rainbow Wānanga with Taini Drummond.</p>

<div class="registration-event-summary">
  <p><strong>Date:</strong> Saturday 15 August 2026</p>
  <p><strong>Where:</strong> At the whare</p>
  <p><strong>Time:</strong> To be confirmed</p>
  <p><strong>Koha:</strong> Koha based — all proceeds to the whare</p>
</div>

<form class="registration-form" data-registration-form data-registration-event="Uenuku Rainbow Wānanga">
  <div class="registration-form-grid">
    <label class="field">
      Your name
      <input type="text" name="name" autocomplete="name" required>
    </label>

    <label class="field">
      Email
      <input type="email" name="email" autocomplete="email" required>
    </label>

    <label class="field">
      Phone
      <input type="tel" name="phone" autocomplete="tel">
    </label>

    <label class="field">
      Number attending
      <input type="number" name="attending" min="1" step="1" value="1" required>
    </label>
  </div>

  <label class="field">
    Names of anyone else coming with you
    <textarea name="extra_names" rows="3"></textarea>
  </label>

  <label class="field">
    Anything Taini/Kate should know?
    <textarea name="notes" rows="4" placeholder="Accessibility needs, transport questions, or anything else"></textarea>
  </label>

  <div class="registration-actions">
    <button class="btn btn-primary btn-lg" type="submit">Send registration interest</button>
    <a class="btn btn-ghost" href="tel:+64225676059">Call/text Taini: 022 567 6059</a>
  </div>

  <p class="note">This form opens an email with your details filled in so registrations can be confirmed by the whānau team.</p>
</form>

<script src="{{ '/assets/js/registration-mailto.js' | relative_url }}" defer></script>
