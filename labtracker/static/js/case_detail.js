console.log('▶ case_detail.js 로드됨 – data-case-id 활용');

document.addEventListener('DOMContentLoaded', () => {
  // DOM 로드 후에야 요소가 잡힙니다
  const container  = document.getElementById('case-detail');
  const caseId     = container?.dataset.caseId;
  const btnChange  = document.getElementById('change-status');
  const selectNew  = document.getElementById('new-status');
  const spanCurrent= document.getElementById('current-status');
  const btnPrint   = document.getElementById('print-label');
  const tbody      = document.querySelector('#file-table tbody');

  if (!caseId || !btnChange || !selectNew || !spanCurrent || !btnPrint || !tbody) {
    console.error('필수 요소를 찾을 수 없습니다:', {
      caseId, btnChange, selectNew, spanCurrent, btnPrint, tbody
    });
    return;
  }

  // 상태 PATCH
  btnChange.addEventListener('click', async () => {
    console.log('▶ 변경 버튼 클릭, CASE_ID=', caseId, '선택값=', selectNew.value);
    try {
      const res = await fetch(`/api/cases/${caseId}/status`, {
        method: 'PATCH',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ status: selectNew.value })
      });
      const result = await res.json();
      if (!res.ok) throw new Error(result.msg || res.statusText);

      // 실제 화면 갱신
      spanCurrent.textContent = result.status_label;
      selectNew.value        = result.status;
    } catch (err) {
      console.error('상태 변경 실패:', err);
      alert('상태 변경에 실패했습니다:\n' + err.message);
    }
  });

  // 라벨 재출력
  btnPrint.addEventListener('click', async () => {
    const res = await fetch(`/api/cases/${caseId}/print_label`, { method: 'POST' });
    alert(res.ok ? '프린터로 전송!' : '출력 실패');
  });

  // 파일 목록 로드
  (async function loadFiles() {
    try {
      const res   = await fetch(`/api/cases/${caseId}/files`);
      const files = await res.json();
      tbody.innerHTML = '';
      files.forEach((f, i) => {
        tbody.insertAdjacentHTML('beforeend', `
          <tr>
            <td>${i + 1}</td>
            <td>${f.filename}</td>
            <td>${formatKST(f.created_at)}</td>
            <td>
              <a class="btn btn-sm btn-outline-primary"
                 href="/api/files/${f.id}/download">다운로드</a>
            </td>
          </tr>`);
      });
    } catch (err) {
      console.error('파일 목록 로드 실패:', err);
    }
  })();
});

// KST 포맷 함수
function formatKST(iso) {
  if (!iso) return '';
  const utc  = new Date(iso);
  const tz   = new Date(utc.toLocaleString('ko-KR', { timeZone: 'Asia/Seoul' }));
  const yy   = String(tz.getFullYear()).slice(-2);
  const m    = tz.getMonth() + 1;
  const d    = tz.getDate();
  let   h    = tz.getHours();
  const ampm = h >= 12 ? '오후' : '오전';
  h = h % 12 || 12;
  const min = String(tz.getMinutes()).padStart(2, '0');
  return `${yy}/${m}/${d} ${ampm}${h}시${min}`;
}