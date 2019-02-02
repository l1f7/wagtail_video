$(function() {

  function populateTitle() {
    var fileWidget = $('#id_mp4');
    fileWidget.on('change', function () {
      var titleWidget = $('#id_title');
      var title = titleWidget.val();
      if (title === '') {
        // The file widget value example: `C:\fakepath\image.jpg`
        var parts = fileWidget.val().split('\\');
        var fileName = parts[parts.length - 1].replace(/\.[^/.]+$/, "");
        titleWidget.val(fileName);
      }
    });
  }

  populateTitle();

});
