document.addEventListener('DOMContentLoaded', () => {
  const cid  = Number(document.documentElement.dataset.cid);
  const API  = '/api/cases';

  async function load() {
    const res = await fetch(`${API}/${cid}`);
    const d   = await res.json();
    document.getElementById('status').textContent = d.status;
    document.getElementById('statusSel').value    = d.status;
  }

  document.getElementById('chgBtn').addEventListener('click', async () => {
    const newStatus = document.getElementById('statusSel').value;
    await fetch(`${API}/bulk`, {
      method: 'PATCH',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ ids: [cid], new_status: newStatus })
    });
    await load();
    alert('변경 완료!');
  });

  load();
});
