(() => {
  const STORAGE_KEY = 'owairoaWaiataLyricsSizeStep';
  const MIN_STEP = -2;
  const MAX_STEP = 4;
  const BASE_REM = 1.15;
  const STEP_REM = 0.12;

  const clamp = (value) => Math.max(MIN_STEP, Math.min(MAX_STEP, value));

  const readStep = () => {
    const saved = Number.parseInt(window.localStorage.getItem(STORAGE_KEY) || '0', 10);
    return Number.isFinite(saved) ? clamp(saved) : 0;
  };

  const writeStep = (step) => {
    window.localStorage.setItem(STORAGE_KEY, String(step));
  };

  const sizeForStep = (step) => `${(BASE_REM + step * STEP_REM).toFixed(2)}rem`;

  const applyStep = (lyrics, step) => {
    lyrics.style.setProperty('--lyrics-size', sizeForStep(step));
    lyrics.setAttribute('data-size-step', String(step));
  };

  const buildButton = (label, action, title) => {
    const button = document.createElement('button');
    button.type = 'button';
    button.className = 'lyrics-size-btn';
    button.dataset.action = action;
    button.textContent = label;
    button.setAttribute('aria-label', title);
    button.title = title;
    return button;
  };

  const enhanceLyrics = (lyrics) => {
    if (lyrics.closest('.lyrics-wrap')) return;

    const wrapper = document.createElement('div');
    wrapper.className = 'lyrics-wrap';

    const toolbar = document.createElement('div');
    toolbar.className = 'lyrics-toolbar';

    const label = document.createElement('div');
    label.className = 'lyrics-toolbar-label';
    label.textContent = 'Kupu size';

    const actions = document.createElement('div');
    actions.className = 'lyrics-toolbar-actions';
    actions.append(
      buildButton('A−', 'decrease', 'Make kupu smaller'),
      buildButton('Reset', 'reset', 'Reset kupu size'),
      buildButton('A+', 'increase', 'Make kupu larger')
    );

    toolbar.append(label, actions);
    lyrics.parentNode.insertBefore(wrapper, lyrics);
    wrapper.append(toolbar, lyrics);

    let step = readStep();
    applyStep(lyrics, step);

    toolbar.addEventListener('click', (event) => {
      const button = event.target.closest('button[data-action]');
      if (!button) return;

      if (button.dataset.action === 'increase') step = clamp(step + 1);
      if (button.dataset.action === 'decrease') step = clamp(step - 1);
      if (button.dataset.action === 'reset') step = 0;

      writeStep(step);
      document.querySelectorAll('.lyrics').forEach((item) => applyStep(item, step));
    });
  };

  document.querySelectorAll('.lyrics').forEach(enhanceLyrics);
})();
