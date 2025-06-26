document.addEventListener('DOMContentLoaded', () => {

  // 상태 변경
  document.getElementById('change-status').onclick = async () => {
    const code = document.getElementById('new-status').value;
    const res  = await fetch(`/api/cases/${window.CASE_ID}/status`, {
      method : 'PATCH',
      headers: { 'Content-Type': 'application/json' },
      body   : JSON.stringify({ status: code })
    });
    const result = await res.json();
    if (res.ok) {
      document.getElementById('current-status').textContent = result.status;
    } else {
      alert('상태 변경 실패');
    }
  };

  // 라벨 재출력 (프린터 연결 전까지는 로그만)
  document.getElementById('print-label').onclick = async () => {
    const res = await fetch(`/api/cases/${window.CASE_ID}/print_label`, { method: 'POST' });
    alert(res.ok ? '프린터로 전송!' : '출력 실패');
  };

  // ▶ 케이스 목록 가져오기
  fetch('/api/cases')
    .then(r => r.json())
    .then(cases => {
      const tbody = document.querySelector('#case-tbody');
      cases.forEach((c, i) => {
        tbody.insertAdjacentHTML('beforeend', `
          <tr>
            <td><input type="checkbox" data-id="${c.id}"></td>
            <td>${c.id}</td>
            <td>${c.name}</td>          <!-- ★ 이름 열 추가 -->
            <td>${c.status}</td>
            <td>${new Date(c.updated_at).toLocaleString()}</td>
          </tr>`);
      });
    });
