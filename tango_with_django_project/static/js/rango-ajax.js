$(document).ready(function(){

	$('#likes').click(function(){
		var catid;
		catid = $(this).attr("data-catid");
		$.get('/rango/like_category/', { category_id: catid }, function(data){
			    $('#like_count').html(data);
			    //$('#likes').hide();
			    $('#likes').addClass("disabled");
		    });
	    });
	$('.rango-add').click(function(){
		var catid, title, url
		catid = $(this).attr("data-catid");
		title = $(this).attr("data-title");
		url = $(this).attr("data-url");
	        $(this).addClass("disabled");
	        $.get('/rango/auto_add_page/', { category_id: catid, title: title, url: url}, function(data){
			$('#page').html(data);
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
