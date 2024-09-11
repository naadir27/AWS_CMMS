document.addEventListener("DOMContentLoaded", function() {
    const passwordInput = document.getElementById('inputPassword');
    const confirmPasswordInput = document.getElementById('confirmPassword');
    const lengthCriteria = document.getElementById('length');
    const lowercaseCriteria = document.getElementById('lowercase');
    const uppercaseCriteria = document.getElementById('uppercase');
    const digitCriteria = document.getElementById('digit');
    const specialCriteria = document.getElementById('special');
    const matchCriteria = document.getElementById('match');

    function validatePassword() {
        const password = passwordInput.value;
        const confirmPassword = confirmPasswordInput.value;

        // Check the length
        if (password.length >= 8) {
            lengthCriteria.classList.remove('invalid');
            lengthCriteria.classList.add('valid');
        } else {
            lengthCriteria.classList.remove('valid');
            lengthCriteria.classList.add('invalid');
        }

        // Check for lowercase letter
        if (/[a-z]/.test(password)) {
            lowercaseCriteria.classList.remove('invalid');
            lowercaseCriteria.classList.add('valid');
        } else {
            lowercaseCriteria.classList.remove('valid');
            lowercaseCriteria.classList.add('invalid');
        }

        // Check for uppercase letter
        if (/[A-Z]/.test(password)) {
            uppercaseCriteria.classList.remove('invalid');
            uppercaseCriteria.classList.add('valid');
        } else {
            uppercaseCriteria.classList.remove('valid');
            uppercaseCriteria.classList.add('invalid');
        }

        // Check for digit
        if (/\d/.test(password)) {
            digitCriteria.classList.remove('invalid');
            digitCriteria.classList.add('valid');
        } else {
            digitCriteria.classList.remove('valid');
            digitCriteria.classList.add('invalid');
        }

        // Check for special character
        if (/[!@#$%^&*(),.?":{}|<>]/.test(password)) {
            specialCriteria.classList.remove('invalid');
            specialCriteria.classList.add('valid');
        } else {
            specialCriteria.classList.remove('valid');
            specialCriteria.classList.add('invalid');
        }

        // Check if passwords match
        if (password === confirmPassword) {
            matchCriteria.classList.remove('invalid');
            matchCriteria.classList.add('valid');
        } else {
            matchCriteria.classList.remove('valid');
            matchCriteria.classList.add('invalid');
        }
    }

    passwordInput.addEventListener('input', validatePassword);
    confirmPasswordInput.addEventListener('input', validatePassword);
});
