document.addEventListener('DOMContentLoaded', () => {

  // 상태 변경
  document.getElementById('change-status').onclick = async () => {
    const code = document.getElementById('new-status').value;
    const res  = await fetch(`/api/cases/${window.CASE_ID}/status`, {
      method : 'PATCH',
      headers: { 'Content-Type': 'application/json' },
      body   : JSON.stringify({ status: code })
    });
    if (res.ok) location.reload();
    else alert('상태 변경 실패');
  };

  // 라벨 재출력 (프린터 연결 전까지는 로그만)
  document.getElementById('print-label').onclick = async () => {
    const res = await fetch(`/api/cases/${window.CASE_ID}/print_label`, { method: 'POST' });
    alert(res.ok ? '프린터로 전송!' : '출력 실패');
  };

  // 파일 목록 가져오기
  fetch(`/api/cases/${window.CASE_ID}/files`)
    .then(r => r.json())
    .then(files => {
      const tbody = document.querySelector('#file-table tbody');
      files.forEach((f, i) => {
        tbody.insertAdjacentHTML('beforeend', `
          <tr>
            <td>${i + 1}</td>
            <td>${f.filename}</td>
            <td>${new Date(f.created_at).toLocaleString()}</td>
            <td><a href="/api/files/${f.id}/download" target="_blank">⬇</a></td>
          </tr>`);
      });
    });
});
