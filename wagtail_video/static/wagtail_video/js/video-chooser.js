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
                            data: {q: $('#id_q').val()},
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
                    videoTitle.text(videoData.title)
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