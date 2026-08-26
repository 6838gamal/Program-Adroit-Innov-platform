function toggleMenu() {
  const menu = document.getElementById('navMenu');
  if (menu) {
    menu.classList.toggle('navbar__menu--open');
  }
}

document.addEventListener('DOMContentLoaded', () => {
  const editor = document.getElementById('codeEditor');
  if (editor) {
    editor.addEventListener('keydown', (e) => {
      if (e.key === 'Tab') {
        e.preventDefault();
        const start = editor.selectionStart;
        const end = editor.selectionEnd;
        editor.value = editor.value.substring(0, start) + '    ' + editor.value.substring(end);
        editor.selectionStart = editor.selectionEnd = start + 4;
      }
    });
  }
});
