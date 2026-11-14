(() => {
  'use strict';
  const IDS={'solte-esse-peso':{title:'Solte Esse Peso',kind:'step'},
             'reconheca-seu-valor':{title:'Reconheça Seu Valor',kind:'quiz'}};
  const modal=document.getElementById('pilot-dialog');
  const heading=document.getElementById('pilot-title');
  const log=document.getElementById('pilot-log');
  const input=document.getElementById('pilot-input');
  const send=document.getElementById('pilot-send');
  const form=document.getElementById('pilot-form');
  const progress=document.getElementById('pilot-progress');
  const status=document.getElementById('pilot-status');
  const reset=document.getElementById('pilot-reset');
  const close=document.getElementById('pilot-close');
  let active=null, token=null, state=null, generation=0, busy=false;

  function bubble(kind,text) {
    const p=document.createElement('p');
    p.className='coragem-bubble coragem-'+kind;
    p.textContent=text;
    log.append(p);
    log.scrollTop=log.scrollHeight;
  }
  function setProgress(result) {
    if(result.done) progress.textContent='Reflexão concluída';
    else if(active && IDS[active].kind==='quiz') progress.textContent='Questão '+(result.state.index+1)+' de 10';
    else progress.textContent='Etapa '+(Math.min(['episode','emotion','certainty','control','repair','action'].indexOf(result.state.step)+1,6))+' de 6';
    input.disabled=result.done||!token;
    send.disabled=result.done||!token;
  }
  async function call(message,previous) {
    const r=await fetch('/api/me/preview/'+active+'/turn',{
      method:'POST',credentials:'same-origin',
      headers:{'Content-Type':'application/json','X-CSRF-Token':token},
      body:JSON.stringify({message,state:previous||{}})
    });
    const body=await r.json().catch(()=>({}));
    if(!r.ok) throw Error(typeof body.detail==='string'?body.detail:'Não foi possível continuar.');
    return body;
  }
  async function start(slug) {
    if(!IDS[slug]) return;
    const id=++generation;
    active=slug;token=null;state=null;busy=true;
    heading.textContent=IDS[slug].title;
    log.replaceChildren();
    input.value='';input.disabled=true;send.disabled=true;reset.disabled=true;
    progress.textContent='Iniciando...';
    status.textContent='Demonstração: nenhuma resposta é gravada; não use dados pessoais reais.';
    if(!modal.open) modal.showModal();
    try {
      const auth=await fetch('/api/auth/me',{credentials:'same-origin'});
      if(id!==generation||!modal.open) return;
      if(!auth.ok) {
        bubble('system','Faça login numa conta de demonstração para experimentar. Não utilize dados sensíveis neste teste.');
        progress.textContent='Login necessário';
        const button=document.createElement('button');
        button.className='account-action';button.type='button';button.textContent='Entrar numa conta de teste';
        button.onclick=()=>{modal.close();document.getElementById('account-btn')?.click();};
        log.append(button);
        return;
      }
      token=(await auth.json()).csrf_token;
      const answer=await call('',{});
      if(id!==generation||!modal.open) return;
      state=answer.state;
      bubble('assistant',answer.reply);
      setProgress(answer);
      reset.disabled=false;
      input.focus({preventScroll:true});
    } catch(error) {
      if(id===generation&&modal.open){
        bubble('system','A prévia não está disponível aqui: '+error.message);
        progress.textContent='Indisponível';
      }
    } finally {busy=false;}
  }
  window.startPilotDemo=start;
  form.addEventListener('submit',async event=>{
    event.preventDefault();
    if(busy||!token||!state)return;
    const message=input.value.trim();
    if(!message)return;
    const id=generation;
    busy=true;send.disabled=true;
    bubble('user',message);
    input.value='';
    try {
      const answer=await call(message,state);
      if(id!==generation||!modal.open)return;
      state=answer.state;
      bubble('assistant',answer.reply);
      status.textContent=answer.safety==='normal'
        ? 'Roteiro demonstrativo, sem inteligência generativa.'
        : 'Roteiro interrompido para priorizar sua segurança.';
      setProgress(answer);
    } catch(error){
      if(id!==generation||!modal.open)return;
      bubble('system','Não consegui continuar: '+error.message);
      input.value=message;
      send.disabled=false;
    } finally {
      busy=false;
      if(modal.open&&!input.disabled) input.focus({preventScroll:true});
    }
  });
  reset.onclick=()=>{if(!busy&&active) start(active);};
  close.onclick=()=>modal.close();
  modal.addEventListener('click',e=>{if(e.target===modal)modal.close();});
  modal.addEventListener('close',()=>{
    generation++;
    active=null;token=null;state=null;busy=false;
    input.value='';log.replaceChildren();
  });
})();
