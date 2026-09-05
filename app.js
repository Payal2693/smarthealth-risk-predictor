document.addEventListener("DOMContentLoaded", function () {
    var alerts = document.querySelectorAll(".alert");
    alerts.forEach(function (alertEl) {
        setTimeout(function () {
            var bsAlert = bootstrap.Alert.getOrCreateInstance(alertEl);
            if (bsAlert) bsAlert.close();
        }, 5000);
    });
});
