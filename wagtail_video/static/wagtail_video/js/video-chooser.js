function createVideoChooser(id) {
    var chooserElement = $('#' + id + '-chooser');
    var videoTitle = chooserElement.find('.title');
    var input = $('#' + id);
    var editLink = chooserElement.find('.edit-link');

    $('.action-choose', chooserElement).click(function() {
        ModalWorkflow({
            'url': window.chooserUrls.videoChooser,
            'onload': {
                'chooser': function(modal, jsonData) {
                    var searchUrl = $('form.video-search', modal.body).attr('action');

                    function ajaxifyLinks (context) {
                        $('.listing a', context).click(function() {
                            modal.loadUrl(this.href);
                            return false;
                        });

                        $('.pagination a', context).click(function() {
                            var page = this.getAttribute("data-page");
                            setPage(page);
                            return false;
                        });
                    }

                    function search() {
                        $.ajax({
                            url: searchUrl,
                            data: {
                              q: $('#id_q').val(),
                              collection_id: $('#collection_chooser_collection_id').val()
                            },
                            success: function(data, status) {
                                $('#search-results').html(data);
                                ajaxifyLinks($('#search-results'));
                            }
                        });
                        return false;
                    }

                    function setPage(page) {
                        if($('#id_q').val().length){
                            dataObj = {q: $('#id_q').val(), p: page};
                        }else{
                            dataObj = {p: page};
                        }

                        $.ajax({
                            url: searchUrl,
                            data: dataObj,
                            success: function(data, status) {
                                $('#search-results').html(data);
                                ajaxifyLinks($('#search-results'));
                            }
                        });
                        return false;
                    }

                    ajaxifyLinks(modal.body);


                    $('form.video-upload', modal.body).on('submit', function() {
                      var formdata = new FormData(this);

                      if ($('#id_title', modal.body).val() == '') {
                        var li = $('#id_title', modal.body).closest('li');
                        if (!li.hasClass('error')) {
                          li.addClass('error');
                          $('#id_title', modal.body).closest('.field-content').append('<p class="error-message"><span>This field is required.</span></p>')
                        }
                        setTimeout(cancelSpinner, 500);
                      } else {
                        $.ajax({
                          url: this.action,
                          data: formdata,
                          processData: false,
                          contentType: false,
                          type: 'POST',
                          dataType: 'text',
                          success: modal.loadResponseText,
                          error: function(response, textStatus, errorThrown) {
                            message = jsonData['error_message'] + '<br />' + errorThrown + ' - ' + response.status;
                            $('#upload').append(
                              '<div class="help-block help-critical">' +
                              '<strong>' + jsonData['error_label'] + ': </strong>' + message + '</div>');
                          }
                        });
                      }

                      return false;
                    });
                    $('#collection_chooser_collection_id').on('change', search);
                    $('form.video-search', modal.body).submit(search);

                    $('#id_q').on('input', function() {
                        clearTimeout($.data(this, 'timer'));
                        var wait = setTimeout(search, 200);
                        $(this).data('timer', wait);
                    });
                    $('a.suggested-tag').click(function() {
                        $('#id_q').val($(this).text());
                        search();
                        return false;
                    });

                    //{% url 'wagtailadmin_tag_autocomplete' as autocomplete_url %}

                    function populateTitle(context) {
                      // Note: There are two inputs with `#id_title` on the page.
                      // The page title and image title. Select the input inside the modal body.
                      var fileWidget = $('#id_mp4', context);
                      fileWidget.on('change', function () {
                        var titleWidget = $('#id_title', context);
                        var title = titleWidget.val();
                        if (title === '') {
                          // The file widget value example: `C:\fakepath\image.jpg`
                          var parts = fileWidget.val().split('\\');
                          var fileName = parts[parts.length - 1].replace(/\.[^/.]+$/, "");
                          titleWidget.val(fileName);
                        }
                      });
                    }

                    populateTitle(modal.body);

                    /* Add tag entry interface (with autocompletion) to the tag field of the embed video upload form */
                    $('#id_tags', modal.body).tagit({
                        autocomplete: {source: jsonData.autocomplete_url}
                    });
                },
                'video_chosen': function(modal, jsonData) {
                    modal.respond('videoChosen', jsonData.result);
                    modal.close();
                },
                'select_format': function(modal) {
                    $('form', modal.body).submit(function() {
                        var formdata = new FormData(this);

                        $.post(this.action, $(this).serialize(), function(response){
                            modal.loadResponseText(response);
                        }, 'text');

                        return false;
                    });
                },
            },
            'responses': {
                'videoChosen': function(videoData) {
                    input.val(videoData.id);
                    videoTitle.text(videoData.title);

                    var videoElement = chooserElement.find("video").get(0);
                    videoElement.innerHTML = '';
                    if (videoData.mp4_url) {
                      var source = document.createElement('source');
                      source.setAttribute('src', videoData.mp4_url);
                      source.setAttribute('type', "video/mp4");

                      videoElement.appendChild(source);
                      videoElement.load();
                    }
                    chooserElement.removeClass('blank');
                    editLink.attr('href', videoData.edit_link);
                }
            }
        });
    });

    $('.action-clear', chooserElement).click(function() {
        input.val('');
        chooserElement.addClass('blank');
    });
}
