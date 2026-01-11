animation = r"""
(function () {
  // 중복 실행 방지 (리로드/핫리로드에서 유용)
  if (window.__gradioAnimationLoaded) return;
  window.__gradioAnimationLoaded = true;

  function createGradioAnimation() {
    var container = document.createElement('div');
    container.id = 'gradio-animation';
    container.style.fontSize = '2em';
    container.style.fontWeight = 'bold';
    container.style.textAlign = 'center';
    container.style.marginTop = '0px';
    container.style.marginBottom = '0px';

    var text = 'Objektify.xyz';
    for (var i = 0; i < text.length; i++) {
      (function(i){
        setTimeout(function(){
          var letter = document.createElement('span');
          letter.style.opacity = '0';
          letter.style.transition = 'opacity 0.5s';
          letter.innerText = text[i];

          container.appendChild(letter);

          setTimeout(function() {
            letter.style.opacity = '1';
          }, 50);
        }, i * 100); // 여기서 시간을 줄여서 글자 출력 속도를 빠르게 합니다
      })(i);
    }

    var gradioContainer = document.querySelector('.gradio-container');
    gradioContainer.insertBefore(container, gradioContainer.firstChild);

    setTimeout(function() {
      container.style.transition = 'all 2s';
      container.style.fontSize = '1.6em';
      container.style.letterSpacing = '0.1em';
    }, 3000);
  }

  function runWhenReady() {
    var gradioContainer = document.querySelector('.gradio-container');
    if (!gradioContainer) {
      requestAnimationFrame(runWhenReady);
      return;
    }
    createGradioAnimation();
  }

  runWhenReady();
})();
"""
