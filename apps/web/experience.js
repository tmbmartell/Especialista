(() => {
  'use strict';
  const dialog = document.getElementById('experience-dialog');
  const content = document.getElementById('experience-content');
  const close = document.getElementById('close-experience');
  let profiles = null;
  const $el = (tag, className='', text='') => {
    const item = document.createElement(tag);
    if (className) item.className = className;
    if (text) item.textContent = text;
    return item;
  };
  async function load() {
    if (!profiles) {
      const res = await fetch('./experiencias.json',{cache:'no-store'});
      if (!res.ok) throw new Error('Prévia indisponível');
      const json = await res.json();
      if (json.publicDataOnly !== true || !Array.isArray(json.items)) {
        throw new Error('Manifesto de prévia inválido');
      }
      profiles = json.items;
    }
    return profiles;
  }
  function render(item) {
    content.replaceChildren();
    content.append($el('p','eyebrow','UMA CONVERSA COM PROPÓSITO'));
    const name = document.querySelector('[data-slug="'+item.slug+'"]')?.closest('.card')?.querySelector('h3')?.textContent || 'Seu especialista';
    content.append($el('h2','',name));
    content.append($el('p','experience-purpose',item.purpose));
    const opening = $el('div','experience-message');
    opening.append($el('small','', 'Como essa conversa começa'));
    opening.append($el('p','',item.firstQuestion));
    content.append(opening);
    content.append($el('p','experience-subheading','O que vamos explorar'));
    const list=$el('ol','experience-stages');
    for (const step of item.stages) list.append($el('li','',step.title));
    content.append(list);
    content.append($el('p','experience-disclaimer',item.disclaimer));
    content.append($el('p','experience-status','Prévia da experiência: ainda sem IA, pagamento ou atendimento pelo WhatsApp.'));
    if (item.slug === 'coragem-para-ir') {
      const button=$el('button','account-action','Experimentar conversa curta');
      button.type='button';
      button.addEventListener('click',()=>{
        dialog.close();
        window.startCoragemDemo?.();
      });
      content.append(button);
    }
  }
  window.showExperiencePreview = async (slug) => {
    content.replaceChildren($el('p','','Carregando prévia…'));
    if (!dialog.open) dialog.showModal();
    try {
      const list = await load();
      const item = list.find((entry)=>entry.slug===slug);
      if (!item) throw new Error('Experiência não encontrada');
      render(item);
    } catch (error) {
      content.replaceChildren($el('p','account-error',error.message));
    }
  };
  close.addEventListener('click',()=>dialog.close());
  dialog.addEventListener('click',event=>{if(event.target===dialog)dialog.close();});
})();
