
(function(){
  const menuBtn = document.getElementById('menu-toggle');
  const sidebar = document.getElementById('sidebar');
  if(menuBtn && sidebar){
    menuBtn.addEventListener('click',()=>sidebar.classList.toggle('open'));
    document.addEventListener('click',(e)=>{
      if(window.innerWidth<=760 && sidebar.classList.contains('open') && !sidebar.contains(e.target) && e.target!==menuBtn){
        sidebar.classList.remove('open');
      }
    });
  }
  const input = document.getElementById('search-input');
  const box = document.getElementById('search-results');
  if(!input || !box || !window.SEARCH_INDEX) return;
  const root = document.body.dataset.root || '';
  function escapeHtml(s){return s.replace(/[&<>"']/g,m=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[m]));}
  function render(){
    const q = input.value.trim().toLowerCase();
    if(q.length < 1){box.classList.remove('open');box.innerHTML='';return;}
    const hits = window.SEARCH_INDEX.filter(item=>{
      const hay = (item.title+' '+item.summary+' '+(item.tags||[]).join(' ')+' '+item.text).toLowerCase();
      return hay.includes(q);
    }).slice(0,9);
    if(!hits.length){box.innerHTML='<div class="search-empty">没有找到，试试“蛋白质”“减重”“维生素 D”。</div>';box.classList.add('open');return;}
    box.innerHTML = hits.map(item=>`<a class="search-hit" href="${root}${item.url}"><b>${escapeHtml(item.title)}</b><span>${escapeHtml(item.module)} · ${escapeHtml(item.summary||'')}</span></a>`).join('');
    box.classList.add('open');
  }
  input.addEventListener('input', render);
  input.addEventListener('focus', render);
  document.addEventListener('click',(e)=>{if(!box.contains(e.target)&&e.target!==input)box.classList.remove('open');});
  document.addEventListener('keydown',(e)=>{if(e.key==='Escape'){box.classList.remove('open');input.blur();}});
})();
