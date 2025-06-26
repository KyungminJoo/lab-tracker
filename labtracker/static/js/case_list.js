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
            <td>${c.name}</td>            <!-- ★ 케이스 이름 -->
            <td>${c.status}</td>
            <td>${new Date(c.updated_at).toLocaleString()}</td>
          </tr>`);
      });
    });
});