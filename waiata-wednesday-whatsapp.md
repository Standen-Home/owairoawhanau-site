---
title: "Join the Waiata Wednesday WhatsApp Group"
permalink: /waiata-wednesday-whatsapp/
description: "Share your phone number to join the Ō Wairoa Waiata Wednesday WhatsApp group."
---

# Join the Waiata Wednesday WhatsApp Group

Kia ora! Use this form to share your mobile number for the **Waiata Wednesday WhatsApp group**.

<div class="registration-event-summary">
  <p><strong>What it is for:</strong> Waiata Wednesday reminders, practice updates, and whānau notices.</p>
  <p><strong>Privacy:</strong> Other WhatsApp group members may be able to see your phone number. You can leave the group at any time.</p>
</div>

<form class="registration-form" id="waiata-whatsapp-form">
  <div class="registration-form-grid">
    <div class="field">
      <label for="whatsapp-name">Your name</label>
      <input id="whatsapp-name" name="name" type="text" autocomplete="name" required>
    </div>
    <div class="field">
      <label for="whatsapp-phone">Mobile number</label>
      <input id="whatsapp-phone" name="phone" type="tel" autocomplete="tel" inputmode="tel" placeholder="022 123 4567" required>
    </div>
  </div>
  <div class="field">
    <label for="whatsapp-note">Anything we should know? <span class="muted">(optional)</span></label>
    <textarea id="whatsapp-note" name="note" rows="3"></textarea>
  </div>
  <div class="registration-actions">
    <button class="btn btn-primary btn-lg" type="submit">Send my details</button>
  </div>
  <p class="note">Submitting opens an email to Ō Wairoa Whānau with your details filled in. Check the message, then press Send.</p>
</form>

<script>
(function () {
  const form = document.getElementById('waiata-whatsapp-form');
  if (!form) return;

  form.addEventListener('submit', function (event) {
    event.preventDefault();
    const data = new FormData(form);
    const name = String(data.get('name') || '').trim();
    const phone = String(data.get('phone') || '').trim();
    const note = String(data.get('note') || '').trim();
    const subject = 'Waiata Wednesday WhatsApp group signup';
    const body = [
      'Kia ora,',
      '',
      'Please add me to the Waiata Wednesday WhatsApp group.',
      '',
      'Name: ' + name,
      'Mobile: ' + phone,
      'Note: ' + (note || '—'),
      '',
      'I understand that other WhatsApp group members may be able to see my phone number.'
    ].join('\n');
    window.location.href = 'mailto:info@owairoawhanau.co.nz?subject=' + encodeURIComponent(subject) + '&body=' + encodeURIComponent(body);
  });
})();
</script>
