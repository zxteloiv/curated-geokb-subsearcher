
if (typeof jQuery === "undefined") {
    throw new Error("jQuery lib is missing.");
}

var handle_submit = function() {
    var query = $("#query").val();
    var domain = $('#domain').val();
    var city = $('#city').val();
    var sex = $('#feature_sex').val();
    var age = $('#feature_age').val();
    var time = $('#time').val();

    $.ajax('/s', {
        method: "GET",
        dataType: "json",
        data: {
            q: query,
            domain: domain,
            city: city,
            sex: sex,
            age: age,
            time: time,
            lat: 39.983424,
            lng: 116.322987,
        },
        success: function(data, state, jqXHR) {
            if (!data || !('errno' in data) || !('errmsg' in data)) {
                console.log("returned data is not valid.");
                $('#searchresult').text('').append($('<span>').addClass('label label-warning').text(
                    'invalid data received'
                ));
                return;
            }

            if (data.errno > 0) {
                console.log("server error: " + data.errno + "\n" + data.errmsg);
                if (data.errno === 1) {
                    $('#searchresult').text('').append($('<span>')
                        .addClass('label label-danger').text( data.errmsg ));
                } else {
                    $('#searchresult').text('').append($('<span>').addClass('label label-warning').text(
                        'Sorry, we can not understand your question.'
                    ));
                }
                return;
            }

            render_data(data.data);
        },
        error: function(jqXHR, state, err) {
            console.log(state + ": answer server api error\n" + err)
        }
    });

    return false;
};

var render_data = function(pois) {
    $("#searchresult").html("");
    var poi_fieldnames = [
        "名称", "地址", "简介",
        "分店", "营业时间", "电话",
        "popularity",
        "门票价格", "服务评分", "环境评分",
        '推荐菜品', '人均消费',
        '入离店时间', '联系方式', '每晚最低价格',
        '酒店设施','房间设施','酒店服务'
    ];
    var rename_fields = { popularity: '流行程度' };

    pois.forEach(function(poi) {
        var row = $("<div>").addClass("row");

        poi_fieldnames.forEach(function(field) {
            if (!poi.hasOwnProperty(field)) { return; }
            var value = poi[field];

            if (!value || (value.trim && value.trim() === "")) { return; }

            var key_span = $('<span>').addClass('col-xs-2');
            key_span.text(rename_fields.hasOwnProperty(field) ? rename_fields[field] : field);
            var val_span = $('<span>').addClass('col-xs-10');
            val_span.text(value);

            row.append(key_span);
            row.append(val_span);
            row.append('<br>');

        });

        $("#searchresult").append(row);
        $("#searchresult").append("<hr>");
    });

    if (pois.length === 0) {
        $("#searchresult").text('')
            .append($('<span>').addClass('label-info label').text('No result found.'));
    }
};

+function($){
    $("#searchform").submit(handle_submit);
}(jQuery);

