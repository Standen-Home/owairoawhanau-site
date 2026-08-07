(() => {
  const form = document.querySelector('[data-registration-form]');
  if (!form) return;

  form.addEventListener('submit', (event) => {
    event.preventDefault();
    const data = new FormData(form);
    const get = (name) => (data.get(name) || '').toString().trim();
    const eventName = form.dataset.registrationEvent || 'Event registration';

    const body = [
      `Kia ora,`,
      ``,
      `Please register my interest for ${eventName}.`,
      ``,
      `Name: ${get('name')}`,
      `Email: ${get('email')}`,
      `Phone: ${get('phone') || 'Not provided'}`,
      `Number attending: ${get('attending') || '1'}`,
      `Other names: ${get('extra_names') || 'None provided'}`,
      `Notes: ${get('notes') || 'None provided'}`,
      ``,
      `Ngā mihi`,
      get('name')
    ].join('\n');

    const subject = `${eventName} registration interest - ${get('name') || 'new registration'}`;
    const mailto = `mailto:info@owairoawhanau.co.nz?subject=${encodeURIComponent(subject)}&body=${encodeURIComponent(body)}`;
    window.location.href = mailto;
  });
})();
