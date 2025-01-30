let select = document.getElementById('userPermission');
let adminRoleContainer = document.getElementById('adminRoleContainer');
let gradeContainer = document.getElementById('gradeContainer');
let firstStudentRoleContainer = document.getElementById('firstStudentRoleContainer');
let secondStudentRoleContainer = document.getElementById('secondStudentRoleContainer');

select.onchange = function () {
    if (select.value === "student") {
        adminRoleContainer.style.display = "none";
        gradeContainer.style.display = "block";
        firstStudentRoleContainer.style.display = "block";
        secondStudentRoleContainer.style.display = "block";
    }
    else {
        adminRoleContainer.style.display = "block";
        gradeContainer.style.display = "none";
        firstStudentRoleContainer.style.display = "none";
        secondStudentRoleContainer.style.display = "none";
    }
};
