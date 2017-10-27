// MAKE THE PLOTS RESPONSIVE
(function() {
  var d3 = Plotly.d3;
  var WIDTH_IN_PERCENT_OF_PARENT = 100,
      HEIGHT_IN_PERCENT_OF_PARENT = 100;
  
  var gd3 = d3.selectAll(".responsive-plot")
      .style({
        width: WIDTH_IN_PERCENT_OF_PARENT + '%',
        'margin-left': (100 - WIDTH_IN_PERCENT_OF_PARENT) / 2 + '%',
        

      });

  var nodes_to_resize = gd3[0]; //not sure why but the goods are within a nested array
  window.onresize = function() {
    for (var i = 0; i < nodes_to_resize.length; i++) {
      Plotly.Plots.resize(nodes_to_resize[i]);
    }
  };
  
})();

(function() {
	$(document).ready(function() {
	  $(window).on("scroll", function() {
	    if ($(window).scrollTop() >= 70) {
	      $(".navbar").addClass("compressed");
	    } else {
	      $(".navbar").removeClass("compressed");
	    }
	  });
	});
})();


(function() {
    
    // Back to top
    var amountScrolled = 200;
    var amountScrolledNav = 25;

    $(window).scroll(function() {
      if ( $(window).scrollTop() > amountScrolled ) {
        $('button.back-to-top').addClass('show');
      } else {
        $('button.back-to-top').removeClass('show');
      }
    });

    $('button.back-to-top').click(function() {
      $('html, body').animate({
        scrollTop: 0
      }, 800);
      return false;
    });

})();

/*
(function() {

	var elementPosition = $('#rates').offset();

	console.log(elementPosition);

	$(window).scroll(function(){
	        if($(window).scrollTop() > elementPosition.top){
	              $('#rates').css('position','fixed').css('top','0').css('right','0')
	        } else {
	            $('#rates').css('position','static');
	        }    
	});

})();
*/