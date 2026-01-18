// Prevent duplicate initialization
if (typeof butterflySwiper === 'undefined') {
  var butterflySwiper = null;
}

if (butterflySwiper) {
  butterflySwiper.destroy(true, true);
  butterflySwiper = null;
}

var butterflySwiper = new Swiper('.blog-slider', {
    passiveListeners: true,
    spaceBetween: 0,
    effect: 'slide',
    speed: 600,
    loop: true,
    autoplay: {
      disableOnInteraction: false,
      delay: 5000
    },
    mousewheel: {
        forceToAxis: true,
        sensitivity: 1,
        thresholdDelta: 50,
        eventsTarget: '.blog-slider'
    },
    // Removed observer for performance
    // observer: true, 
    // observeParents: true,
    pagination: {
      el: '.blog-slider__pagination',
      clickable: true,
    },
    navigation:{nextEl:".swiper-button-next",prevEl:".swiper-button-prev"}
});

// Optional: Pause on hover
var comtainer = document.getElementById('swiper_container');
if (comtainer) {
  comtainer.onmouseenter = function() {
    if(butterflySwiper) butterflySwiper.autoplay.stop();
  };
  comtainer.onmouseleave = function() {
    if(butterflySwiper) butterflySwiper.autoplay.start();
  };
}