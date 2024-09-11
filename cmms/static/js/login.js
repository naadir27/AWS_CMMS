$(document).ready(function() {
    $('#loginForm').submit(function(event) {
        event.preventDefault();  // Prevent the form from submitting via the browser
        
        const formData = {
            email: $('#email').val(),
            password: $('#pass').val()
        };

        $.ajax({
            url: "{{ url_for('auth_forms.login') }}",
            type: 'POST',
            contentType: 'application/json',
            data: JSON.stringify(formData),
            success: function(response) {
                if (response.access_token) {
                    // Store the JWT token
                    localStorage.setItem('access_token', response.access_token);
                    
                    // Redirect to the 'redirect_user' route
                    window.location.href = "{{ url_for('auth_forms.redirect_user') }}?message=authenticated";
                }
            },
            error: function() {
                alert('Login failed. Please check your credentials and try again.');
            }
        });
    });
});