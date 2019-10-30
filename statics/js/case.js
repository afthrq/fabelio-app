var get_pid_try_count = 0;
$('.btn-case').click(function (event) {
    event.preventDefault();
    var url = $('.link-input').val().toLowerCase();
    var $alert = $('.alert-danger');
    var $err = $('.error-message');

    if (url === "" && url.trim().length === 0){
        $err.html("Input should not be empty");
        if (!$alert.hasClass("show")){
            $alert.addClass("show");
        }
        return false;
    } else if (url.indexOf("fabelio.com") === -1){
        $err.html("Not a valid Fabelio link");
        if (!$alert.hasClass("show")){
            $alert.addClass("show");
        }
        return false;
    }

    $('body').loading();
    var status;
    var pid;
    var uuid;
    $.ajax({
        type: 'POST',
        url: '/urlcheck/',
        data: $('#search-form').serialize(),
        success: function(response) {
            try {
                if (response.status === true){
                    status = true;
                    pid = response.pid;
                } else {
                    status = false;
                    uuid = response.uuid;
                }
            } catch(e) {
                $err.html("Error when connecting to server, please try again");
                if (!$alert.hasClass("show")){
                    $alert.addClass("show");
                }
                $('body').loading('stop');
                return false;
            }
        },
        failed: function() {
            $err.html("Error when processing url, please try again");
            if (!$alert.hasClass("show")){
                $alert.addClass("show");
            }
            $('body').loading('stop');
            return false;
        },
        complete: function () {
            if (status === true){
                window.location = '/product/' + pid;
                return true;
            } else {
                $('.uuid-field').val(uuid);
                get_pid();
                return true;
            }
        },
        statusCode: {
            500: function() {
                $err.html("Error when processing url, please try again");
                if (!$alert.hasClass("show")){
                    $alert.addClass("show");
                }
                $('body').loading('stop');
                return false;
            }
        }
    });
});

function get_pid() {
    var $uuid = $('.uuid-field');
    var uuid = $uuid.val();

    var $alert = $('.alert-danger');
    var $err = $('.error-message');
    $.ajax({
        type: 'POST',
        url: '/getpid/',
        data:  $('#get-pid-form').serialize(),
        tryCount: get_pid_try_count,
        retryLimit: 3,
        success: function(response) {
            try {
                get_pid_try_count = 0;
                pid = response.pid;
                window.location = '/product/' + pid;
                return true;
            } catch(e) {
                return false;
            }
        },
        error : function(response) {
            if (response.status === 404) {
                get_pid_try_count++;
                if (get_pid_try_count <= this.retryLimit) {
                    setTimeout(function () {
                        get_pid(uuid);
                    }, 2500);
                } else {
                    get_pid_try_count = 0;
                    $err.html("Error when processing url, please try again");
                    if (!$alert.hasClass("show")){
                        $alert.addClass("show");
                    }
                    $('body').loading('stop');
                    return false;
                }
            }
        }
    });
}