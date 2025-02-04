        function moveToNext(index) {
            let currentInput = document.getElementById(`otp-${index}`);
            let nextInput = document.getElementById(`otp-${index + 1}`);
            let prevInput = document.getElementById(`otp-${index - 1}`);
            if (currentInput.value.length === 1 && nextInput) {
                nextInput.focus();
            }
            currentInput.addEventListener("keydown", function (event) {
                if (event.key === "Backspace" && currentInput.value === "" && prevInput) {
                    prevInput.focus();
                }
            });
        }
