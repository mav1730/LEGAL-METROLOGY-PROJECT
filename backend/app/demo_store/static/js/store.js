/* DemoMart gallery + UI helpers */
(function () {
  var main = document.getElementById("main-image");
  var thumbs = document.getElementById("thumbs");
  if (!main || !thumbs) return;

  thumbs.addEventListener("click", function (e) {
    var t = e.target;
    if (t.tagName !== "IMG") return;
    var src = t.getAttribute("data-full") || t.getAttribute("src");
    main.setAttribute("src", src);
    thumbs.querySelectorAll("img").forEach(function (img) {
      img.classList.remove("active");
    });
    t.classList.add("active");
  });
})();
