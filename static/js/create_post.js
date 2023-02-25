let btn = $(".btn");

$(".text-input").each(function () {
    console.log("hello")
    $(this).on("input", function (e) {
        let allFilled = true;
        $(".text-input").each(function () {
            if ($(this).val() === "") {
                allFilled = false;
            }
        });
        if (allFilled) {
            btn.removeAttr("disabled");
        } else {
            btn.attr("disabled", "true");
        }
    });
});
