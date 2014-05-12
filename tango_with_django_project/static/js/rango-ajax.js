$(document).ready(function(){

	$('#likes').click(function(){
		var catid = $(this).attr("data-catid");
		$.get('/rango/like_category/', { category_id: catid }, function(data){
			    $('#like_count').html(data);
			    //$('#likes').hide();
			    $('#likes').addClass("disabled");
		    });
	    });
	$('.rango-add').click(function(){
		var catid = $(this).attr("data-catid");
		var title = $(this).attr("data-title");
		var url = $(this).attr("data-url");
	        var me = $(this)
	        $.get('/rango/auto_add_page/', { category_id: catid, title: title, url: url }, function(data){
			$('#page').html(data);
			me.hide();
		    });
	    });
 
	$('#suggestion').keyup(function(){
		var query;
		query = $(this).val();
		$.get('/rango/suggest_category/', { suggestion: query }, function(data){
			$('#cats').html(data);
		    });
	    });
    });
