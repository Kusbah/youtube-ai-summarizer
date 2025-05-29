document.addEventListener("DOMContentLoaded", function () {
    const checkboxes = document.querySelectorAll(".compare-checkbox");
    const compareBtn = document.getElementById("compare-btn");
  
    function updateCompareButton() {
      const checkedCount = Array.from(checkboxes).filter(cb => cb.checked).length;
      compareBtn.disabled = checkedCount !== 2;
    }
  
    checkboxes.forEach(cb => cb.addEventListener("change", updateCompareButton));
  });
  


  document.addEventListener("DOMContentLoaded", function () {
    const checkboxes = document.querySelectorAll(".compare-checkbox");
    const compareBtn = document.getElementById("compare-btn");
    const compare1 = document.getElementById("compare1");
    const compare2 = document.getElementById("compare2");
  
    function updateCompareButton() {
      const selected = Array.from(checkboxes).filter(cb => cb.checked).map(cb => cb.value);
      
      compareBtn.disabled = selected.length !== 2;
  
      if (selected.length === 2) {
        compare1.value = selected[0];
        compare2.value = selected[1];
      } else {
        compare1.value = "";
        compare2.value = "";
      }
    }
  
    checkboxes.forEach(cb => cb.addEventListener("change", updateCompareButton));
  });

  
  