let formPwd = $("#formPassword");
let formConfPwd = $("#formConfPassword");
let pwd_match_warning = $(".pwd-match-warning");
let pwd_len_warning = $(".pwd-len-warning");
let btn = $(".btn");

formPwd.on("input", function (e) {
    if (this.value !== formConfPwd.val()) {
        pwd_match_warning.removeClass("d-none");
    } else {
        pwd_match_warning.addClass("d-none");
    }
    if (this.value.length < 8) {
        pwd_len_warning.removeClass("d-none");
    } else {
        pwd_len_warning.addClass("d-none");
    }
});

formConfPwd.on("input", function (e) {
    if (this.value !== formPwd.val()) {
        pwd_match_warning.removeClass("d-none");
    } else {
        pwd_match_warning.addClass("d-none");
    }
});

$(".text-input").each(function () {
    $(this).on("input", function (e) {
        let allFilled = true;
        $(".text-input").each(function () {
            if ($(this).val() === "") {
                allFilled = false;
            }
        });
        if (
            allFilled &&
            formPwd.val() === formConfPwd.val() &&
            formPwd.val().length >= 8
        ) {
            btn.removeAttr("disabled");
        } else {
            btn.attr("disabled", "true");
        }
    });
});
