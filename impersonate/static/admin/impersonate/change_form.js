$( document ).ready(function() {
    $('a.darken-3').click(function () {
        localStorage.removeItem('token');
        localStorage.removeItem('userDetails');
    });
    $('a.lighten-3').click(function () {
        const userDetails = {
            "email": this.dataset.email,
            "pk": this.dataset.pk,
            "account": this.dataset.account,
            "account_status": this.dataset.status,
            "phone": this.dataset.phone,
            "first_name": this.dataset.first_name,
            "last_name": this.dataset.last_name
        };
        localStorage.setItem('token', this.dataset.token);
        localStorage.setItem('userDetails', JSON.stringify(userDetails));
    });
});
