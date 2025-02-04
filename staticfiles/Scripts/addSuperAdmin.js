let userName = document.getElementById('userName');
let nationalId = document.getElementById('nationalId');
let firstName = document.getElementById('firstName');
firstName.oninput = nationalId.oninput = function (value){
    let first = firstName.value.replace(/\s+/g, '');
    let id = nationalId.value.replace(/\s+/g, '');
    userName.value = first + id;

};
let dropArea = document.getElementById("dropArea");
let fileInput = document.getElementById("fileInput");
let fileText = document.getElementById("fileText");
dropArea.addEventListener("dragover", (event) => {
    event.preventDefault();
    dropArea.classList.add("border-blue-500");
});
dropArea.addEventListener("dragleave", () => {
    dropArea.classList.remove("border-blue-500");
});
dropArea.addEventListener("drop", (event) => {
    event.preventDefault();

    let file = event.dataTransfer.files[0];
    if (file) {
        fileText.innerText = `Uploaded: ${file.name}`;
    }
});
fileInput.addEventListener("change", () => {
    let file = fileInput.files[0];
    if (file) {
        fileText.innerText = `Uploaded: ${file.name}`;
        dropArea.classList.add("border-blue-500");
    }
});
