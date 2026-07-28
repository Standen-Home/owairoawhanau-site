(function(){
  const btn = document.querySelector('[data-nav-toggle]');
  const nav = document.querySelector('[data-site-nav]');
  if(!btn || !nav) return;

  function setOpen(open){
    nav.classList.toggle('open', open);
    btn.setAttribute('aria-expanded', open ? 'true' : 'false');
    btn.setAttribute('aria-label', open ? 'Close navigation menu' : 'Open navigation menu');
    document.body.classList.toggle('nav-open', open);
  }

  btn.addEventListener('click', () => {
    setOpen(!nav.classList.contains('open'));
  });

  nav.addEventListener('click', (event) => {
    if(event.target.closest('a')) setOpen(false);
  });

  document.addEventListener('keydown', (event) => {
    if(event.key === 'Escape') setOpen(false);
  });
})();
