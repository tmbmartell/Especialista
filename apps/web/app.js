(() => {
  'use strict';
  let catalog = [];
  const selected = new Set();
  let category = 'Todos';
  const $ = (id) => document.getElementById(id);
  const money = (cents) => (cents / 100).toLocaleString('pt-BR', {style:'currency',currency:'BRL'});
  const icon = {spark:'✦',cycle:'↻',cards:'✧',tree:'♧',moon:'☾',heart:'♡',hand:'✋',links:'∞',number:'③',seed:'❀',flower:'✿',feather:'❧',sun:'☀'};
  function monthly(n) { return n ? 990 + (n - 1) * 499 : 0; }
  function make(tag, klass, text) { const el = document.createElement(tag); if (klass) el.className = klass; if (text !== undefined) el.textContent = text; return el; }
  function renderFilters() {
    const box = $('filters'); box.replaceChildren();
    for (const item of ['Todos', ...new Set(catalog.map((x) => x.category))]) {
      const b = make('button','filter',item); b.type='button'; b.setAttribute('aria-pressed',String(category === item)); b.onclick=()=>{category=item;renderFilters();renderCards();}; box.append(b);
    }
  }
  function renderCards() {
    const box=$('cards'); box.replaceChildren();
    for (const product of catalog.filter((x)=>category === 'Todos' || x.category === category)) {
      const c=make('article','card');
      const visual=make('div','symbol',icon[product.icon] || '✦'); visual.setAttribute('aria-hidden','true');
      const label=make('div','category',product.category), title=make('h3','',product.name), desc=make('p','',product.description);
      const add=make('button','add',selected.has(product.slug) ? '✓ Adicionado — retirar' : '+ Adicionar ao plano');
      add.type='button'; add.dataset.slug=product.slug; add.setAttribute('aria-pressed',String(selected.has(product.slug)));
      if(selected.has(product.slug)) add.classList.add('added');
      add.onclick=()=>{if(selected.has(product.slug)) selected.delete(product.slug); else selected.add(product.slug);renderCards();renderCart();emitSelection();};
      const peek=make('button','preview','Conhecer experiência');
      peek.type='button';
      peek.onclick=()=>window.showExperiencePreview?.(product.slug);
      c.append(visual,label,title,desc,peek,add); box.append(c);
    }
  }
  function renderCart() {
    $('count').textContent = String(selected.size);
    $('amount').textContent = money(monthly(selected.size));
    $('simulate').disabled = selected.size === 0;
    const ul=$('selected');ul.replaceChildren();
    if(!selected.size){ul.append(make('li','', 'Escolha um especialista para começar.'));return;}
    const picked = [...selected].map((slug)=>catalog.find((c)=>c.slug===slug)).filter(Boolean);
    picked.forEach((p,i)=>{
      const li=make('li','');li.append(make('span','',p.name),make('strong','',i===0?money(990):money(499)));
      const rm=make('button','', 'Retirar');rm.type='button';rm.setAttribute('aria-label','Retirar '+p.name);
      rm.onclick=()=>{selected.delete(p.slug);renderCards();renderCart();emitSelection();};li.append(rm);ul.append(li);
    });
  }
  function emitSelection() { window.dispatchEvent(new CustomEvent('especialista:selection',{detail:[...selected]})); }
  window.EspecialistaStore = {
    getSelection: () => [...selected],
    setSelection(slugs) {
      selected.clear();
      for (const slug of slugs) selected.add(slug);
      if (catalog.length) {renderCards();renderCart();}
    }
  };
  async function init() {
    try {
      const response=await fetch('./catalogo.json',{cache:'no-store'});
      if(!response.ok) throw new Error('HTTP '+response.status);
      const data=await response.json();
      if(!Array.isArray(data.items)) throw new Error('Catálogo inválido');
      catalog=data.items;
      renderFilters();renderCards();renderCart();
      $('simulate').onclick=()=>{
        const count=selected.size;
        $('checkout-note').textContent='Prévia: '+count+' especialista(s) por '+money(monthly(count))+'/mês. Nenhuma cobrança foi efetuada. O checkout seguro será integrado nas próximas fases.';
        $('checkout-note').setAttribute('role','status');
      };
    } catch (e) {
      $('cards').replaceChildren(make('p','', 'O catálogo não pôde ser carregado. Execute a prévia usando um servidor HTTP local.'));
      console.error('Erro ao carregar catálogo:',e);
    }
  }
  init();
})();
