document.addEventListener('DOMContentLoaded', () => {
  // 상태 변경
  document.getElementById('change-status').onclick = async () => {
    const code = document.getElementById('new-status').value;
    const res = await fetch(`/api/cases/${window.CASE_ID}/status`, {
      method: 'PATCH',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ status: code })
    });
    const result = await res.json();
    if (res.ok) {
      document.getElementById('current-status').textContent = result.status;
    } else {
      alert('상태 변경 실패');
    }
  };

  // 라벨 재출력
  document.getElementById('print-label').onclick = async () => {
    const res = await fetch(`/api/cases/${window.CASE_ID}/print_label`, { method: 'POST' });
    alert(res.ok ? '프린터로 전송!' : '출력 실패');
  };

  // 파일 목록 로드
  async function loadFiles() {
    const res = await fetch(`/api/cases/${window.CASE_ID}/files`);
    const files = await res.json();
    const tbody = document.querySelector('#file-table tbody');
    tbody.innerHTML = '';
    files.forEach((f, i) => {
      tbody.insertAdjacentHTML('beforeend', `
        <tr>
          <td>${i + 1}</td>
          <td>${f.filename}</td>
          <td>${formatKST(f.created_at)}</td>
          <td><a class="btn btn-sm btn-outline-primary" href="/api/files/${f.id}/download">다운로드</a></td>
        </tr>
      `);
    });
  }

  loadFiles();
});

function formatKST(iso) {
  if (!iso) return '';
  const utc = new Date(iso);
  const tz = new Date(utc.toLocaleString('en-US', { timeZone: 'Asia/Seoul' }));
  const yy = String(tz.getFullYear()).slice(-2);
  const m = tz.getMonth() + 1;
  const d = tz.getDate();
  let h = tz.getHours();
  const ampm = h >= 12 ? '오후' : '오전';
  h = h % 12;
  if (h === 0) h = 12;
  const min = String(tz.getMinutes()).padStart(2, '0');
  return `${yy}/${m}/${d} ${ampm}${h}시${min}`;
}
