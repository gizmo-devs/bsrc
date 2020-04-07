$(document).ready(function(){
    $('.updateable').click(function() {
        clear_score_form();
        var score_id = $(this).attr('data-shot-id').toString();
        var shooter_name  = $(this).attr('data-name');
        $('#round_header_num').text($(this).attr('data-round'));
        console.log(score_id)
        if (score_id!=('None','')) {
            $.get("/round_result/" + score_id, function(data) {
                console.log(data);
                var round = data.round;
                $('#score_id').val(score_id);
                $('#competition_id').val(data.competition_id);
                $('#user_id').val(data.user_id);
                $('#compTeam_id').val(data.compTeam_id);
                $('#shooter_name').val(shooter_name);
                $('#estimated').val(data.estimated);
                $('#round').val(data.round);
                $('#actual').val(data.result);
                $('#date_shot').val(date_to_yyyy_mm_dd(data.completed));
            });
        } else {
            var u_id = $(this).attr('data-user-id');
            var c_id = $(this).attr('data-comp-id');
            var round = $(this).attr('data-round');
            var compTeam_id = $(this).attr('data-uteam-id');

            $('#compTeam_id').val(compTeam_id);
            $('#competition_id').val(c_id);
            $('#user_id').val(u_id);
            $('#shooter_name').val(shooter_name);
            $('#estimated').val(0);
            $('#actual').val(0);
            $('#round').val(round);
            //$('#date_shot').val();
            //$('#shooter_name').val(shooter_name);
        }

        $("#add_score").modal('show');
        $('#actual').select();
     });

    function clear_score_form() {
        $('#score_form').trigger('reset');
        return;
    }

    function date_to_yyyy_mm_dd(date){
        var d = new Date(date)
        y = d.getFullYear();
        m = ("0" + (d.getMonth() + 1)).slice(-2);
        d = ("0" + d.getDate()).slice(-2);

        return y + "-" + m + "-" + d
    }

    $('.user.table button').click(function(e) {
        var row = $(this.closest('tr'))
        var u_id = row.children('td').first().html()
        window.location.href = ('/user/' + u_id)
    });

    $('.user.table td:first-child').click(function(e) {
        var row = $(this.closest('tr'))
        var u_id = row.children('td').first().html()
        window.location.href = ('/user/' + u_id + '/stats')
    });

//	//new_member = '<div class="form-group"><label for="Member">Member</label><select class="form-control member_selection" ><option selected disabled>Please Select</option><option>Craig</option><option>Mike</option><option>Dave</option></select></div>'
//
//	$("#add_member").on({
//		click: function(event){
//		     event.preventDefault();
//			$("div#members").append(new_member);
//			calc_members();
//		},
//		change: function(){
//			calc_members();
//		}
//	});
//	$("#remove_last").on({
//		click: function(event){
//		    event.preventDefault();
//			$("div#members .form-group:last").remove();
//			calc_members();
//		},
//		change: function(){
//			calc_members();
//		}
//	});
//	$('#team').submit(function() {
//        calc_members();
//    });
//	function calc_members() {
//		var n = 0;
//		jQuery.each($("select"), function () {
//			if ($(this).children("option:selected").val() !== "Please Select") {
//				n++;
//			}
//		});
//		$("#team_size").val(n)
//	}

$(function() {
    $('[data-toggle="popover"]').popover()
});
});