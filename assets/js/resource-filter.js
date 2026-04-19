(function(){
  const q = document.getElementById('resource-q');
  const tag = document.getElementById('resource-tag');
  const cards = Array.from(document.querySelectorAll('[data-resource-card]'));

  function norm(s){return (s||'').toLowerCase().trim();}

  function apply(){
    const nq = norm(q && q.value);
    const ntag = norm(tag && tag.value);
    let shown = 0;

    for(const el of cards){
      const title = norm(el.getAttribute('data-title'));
      const keywords = norm(el.getAttribute('data-keywords'));
      const tags = norm(el.getAttribute('data-tags'));

      const okQ = !nq || title.includes(nq) || keywords.includes(nq) || tags.includes(nq);
      const okT = !ntag || (tags.split(',').map(s=>s.trim()).includes(ntag));

      const ok = okQ && okT;
      el.style.display = ok ? '' : 'none';
      if(ok) shown++;
    }

    const counter = document.getElementById('resource-count');
    if(counter) counter.textContent = shown;
  }

  if(q) q.addEventListener('input', apply);
  if(tag) tag.addEventListener('change', apply);
  apply();
})();
