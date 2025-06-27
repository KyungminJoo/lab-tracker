// labtracker/static/js/case_list.js
// “케이스 상태 일괄 변경” 페이지용 스크립트

document.addEventListener('DOMContentLoaded', () => {
  // ▸ 케이스 목록 가져와서 테이블에 삽입
  fetch('/api/cases')
    .then(r => r.json())
    .then(cases => {
      const tbody = document.querySelector('#case-tbody');   // <tbody id="case-tbody">
      cases.forEach((c, i) => {
        tbody.insertAdjacentHTML('beforeend', `
          <tr>
            <td><input type="checkbox" data-id="${c.id}"></td>
            <td>${c.id}</td>
            <td>${c.case_id}</td>
            <td>${c.status}</td>
            <td>${formatKST(c.updated_at)}</td>
          </tr>`);
      });
    });
});

function formatKST(iso) {
  if (!iso) return '';
  const utc = new Date(iso);
  const tz = new Date(utc.toLocaleString('ko-KR', { timeZone: 'Asia/Seoul' }));
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
