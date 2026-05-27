(function(){
  function qs(sel, root=document){return root.querySelector(sel)}
  function qsa(sel, root=document){return Array.from(root.querySelectorAll(sel))}

  function openModal(modal){
    if(!modal) return;
    modal.classList.add('open');
    modal.setAttribute('aria-hidden','false');
    document.body.classList.add('modal-open');

    // focus close button
    const closeBtn = qs('[data-modal-close]', modal);
    if(closeBtn) closeBtn.focus();
  }

  function closeModal(modal){
    if(!modal) return;
    modal.classList.remove('open');
    modal.setAttribute('aria-hidden','true');
    document.body.classList.remove('modal-open');
  }

  qsa('[data-modal-open]').forEach(btn => {
    btn.addEventListener('click', () => {
      const id = btn.getAttribute('data-modal-open');
      openModal(document.getElementById(id));
    });
  });

  qsa('.modal').forEach(modal => {
    qsa('[data-modal-close]', modal).forEach(el => {
      el.addEventListener('click', () => closeModal(modal));
    });
  });

  document.addEventListener('keydown', (e) => {
    if(e.key !== 'Escape') return;
    const modal = qs('.modal.open');
    if(modal) closeModal(modal);
  });
})();
