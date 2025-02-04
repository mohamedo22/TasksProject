document.addEventListener("DOMContentLoaded", function () {
        const form = document.querySelector("form");
        const oldPassword = document.getElementById("oldPassword");
        const newPassword = document.getElementById("newPassword");
        const confirmPassword = document.getElementById("confirmPassword");

        form.addEventListener("submit", function (event) {
            event.preventDefault();

            const passwordPattern = /^(?=.*\d)(?=.*[!@#$%^&*()_+])[A-Za-z\d!@#$%^&*()_+\s]{8,}$/;

            if (!passwordPattern.test(newPassword.value)) {
                Swal.fire({
                    icon: "error",
                    title: "Invalid Password",
                    text: "Password must be at least 8 characters long and include at least one number and one special character.",
                });
                return;
            }

            if (newPassword.value !== confirmPassword.value) {
                Swal.fire({
                    icon: "error",
                    title: "Passwords Do Not Match",
                    text: "Please make sure the new password and confirm password are the same.",
                });
                return;
            }

            form.submit();
        });
    });
function togglePassword(inputId, iconId) {
            let input = document.getElementById(inputId);
            let icon = document.getElementById(iconId);

            if (input.type === "password") {
                input.type = "text";
                icon.classList.replace("fa-eye-slash","fa-eye" );
            } else {
                input.type = "password";
                icon.classList.replace("fa-eye","fa-eye-slash" );
            }
        }