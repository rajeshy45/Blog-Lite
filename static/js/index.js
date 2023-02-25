let show_pwd_check = $(".show-pwd-check");
let pwd = $(".pwd");
let add_new_comment = $("#add-new-comment");
let input_comment = $("#new-comment");

show_pwd_check.on("change", function (e) {
    if (this.checked) {
        pwd.attr("type", "text");
    } else {
        pwd.attr("type", "password");
    }
});

add_new_comment.on("click", function (e) {
    input_comment.focus();
});
