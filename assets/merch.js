'use strict';
(() => {
  const panel=document.querySelector('#merch-panel'), form=document.querySelector('#merch-form'), status=document.querySelector('#merch-state'), rows=document.querySelector('#merch-items');
  let products={}, loadedToken='';
  const labels={'25':'Up to $25','40':'Up to $40','60':'Up to $60',over60:'Over $60',unsure:'Not sure yet'};
  function element(tag,text){const e=document.createElement(tag);e.textContent=text;return e;}
  function addItem(item={}) {
    const row=element('div','');row.className='merch-item';
    const product=document.createElement('select'),size=document.createElement('select'),quantity=document.createElement('input'),remove=element('button','Remove');
    product.setAttribute('aria-label','Item');size.setAttribute('aria-label','Size');quantity.setAttribute('aria-label','Quantity');
    product.className='merch-product';size.className='merch-size';quantity.className='merch-quantity';
    for(const [id,p] of Object.entries(products))product.add(new Option(p.name,id));
    product.value=item.product || 'tee';
    size.required=true;
    function sizes(){size.replaceChildren();if(products[product.value].sizes.length>1)size.add(new Option('Choose size',''));for(const s of products[product.value].sizes)size.add(new Option(s,s));}
    product.onchange=sizes;sizes();if(item.size)size.value=item.size;
    quantity.type='number';quantity.min='1';quantity.max='20';quantity.required=true;quantity.value=item.quantity || 1;
    remove.type='button';remove.className='small-button';remove.onclick=()=>{row.remove();sync();};
    row.append(product,size,quantity,remove);rows.append(row);sync();
  }
  function sync(){form.elements.email.required=rows.children.length>0;document.querySelector('#add-merch').disabled=rows.children.length>=10 || form.elements.favorite.value==='none';}
  async function load(){
    const token=location.hash.slice(1);if(!token || loadedToken===token)return;
    try{
      const response=await fetch('/api/merch/catalog');if(!response.ok)throw new Error('Merch options are unavailable.');
      products=(await response.json()).products;
      const result=await api('/api/merch',{token});
      form.elements.favorite.replaceChildren(new Option('Choose your favorite',''));
      for(const [id,p] of Object.entries(products))form.elements.favorite.add(new Option(p.name,id));
      form.elements.favorite.add(new Option('No merch for me','none'));
      form.elements.budget.replaceChildren();for(const [id,label] of Object.entries(labels))form.elements.budget.add(new Option(label,id));
      const saved=result.response;form.elements.favorite.value=saved?.favorite || '';form.elements.budget.value=saved?.budget || 'unsure';form.elements.email.value=saved?.email || '';
      rows.replaceChildren();for(const item of saved?.items || [])addItem(item);
      loadedToken=token;panel.hidden=false;form.hidden=false;sync();
      status.textContent=saved?'Your choices are saved. You can change or cancel reservations here.':'';
    }catch(error){panel.hidden=false;status.textContent=error.message;form.hidden=true;}
  }
  form.elements.favorite.onchange=()=>{if(form.elements.favorite.value==='none')rows.replaceChildren();sync();};
  document.querySelector('#add-merch').onclick=()=>addItem();
  form.onsubmit=async event=>{
    event.preventDefault();const button=form.querySelector('[type=submit]');button.disabled=true;status.textContent='Saving…';
    const items=[...rows.children].map(row=>({product:row.querySelector('.merch-product').value,size:row.querySelector('.merch-size').value,quantity:Number(row.querySelector('.merch-quantity').value)}));
    try{await api('/api/merch/save',{token:location.hash.slice(1),favorite:form.elements.favorite.value,budget:form.elements.budget.value,email:form.elements.email.value,items});status.textContent=items.length?'Vote and unpaid reservations saved. Nothing has been charged or ordered.':'Vote saved. You have no items reserved.';}
    catch(error){status.textContent=error.message;}finally{button.disabled=false;}
  };
  window.addEventListener('fc5k-rsvp-saved',load);load();
})();
