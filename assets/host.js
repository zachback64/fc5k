'use strict';
const state = document.querySelector('#host-state');
let invites = [];
async function api(path, body) {
  const response = await fetch(path, body === undefined ? {} : {method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify(body)});
  const result = await response.json();
  if (response.status === 401) {
    document.querySelector('#login').hidden = false;
    document.querySelector('#dashboard').hidden = true;
  }
  if (!response.ok) throw new Error(result.error || 'Request failed. Try again.');
  return result;
}
function node(tag, text, className) {
  const element = document.createElement(tag);
  element.textContent = text;
  if (className) element.className = className;
  return element;
}
function showShare(url, name) {
  document.querySelector('#share').hidden = false;
  document.querySelector('#share-hint').textContent = `Invitation for ${name}`;
  document.querySelector('#invite-message').value = `Hey ${name}! Come FC5K with us. December 26 in Elmhurst. Hot chocolate at 2, gun at 3, party after. Run, walk, or just hang. RSVP here: ${url}`;
}
function render() {
  const stats = document.querySelector('#stats');
  stats.replaceChildren();
  const count = status => invites.filter(i => i.status === status);
  [['Coming', count('yes').reduce((sum, i) => sum + i.party_size, 0)], ['Maybe', count('maybe').reduce((sum, i) => sum + i.party_size, 0)], ['Not answered', count('pending').length], ['Declined', count('no').length]].forEach(([label, number]) => {
    const card = node('div', '', 'stat'); card.append(node('strong', number), node('span', label)); stats.append(card);
  });
  const list = document.querySelector('#guest-list');
  const filter = document.querySelector('#filter').value;
  list.replaceChildren();
  const filtered = invites.filter(i => filter === 'all' || i.status === filter);
  if (!filtered.length) list.append(node('p', invites.length ? 'No invitations in this group.' : 'No invitations yet. Start with your first guest above.', 'empty-state'));
  filtered.forEach(invite => {
    const card = node('article', '', 'guest-row');
    const details = node('div', '', 'guest-details');
    details.append(node('h3', invite.name));
    const labels = {pending: 'Not answered', yes: 'Coming', maybe: 'Maybe', no: 'Can’t make it'};
    details.append(node('p', `${labels[invite.status]}${['yes', 'maybe'].includes(invite.status) ? ` · ${invite.party_size} people · ${invite.activity}` : ''}`, `response ${invite.status}`));
    if (invite.notes) details.append(node('p', invite.notes, 'guest-notes'));
    const button = node('button', 'Replace invite link', 'small-button');
    button.type = 'button';
    button.onclick = async () => {
      if (!confirm(`Replace ${invite.name}’s link? Their old link will stop working. Their RSVP will be kept.`)) return;
      button.disabled = true;
      try { const result = await api('/api/host/rotate', {id: invite.id}); showShare(result.url, invite.name); state.textContent = 'New invitation ready. The old link no longer works.'; document.querySelector('#share').scrollIntoView({behavior: 'smooth', block: 'center'}); }
      catch (error) { state.textContent = error.message; }
      finally { button.disabled = false; }
    };
    card.append(details, button); list.append(card);
  });
}
async function refresh() {
  const result = await api('/api/host/invites'); invites = result.invites;
  document.querySelector('#login').hidden = true;
  document.querySelector('#dashboard').hidden = false;
  render();
  const merch=await api('/api/host/merch');renderMerch(merch.responses);
}
document.querySelector('#login').onsubmit = async event => {
  event.preventDefault();
  const button = event.target.querySelector('button'); button.disabled = true;
  try { await api('/api/host/login', {password: event.target.elements.password.value}); event.target.reset(); await refresh(); state.textContent = 'Signed in.'; }
  catch (error) { state.textContent = error.message; }
  finally { button.disabled = false; }
};
document.querySelector('#create-invite').onsubmit = async event => {
  event.preventDefault();
  const form = event.target, button = form.querySelector('button'); button.disabled = true;
  try { const result = await api('/api/host/invites', {name: form.elements.name.value, max_guests: Number(form.elements.max_guests.value)}); showShare(result.url, result.name); form.reset(); await refresh(); state.textContent = 'Invitation created. Copy the message to share it.'; }
  catch (error) { state.textContent = error.message; }
  finally { button.disabled = false; }
};
document.querySelector('#copy-invite').onclick = async () => {
  const field = document.querySelector('#invite-message');
  try { await navigator.clipboard.writeText(field.value); state.textContent = 'Invitation copied.'; }
  catch { field.focus(); field.select(); state.textContent = 'Select and copy the invitation above.'; }
};
document.querySelector('#filter').onchange = render;
document.querySelector('#refresh').onclick = () => refresh().then(() => {state.textContent = 'Guest list refreshed.';}).catch(error => {state.textContent = error.message;});
document.querySelector('#logout').onclick = async () => {
  try { await api('/api/host/logout', {}); location.reload(); }
  catch (error) { state.textContent = error.message; }
};
refresh().catch(error => {state.textContent = error.message;});

function renderMerch(responses) {
  const names={tee:'T-shirt',longsleeve:'Long-sleeve shirt',hoodie:'Hoodie',beanie:'Beanie',none:'No merch'};
  const budgets={'25':'Up to $25','40':'Up to $40','60':'Up to $60',over60:'Over $60',unsure:'Not sure'};
  const summary=document.querySelector('#merch-summary');summary.replaceChildren();
  for(const [id,name] of Object.entries(names)) {
    const votes=responses.filter(r=>r.favorite===id).length;
    const quantity=responses.reduce((sum,r)=>sum+r.items.filter(i=>i.product===id).reduce((s,i)=>s+i.quantity,0),0);
    summary.append(node('p',`${name}: ${votes} ${votes===1?'vote':'votes'}${id==='none'?'':` · ${quantity} ${quantity===1?'unit':'units'} requested`}`));
  }
  const sizes={};for(const r of responses)for(const i of r.items){const key=`${names[i.product]} / ${i.size}`;sizes[key]=(sizes[key]||0)+i.quantity;}
  if(Object.keys(sizes).length)summary.append(node('p','Size totals: '+Object.entries(sizes).map(([key,n])=>`${key}: ${n}`).join(' · ')));
  const wrapper=document.querySelector('#merch-responses');wrapper.replaceChildren();
  if(!responses.length){wrapper.append(node('p','No merch responses yet.'));return;}
  const table=node('table','', 'merch-table'),head=node('thead',''),tr=node('tr','');
  for(const label of ['Guest','Vote / budget','Reservations','Email'])tr.append(node('th',label));head.append(tr);table.append(head);
  const body=node('tbody','');for(const r of responses){const row=node('tr','');for(const value of [r.name,`${names[r.favorite]} · ${budgets[r.budget]}`,r.items.map(i=>`${i.quantity} × ${names[i.product]} / ${i.size}`).join(', ')||'None',r.email||'—'])row.append(node('td',value));body.append(row);}table.append(body);wrapper.append(table);
}
