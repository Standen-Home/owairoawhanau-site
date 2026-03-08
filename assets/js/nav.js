(function(){
  const btn = document.querySelector('[data-nav-toggle]');
  const nav = document.querySelector('[data-site-nav]');
  if(!btn || !nav) return;
  btn.addEventListener('click', () => {
    const open = nav.classList.toggle('open');
    btn.setAttribute('aria-expanded', open ? 'true' : 'false');
  });
})();
