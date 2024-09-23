    const inputPassword = document.getElementById('inputPassword');
    const confirmPassword = document.getElementById('confirmPassword');
    
    const lengthCriteria = document.getElementById('length');
    const lowercaseCriteria = document.getElementById('lowercase');
    const uppercaseCriteria = document.getElementById('uppercase');
    const digitCriteria = document.getElementById('digit');
    const specialCriteria = document.getElementById('special');
    const matchCriteria = document.getElementById('match');

    inputPassword.addEventListener('input', validatePassword);
    confirmPassword.addEventListener('input', validatePasswordMatch);

    function validatePassword() {
        const password = inputPassword.value;
        
        // Length
        if (password.length >= 8) {
            lengthCriteria.classList.add('valid');
            lengthCriteria.classList.remove('invalid');
        } else {
            lengthCriteria.classList.add('invalid');
            lengthCriteria.classList.remove('valid');
        }

        // Lowercase letter
        if (/[a-z]/.test(password)) {
            lowercaseCriteria.classList.add('valid');
            lowercaseCriteria.classList.remove('invalid');
        } else {
            lowercaseCriteria.classList.add('invalid');
            lowercaseCriteria.classList.remove('valid');
        }

        // Uppercase letter
        if (/[A-Z]/.test(password)) {
            uppercaseCriteria.classList.add('valid');
            uppercaseCriteria.classList.remove('invalid');
        } else {
            uppercaseCriteria.classList.add('invalid');
            uppercaseCriteria.classList.remove('valid');
        }

        // Digit
        if (/\d/.test(password)) {
            digitCriteria.classList.add('valid');
            digitCriteria.classList.remove('invalid');
        } else {
            digitCriteria.classList.add('invalid');
            digitCriteria.classList.remove('valid');
        }

        // Special character
        if (/[!@#$%^&*]/.test(password)) {
            specialCriteria.classList.add('valid');
            specialCriteria.classList.remove('invalid');
        } else {
            specialCriteria.classList.add('invalid');
            specialCriteria.classList.remove('valid');
        }

        // Check if passwords match
        validatePasswordMatch();
    }

    function validatePasswordMatch() {
        if (inputPassword.value === confirmPassword.value && inputPassword.value !== '') {
            matchCriteria.classList.add('valid');
            matchCriteria.classList.remove('invalid');
        } else {
            matchCriteria.classList.add('invalid');
            matchCriteria.classList.remove('valid');
        }
    }