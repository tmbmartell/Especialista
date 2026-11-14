(() => {
  'use strict';
  let user = null;
  let csrf = null;
  let saveQueue = Promise.resolve();
  const button = document.getElementById('account-btn');
  const modal = document.getElementById('account-dialog');
  const content = document.getElementById('account-content');
  const store = window.EspecialistaStore;
  const money = cents => (cents/100).toLocaleString('pt-BR',{style:'currency',currency:'BRL'});

  async function api(path, options={}) {
    const headers = {'Content-Type':'application/json',...(csrf?{'X-CSRF-Token':csrf}:{})};
    const response = await fetch('/api'+path,{credentials:'same-origin',headers,...options});
    const data = await response.json().catch(()=>({}));
    if(!response.ok) throw new Error(typeof data.detail==='string'?data.detail:'Ocorreu um erro. Tente novamente.');
    return data;
  }

  function open() { if(!modal.open) modal.showModal(); }
  function node(tag,text,cls) {
    const element=document.createElement(tag);
    if(text!==undefined) element.textContent=text;
    if(cls) element.className=cls;
    return element;
  }
  function notice(message) {
    const n = node('p',message,'account-notice');
    content.append(n);
  }
  function clear() { content.replaceChildren(); }
  function action(text,cb,cls='account-action') {
    const b=node('button',text,cls);b.type='button';b.addEventListener('click',cb);content.append(b);return b;
  }

  function authForm(mode='register') {
    clear();
    content.append(node('h2',mode==='register'?'Crie seu espaço':'Entre no seu espaço'));
    notice('Acesso de demonstração local. Não use senhas pessoais ou dados reais.');
    const form=document.createElement('form');
    form.className='account-form';
    const email=node('input');email.type='email';email.name='email';email.placeholder='E-mail';email.autocomplete='email';email.required=true;email.maxLength=160;
    const password=node('input');password.type='password';password.name='password';password.placeholder='Senha (mínimo 12 caracteres)';password.autocomplete=mode==='register'?'new-password':'current-password';password.required=true;password.minLength=12;password.maxLength=256;
    const submit=node('button',mode==='register'?'Criar conta de teste':'Entrar','account-action');submit.type='submit';
    const feedback=node('p','','account-error');feedback.setAttribute('role','alert');
    form.append(email,password,submit,feedback); content.append(form);
    action(mode==='register'?'Já tenho conta':'Quero criar uma conta',()=>authForm(mode==='register'?'login':'register'),'account-link');
    form.addEventListener('submit', async event => {
      event.preventDefault();submit.disabled=true;feedback.textContent='';
      try {
        const result=await api('/auth/'+mode,{method:'POST',body:JSON.stringify({email:email.value,password:password.value})});
        user=result;csrf=result.csrf_token;button.textContent='Minha conta';
        const selection=store.getSelection();
        if(selection.length) await api('/me/cart',{method:'PUT',body:JSON.stringify({slugs:selection})});
        else {
          const remote=await api('/me/cart');
          store.setSelection(remote.selected.map(x=>x.slug));
        }
        renderAccount();
      } catch(error) {feedback.textContent=error.message;}
      finally {submit.disabled=false;}
    });
  }

  async function renderAccount() {
    clear();
    content.append(node('h2','Meu espaço'));
    content.append(node('p',user.email,'account-muted'));
    notice('Conta de teste: e-mail ainda não verificado. WhatsApp, pagamentos e acesso aos especialistas não estão ativos.');
    const orderList=node('div','','account-orders');
    content.append(orderList);
    async function load() {
      const cart=await api('/me/cart');
      const orders=await api('/me/orders');
      orderList.replaceChildren();
      orderList.append(node('p','Minha seleção: '+cart.specialistCount+' especialista(s) — '+money(cart.monthlyCents)+'/mês','account-summary'));
      orderList.append(node('p','Pedidos de demonstração: '+orders.orders.length,'account-muted'));
      orders.orders.forEach(x=>orderList.append(node('p','Pedido '+x.order_id.slice(0,8)+' · aguardando pagamento · '+money(x.monthlyCents),'account-muted')));
    }
    try{await load();}catch(error){notice(error.message);}
    action('Criar pedido demonstrativo',async()=>{
      try {
        const result=await api('/me/orders',{method:'POST'});
        notice('Pedido '+result.order_id.slice(0,8)+' criado. Nenhuma cobrança foi feita e nenhum especialista foi liberado.');
        await load();
      }catch(error){notice(error.message);}
    });
    action('Sair da conta',async()=>{
      try{
        await api('/auth/logout',{method:'POST'});
        user=null;csrf=null;button.textContent='Entrar / Criar conta';
        store.setSelection([]);authForm('login');
      }catch(error){notice(error.message);}
    },'account-link');
  }

  document.getElementById('close-account').addEventListener('click',()=>modal.close());
  button.addEventListener('click',()=>{open();if(user)renderAccount();else authForm('register');});
  modal.addEventListener('click',event=>{if(event.target===modal)modal.close();});
  window.addEventListener('especialista:selection',event=>{
    if(!user) return;
    const slugs=event.detail.slice();
    saveQueue=saveQueue.catch(()=>{}).then(()=>api('/me/cart',{method:'PUT',body:JSON.stringify({slugs})}));
    saveQueue.catch(err=>console.warn('Seleção ainda não foi salva:',err.message));
  });

  async function boot() {
    try{
      const current=await api('/auth/me');
      user=current;csrf=current.csrf_token;button.textContent='Minha conta';
      const remote=await api('/me/cart');
      store.setSelection(remote.selected.map(item=>item.slug));
    }catch(error){
      // Sem sessão: cliente pode explorar o catálogo sem conta.
    }
  }
  boot();
})();
