(function($){

    function HistoryPerspective(options) {
		var old_callback = options.callback || function() {};

		options.callback = function() {
			var self = this;

			// first time page is rendered
        	$('#make-diff-button').click(function() {
				self.makeDiff();
			});

			$('#tag-changeset-button').click(function() {
				self.showTagForm();
			});

	        $('#doc-revert-button').click(function() {
	            self.revertDocumentToVersion();
	        });

			$('#open-preview-button').click(function(event) {
				var selected = $('#changes-list .entry.selected');

				if (selected.length != 1) {
        		    window.alert("Wybierz dokładnie *jedną* wersję.");
            		return;
		        }

				var version = parseInt($("*[data-stub-value='version']", selected[0]).text());
				window.open($(this).attr('data-basehref') + "?revision=" + version);

				event.preventDefault();
			});

        	$('#changes-list .entry').live('click', function(){
            	var $this = $(this);

            	var selected_count = $("#changes-list .entry.selected").length;

            	if ($this.hasClass('selected')) {
                	$this.removeClass('selected');
                	selected_count -= 1;
            	}
            	else {
            	    if (selected_count  < 2) {
            	        $this.addClass('selected');
            	        selected_count += 1;
            	    };
            	};

            	$('#history-view-editor .toolbar button').attr('disabled', 'disabled').
            	    filter('*[data-enabled-when~=' + selected_count + '], *[data-enabled-when~=*]').
            	    attr('disabled', null);
        	});

    	    $('#changes-list span.tag').live('click', function(event){
        	    return false;
        	});

        	old_callback.call(this);
		}

		$.wiki.Perspective.call(this, options);
    };

    HistoryPerspective.prototype = new $.wiki.Perspective();

    HistoryPerspective.prototype.freezeState = function(){
        // must
    };

    HistoryPerspective.prototype.onEnter = function(success, failure){
        $.wiki.Perspective.prototype.onEnter.call(this);
        $.blockUI({
            message: 'Odświeżanie historii...'
        });

        return this.fetchHistory({
            success: function() {
                $.unblockUI();
                if (success) success();
            },
            failure: function() {
                $.unblockUI();
                if (failure) failure();
            }
        });
    };

	HistoryPerspective.prototype.showTagForm = function(){
		var selected = $('#changes-list .entry.selected');

		if (selected.length != 1) {
            window.alert("Musisz zaznaczyć dokładnie jedną wersję.");
            return;
        }

		var version = parseInt($("*[data-stub-value='version']", selected[0]).text());
		$.wiki.showDialog('#add_tag_dialog', {'revision': version});
	};

	HistoryPerspective.prototype.makeDiff = function() {
        var changelist = $('#changes-list');
        var selected = $('.entry.selected', changelist);

        if (selected.length != 2) {
            window.alert("Musisz zaznaczyć dokładnie dwie wersje do porównania.");
            return;
        }

        $.blockUI({
            message: 'Wczytywanie porównania...'
        });

		var rev_from = $("*[data-stub-value='version']", selected[1]).text();
		var rev_to =  $("*[data-stub-value='version']", selected[0]).text();

        return this.doc.fetchDiff({
            from: rev_from,
			to: rev_to,
            success: function(doc, data){
                var result = $.wiki.newTab(doc, ''+rev_from +' -> ' + rev_to, 'DiffPerspective');

				$(result.view).html(data);
				$.wiki.switchToTab(result.tab);
				$.unblockUI();
            },
            failure: function(doc){
                $.unblockUI();
            }
        });
    };
    
    HistoryPerspective.prototype.fetchHistory = function(params) {
        params = $.extend({}, params);

        return this.doc.fetchHistory({
            success: function(doc, data) {
                $('#history-view .message-box').hide();
                var changes_list = $('#changes-list');
                var $stub = $('#history-view .row-stub');
                changes_list.empty();

                var tags = $('select#id_addtag-tag option');

                $.each(data, function() {
                    $.wiki.renderStub({
                        container: changes_list,
                        stub: $stub,
                        data: this,
                        filters: {
                            tag: function(value) {
                                return tags.filter("*[value='"+value+"']").text();
                            }
                        }
                    });
                });

                if(params.success) params.success(doc, data);
            },
            failure: function(doc, message) {
                $('#history-view .message-box').html('Nie udało się odświeżyć historii:' + message).show();

                if(params.failure) params.failure(doc, message);
            }
       });
    };

    HistoryPerspective.prototype.revertDocumentToVersion = function(){
        var self = this;
        var selected = $('#changes-list .entry.selected');

        if (selected.length != 1) {
            window.alert("Musisz zaznaczyć dokładnie jedną wersję.");
            return;
        }

        var version = parseInt($("*[data-stub-value='version']", selected[0]).text());
        console.log(version);
        this.doc.revert({
            'revision': version,
            success: function() {
                self.fetchHistory();
            }
        });
    };

    $.wiki.HistoryPerspective = HistoryPerspective;

})(jQuery);
