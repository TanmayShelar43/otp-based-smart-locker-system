document.getElementById("login-btn").addEventListener("click", function () {
    const username = document.getElementById("username").value;
    const password = document.getElementById("password").value;
    const errorMessage = document.getElementById("error-message");
  
    fetch('/verify_user', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            username: username,
            password: password
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.status === 'success') {
            document.getElementById("new-password").disabled = false;
            document.getElementById("confirm-password").disabled = false;
            document.getElementById("update-btn").disabled = false;
  
            errorMessage.textContent = data.message;
            errorMessage.style.color = "green";
        } else {
            errorMessage.textContent = data.message;
            errorMessage.style.color = "red";
        }
    })
    .catch(error => {
        console.error('Error:', error);
        errorMessage.textContent = "An error occurred.";
        errorMessage.style.color = "red";
    });
  });
  
  document.getElementById("update-btn").addEventListener("click", function (event) {
    event.preventDefault();
    
    const username = document.getElementById("username").value;
    const newPassword = document.getElementById("new-password").value;
    const confirmPassword = document.getElementById("confirm-password").value;
    const errorMessage = document.getElementById("error-message");
  
    if (newPassword !== confirmPassword) {
        errorMessage.textContent = "Passwords do not match!";
        errorMessage.style.color = "red";
        return;
    }
  
    fetch('/update_user', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            username: username,
            new_password: newPassword
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.status === 'success') {
            errorMessage.textContent = data.message;
            errorMessage.style.color = "green";
        } else {
            errorMessage.textContent = data.message;
            errorMessage.style.color = "red";
        }
    })
    .catch(error => {
        console.error('Error:', error);
        errorMessage.textContent = "An error occurred.";
        errorMessage.style.color = "red";
    });
  }); // Pin functionality removed
  