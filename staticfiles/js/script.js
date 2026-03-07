document.querySelectorAll('.delete-form').forEach(form => {
    form.addEventListener('submit', function(e) {
        e.preventDefault();
        Swal.fire({
            title: 'Are you sure?',
            text: 'This lesson will be permanently deleted.',
            icon: 'warning',
            showCancelButton: true,
            confirmButtonText: 'Yes, delete it',
            cancelButtonText: 'Cancel',
            confirmButtonColor: '#C8793A',
            cancelButtonColor: '#2E5FA3',
        }).then((result) => {
            if (result.isConfirmed) {
                form.submit();
            }
        });
    });
});


document.addEventListener("DOMContentLoaded", function () {
    const messages = document.querySelectorAll(".messages li");
    messages.forEach(function (msg) {
        const isError = msg.classList.contains("error");
        Swal.fire({
            icon: isError ? "error" : "success",
            title: isError ? "Error" : "Success",
            text: msg.textContent.trim(),
            timer: 3000,
            showConfirmButton: false,
        });
    });
     document.querySelectorAll('.errorlist').forEach(function (errorList) {
        errorList.querySelectorAll('li').forEach(function (li) {
            Swal.fire({
                icon: 'error',
                title: 'Conflict',
                text: li.textContent.trim(),
                confirmButtonColor: '#2E5FA3',
            });
        });
    });
});