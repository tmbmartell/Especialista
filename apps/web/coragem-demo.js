(() => {
  'use strict';
  const dialog = document.getElementById('coragem-demo-dialog');
  const closeButton = document.getElementById('coragem-close');
  const log = document.getElementById('coragem-log');
  const form = document.getElementById('coragem-form');
  const textarea = document.getElementById('coragem-input');
  const send = document.getElementById('coragem-send');
  const progress = document.getElementById('coragem-progress');
  const status = document.getElementById('coragem-status');
  const resetButton = document.getElementById('coragem-reset');
  const STAGES = ['goal', 'impact', 'prediction', 'evidence', 'choice', 'timing'];
  let state = null;
  let csrf = null;
  let pending = false;
  let generation = 0;

  function line(kind, text) {
    const p=document.createElement('p');
    p.className='coragem-bubble coragem-'+kind;
    p.textContent=text;
    log.append(p);
    log.scrollTop=log.scrollHeight;
  }
  function updateUI(step, done=false) {
    const current=Math.max(0,STAGES.indexOf(step));
    progress.textContent=done?'Jornada concluída': 'Etapa '+(current+1)+' de '+STAGES.length;
    textarea.disabled=done || !csrf;
    send.disabled=done || !csrf;
    resetButton.disabled=!csrf;
  }
  async function post(message, incomingState) {
    const response=await fetch('/api/me/preview/coragem-para-ir/turn', {
      method:'POST',
      credentials:'same-origin',
      headers:{'Content-Type':'application/json','X-CSRF-Token':csrf},
      body:JSON.stringify({message,state:incomingState||{step:'goal',answers:{}}})
    });
    const data=await response.json().catch(()=>({}));
    if(!response.ok) throw Error(typeof data.detail==='string'?data.detail:'Falha na conversa de teste.');
    return data;
  }
  async function begin() {
    const currentGeneration=++generation;
    state=null;csrf=null;pending=true;
    log.replaceChildren();
    textarea.value='';
    textarea.disabled=true;send.disabled=true;resetButton.disabled=true;
    status.textContent='Roteiro de demonstração sem IA. As respostas não são armazenadas no servidor.';
    progress.textContent='Preparando...';
    if(!dialog.open) dialog.showModal();
    try {
      const auth=await fetch('/api/auth/me',{credentials:'same-origin'});
      if(currentGeneration!==generation || !dialog.open) return;
      if(!auth.ok) {
        line('system','Para experimentar, entre numa conta de teste. Não utilize histórias pessoais sensíveis neste ambiente.');
        status.textContent='Apenas no sandbox local. Faça login primeiro.';
        const login=document.createElement('button');
        login.textContent='Abrir login de teste';
        login.type='button';
        login.className='account-action';
        login.onclick=()=>{dialog.close();document.getElementById('account-btn')?.click();};
        log.append(login);
        progress.textContent='Login necessário';
        return;
      }
      const user=await auth.json();csrf=user.csrf_token;
      const data=await post('',{step:'goal',answers:{}});
      if(currentGeneration!==generation || !dialog.open) return;
      state=data.state;
      line('assistant',data.reply);
      updateUI(state.step,data.done);
      textarea.focus({preventScroll:true});
    } catch(err) {
      line('system','O teste ainda não está disponível aqui: '+err.message);
      progress.textContent='Indisponível';
    } finally {pending=false;}
  }
  window.startCoragemDemo=begin;
  form.addEventListener('submit',async event=>{
    event.preventDefault();
    if(pending || !csrf || !state) return;
    const currentGeneration=generation;
    const text=textarea.value.trim();
    if(!text) return;
    pending=true;
    send.disabled=true;
    line('user',text);
    textarea.value='';
    try {
      const data=await post(text,state);
      if(currentGeneration!==generation || !dialog.open) return;
      state=data.state;
      line('assistant',data.reply);
      updateUI(state.step,data.done);
      status.textContent=data.safety==='normal'
        ? 'Prévia técnica · Sem IA, pagamentos ou WhatsApp.'
        : 'O roteiro foi interrompido para priorizar segurança.';
    } catch(error) {
      if(currentGeneration!==generation || !dialog.open) return;
      line('system','Não foi possível responder agora: '+error.message);
      textarea.value=text;send.disabled=false;
    } finally {
      pending=false;
      log.scrollTop=log.scrollHeight;
      if(dialog.open && !textarea.disabled) textarea.focus({preventScroll:true});
    }
  });
  resetButton.addEventListener('click',()=>{
    if(!csrf || pending) return;
    begin();
  });
  closeButton.addEventListener('click',()=>dialog.close());
  dialog.addEventListener('click',event=>{if(event.target===dialog)dialog.close();});
  dialog.addEventListener('close',()=>{
    generation++;
    // Nada fica no localStorage; ao fechar, descartamos o estado privado da prévia.
    state=null;csrf=null;pending=false;
    textarea.value='';log.replaceChildren();
  });
})();
