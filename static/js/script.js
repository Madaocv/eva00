/*------------------------------------------------------------------

 Project:	    My Desktop
 Version:	    1.0
 Last change:	08/09/2016
 Author:	    UKIE WEB

 -------------------------------------------------------------------*/

$(document).ready(function () {

    "use strict";

    /*
     ----------------------------------------------------------------------
     Progress Bars
     ----------------------------------------------------------------------
     */
    $('.progress-bar').each(function () {
        $(this).on('inview', function (event, isInView) {
            if (isInView) {
                $(this).css('width',  function() {
                    return ($(this).attr('aria-valuenow')+'%');
                });
            }
        });
    });


    /*
     ----------------------------------------------------------------------
     Magnific Popup
     ----------------------------------------------------------------------
     */
    if($("#container-portfolio").length) {
        $('#container-portfolio').mixItUp();
    }


    /*
     ----------------------------------------------------------------------
     Portfolio
     ----------------------------------------------------------------------
     */
    $('.popup-gallery').magnificPopup({
        delegate: ".popup-content",
        type: 'inline',
        midClick: true,
        gallery: {
            enabled: true, // set to true to enable gallery

            preload: [0, 2], // read about this option in next Lazy-loading section

            navigateByImgClick: true,

            arrowMarkup: '<button title="%title%" type="button" class="mfp-arrow mfp-arrow-%dir%"></button>', // markup of an arrow button

            tPrev: 'Previous (Left arrow key)', // title for left button
            tNext: 'Next (Right arrow key)', // title for right button
            tCounter: '<span class="mfp-counter">%curr% of %total%</span>' // markup of counter
        }


    });


    /*
     ----------------------------------------------------------------------
     Preloader
     ----------------------------------------------------------------------
     */
    $('body').jpreLoader();


    /*
     ----------------------------------------------------------------------
     Modal-popup
     ----------------------------------------------------------------------
     */
    $('.camera-icon').on('click',function(){

        $('.popup-photo').addClass('open-popup');
        return false;

    });

    $('.btn-close').on('click',function(){

        $('.popup-photo').removeClass('open-popup');
        return false;

    });

    $('body').each(function () {
        var $spy = $(this).scrollspy({ target: '#menu' });
    });


    /*
     ----------------------------------------------------------------------
     Fixed menu
     ----------------------------------------------------------------------
     */
    var $menu = $("#menu");

    $(window).scroll(function () {
        if ($(this).scrollTop() > 700 && $menu.hasClass("top-menu")) {
            $menu.removeClass("top-menu").addClass("menu-fixed");
        } else if ($(this).scrollTop() <= 700 && $menu.hasClass("menu-fixed")) {
            $menu.removeClass("menu-fixed").addClass("top-menu");
        }
    });//scroll


    /*
     ----------------------------------------------------------------------
     Scroll
     ----------------------------------------------------------------------
     */
    //Check to see if the window is top if not then display button
    $(window).scroll(function () {
        if ($(this).scrollTop() > 400) {
            $('.scroll-to-top').fadeIn();
        } else {
            $('.scroll-to-top').fadeOut();
        }
    });
    //Click event to scroll to top
    $().on('click',function () {
        $('html, body').animate({scrollTop: 0}, 800);
        return false;
    });


}); // End $(document).ready(function(){

