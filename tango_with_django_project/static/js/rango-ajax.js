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
		var catid;
		catid = $(this).attr("data-catid");
		$.get('/rango/auto_add_page/', { category_id: catid }, function(data){
			$('#page').html(data);
			$('.rango-add').addClass("disabled");
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
