(function(){
  const q = document.getElementById('waiata-q');
  const cat = document.getElementById('waiata-category');
  const tag = document.getElementById('waiata-tag');
  const cards = Array.from(document.querySelectorAll('[data-waiata-card]'));

  function norm(s){return (s||'').toLowerCase().trim();}

  function apply(){
    const nq = norm(q && q.value);
    const ncat = norm(cat && cat.value);
    const ntag = norm(tag && tag.value);

    let shown = 0;
    for(const el of cards){
      const title = norm(el.getAttribute('data-title'));
      const keywords = norm(el.getAttribute('data-keywords'));
      const category = norm(el.getAttribute('data-category'));
      const tags = norm(el.getAttribute('data-tags'));

      const okQ = !nq || title.includes(nq) || keywords.includes(nq) || tags.includes(nq);
      const okC = !ncat || category === ncat;
      const okT = !ntag || (tags.split(',').map(s=>s.trim()).includes(ntag));

      const ok = okQ && okC && okT;
      el.style.display = ok ? '' : 'none';
      if(ok) shown++;
    }

    const counter = document.getElementById('waiata-count');
    if(counter) counter.textContent = shown;
  }

  [q,cat,tag].forEach(el => el && el.addEventListener('input', apply));
  apply();
})();
