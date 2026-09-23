'use strict';
let token = location.hash.slice(1);
const form = document.querySelector('#rsvp-form');
const state = document.querySelector('#invite-state');
const attendance = document.querySelector('#attendance');
async function api(path, body) {
  const response = await fetch(path, {method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify(body)});
  const result = await response.json();
  if (!response.ok) throw new Error(result.error || 'Could not save. Please try again.');
  return result;
}
function syncAttendance() {
  attendance.hidden = form.elements.status.value === 'no';
}
form.addEventListener('change', syncAttendance);
form.addEventListener('submit', async event => {
  event.preventDefault();
  const button = form.querySelector('button[type="submit"]');
  button.disabled = true;
  state.textContent = 'Saving your RSVP…';
  const status = form.elements.status.value;
  const size = status === 'no' ? 0 : Number(form.elements.party_size.value);
  try {
    const result = await api(token ? '/api/rsvp' : '/api/public/rsvp', {token, name: form.elements.name.value, status, party_size: size, activity: form.elements.activity.value, notes: form.elements.notes.value});
    if (result.token) {
      token = result.token;
      history.replaceState(null, '', '#'+token);
      document.querySelector('#public-name').hidden = true;
      form.elements.name.required = false;
    }
    document.querySelector('#edit-link').value = location.href;
    state.textContent = 'RSVP saved.';
    document.querySelector('#saved h3').textContent = status === 'no' ? 'We’ll miss you.' : status === 'maybe' ? 'We’ll keep our fingers crossed.' : 'You’re on the list.';
    document.querySelector('#saved-summary').textContent = status === 'no' ? 'Thanks for letting us know. If plans change, come back here.' : `${status === 'maybe' ? 'Tentatively' : 'Confirmed'}: ${size} ${size === 1 ? 'person' : 'people'}. December 26, 2026. Gather at 2, gun at 3.`;
    form.hidden = true;
    document.querySelector('#saved').hidden = false;
    document.querySelector('#edit-rsvp').focus();
  } catch (error) { state.textContent = error.message; }
  finally { button.disabled = false; }
});
document.querySelector('#edit-rsvp').onclick = () => {
  document.querySelector('#saved').hidden = true;
  form.hidden = false;
  state.textContent = 'Make a change and save your RSVP again.';
  form.querySelector('input').focus();
};
(async () => {
  if (!token) {
    state.textContent = 'Everyone’s welcome. Let us know if you’re coming.';
    document.querySelector('#public-name').hidden = false;
    form.elements.name.required = true;
    for (let i = 1; i <= 20; i++) form.elements.party_size.add(new Option(String(i), String(i)));
    form.hidden = false;
    return;
  }
  try {
    const invite = await api('/api/invite', {token});
    document.querySelector('#invite-title').textContent = `You in, ${invite.name}?`;
    state.textContent = invite.status === 'pending' ? 'Good friends. Bad weather. Let us know if you’re coming.' : 'Welcome back. Your previous RSVP is below; update it anytime.';
    for (let i = 1; i <= invite.max_guests; i++) form.elements.party_size.add(new Option(String(i), String(i)));
    form.elements.party_size.value = String(invite.party_size || 1);
    form.elements.status.value = invite.status === 'pending' ? '' : invite.status;
    form.elements.activity.value = invite.activity;
    form.elements.notes.value = invite.notes;
    syncAttendance();
    form.hidden = false;
  } catch (error) { state.textContent = error instanceof TypeError ? 'Could not reach the RSVP service. Please try again shortly.' : error.message; }
})();

document.querySelector('#copy-link').onclick = async () => {
  const field = document.querySelector('#edit-link');
  try { await navigator.clipboard.writeText(field.value); state.textContent = 'Your private link is copied.'; }
  catch { field.focus(); field.select(); state.textContent = 'Select and copy your link below.'; }
};
