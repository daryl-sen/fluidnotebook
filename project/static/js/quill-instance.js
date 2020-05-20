var toolbarOptions = [
  ['bold', 'italic', 'underline'],
  [{ 'header': [2, 3, 4, 5, false] }],
  ['code', 'code-block'],
  ['link'],
  [{ 'list': 'ordered'}, { 'list': 'bullet' }],
  ['clean'],
];

var quill = new Quill('#quillEditor', {
  modules: {
    toolbar: toolbarOptions
  },
  theme: 'snow'
});

// quill.root.innerHTML = document.querySelector('input[name=content]').value;
var form = document.querySelector('form');
form.onsubmit = function() {
  // Populate hidden form on submit
  var about = document.querySelector('input[name=content]');
  var editorContent = quill.root.innerHTML;
  about.value = editorContent;
};
