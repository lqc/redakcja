(function($){

    /* Show theme to the user */
    function selectTheme(themeId){
        var selection = window.getSelection();
        selection.removeAllRanges();

        var range = document.createRange();
        var s = $(".motyw[theme-class='" + themeId + "']")[0];
        var e = $(".end[theme-class='" + themeId + "']")[0];

        if (s && e) {
            range.setStartAfter(s);
            range.setEndBefore(e);
            selection.addRange(range);
        }
    };

    /* Verify insertion port for annotation or theme */
    function verifyTagInsertPoint(node){
        if (node.nodeType == 3) { // Text Node
            node = node.parentNode;
        }

        if (node.nodeType != 1) {
            return false;
        }

        node = $(node);
        var xtype = node.attr('x-node');

        if (!xtype || (xtype.search(':') >= 0) ||
        xtype == 'motyw' ||
        xtype == 'begin' ||
        xtype == 'end') {
            return false;
        }

        // don't allow themes inside annotations
        if (node.is('*[x-annotation-box] *'))
            return false;

        return true;
    }

    /* Convert HTML fragment to plaintext */
    var ANNOT_FORBIDDEN = ['pt', 'pa', 'pr', 'pe', 'begin', 'end', 'motyw'];

    function html2plainText(fragment){
        var text = "";

        $(fragment.childNodes).each(function(){
            if (this.nodeType == 3) // textNode
                text += this.nodeValue;
            else {
                if (this.nodeType == 1 &&
                        $.inArray($(this).attr('x-node'), ANNOT_FORBIDDEN) == -1) {
                    text += html2plainText(this);
                }
            };
        });

        return text;
    }


    /* Insert annotation using current selection */
    function addAnnotation(){
        var selection = window.getSelection();
        var n = selection.rangeCount;

        if (n == 0) {
            window.alert("Nie zaznaczono żadnego obszaru");
            return false;
        }

        // for now allow only 1 range
        if (n > 1) {
            window.alert("Zaznacz jeden obszar");
            return false;
        }

        // remember the selected range
        var range = selection.getRangeAt(0);

        if (!verifyTagInsertPoint(range.endContainer)) {
            window.alert("Nie można wstawić w to miejsce przypisu.");
            return false;
        }

        // BUG #273 - selected text can contain themes, which should be omitted from
        // defining term
        var text = html2plainText(range.cloneContents());
        var tag = $('<span></span>');
        range.collapse(false);
        range.insertNode(tag[0]);

        xml2html({
            xml: '<pe><slowo_obce>' + text + '</slowo_obce> --- </pe>',
            success: function(text){
                var t = $(text);
                tag.replaceWith(t);
                openForEdit(t);
            },
            error: function(){
                tag.remove();
                alert('Błąd przy dodawaniu przypisu:' + errors);
            }
        })
    }


    /* Insert theme using current selection */

    function addTheme(){
        var selection = window.getSelection();
        var n = selection.rangeCount;

        if (n == 0) {
            window.alert("Nie zaznaczono żadnego obszaru");
            return false;
        }

        // for now allow only 1 range
        if (n > 1) {
            window.alert("Zaznacz jeden obszar.");
            return false;
        }


        // remember the selected range
        var range = selection.getRangeAt(0);


        if ($(range.startContainer).is('.html-editarea') ||
        $(range.endContainer).is('.html-editarea')) {
            window.alert("Motywy można oznaczać tylko na tekście nie otwartym do edycji. \n Zamknij edytowany fragment i spróbuj ponownie.");
            return false;
        }

        // verify if the start/end points make even sense -
        // they must be inside a x-node (otherwise they will be discarded)
        // and the x-node must be a main text
        if (!verifyTagInsertPoint(range.startContainer)) {
            window.alert("Motyw nie może się zaczynać w tym miejscu.");
            return false;
        }

        if (!verifyTagInsertPoint(range.endContainer)) {
            window.alert("Motyw nie może się kończyć w tym miejscu.");
            return false;
        }

        var date = (new Date()).getTime();
        var random = Math.floor(4000000000 * Math.random());
        var id = ('' + date) + '-' + ('' + random);

        var spoint = document.createRange();
        var epoint = document.createRange();

        spoint.setStart(range.startContainer, range.startOffset);
        epoint.setStart(range.endContainer, range.endOffset);

        var mtag, btag, etag, errors;

        // insert theme-ref

        xml2html({
            xml: '<end id="e' + id + '" />',
            success: function(text){
                etag = $('<span></span>');
                epoint.insertNode(etag[0]);
                etag.replaceWith(text);
                xml2html({
                    xml: '<motyw id="m' + id + '"></motyw>',
                    success: function(text){
                        mtag = $('<span></span>');
                        spoint.insertNode(mtag[0]);
                        mtag.replaceWith(text);
                        xml2html({
                            xml: '<begin id="b' + id + '" />',
                            success: function(text){
                                btag = $('<span></span>');
                                spoint.insertNode(btag[0])
                                btag.replaceWith(text);
                                selection.removeAllRanges();
                                openForEdit($('.motyw[theme-class=' + id + ']'));
                            }
                        });
                    }
                });
            }
        });
    }

    function addSymbol() {
        if($('div.html-editarea textarea')[0]) {
            var specialCharsContainer = $("<div id='specialCharsContainer'><a href='#' id='specialCharsClose'>Zamknij</a><table id='tableSpecialChars' style='width: 600px;'></table></div>");
            var specialChars = ['Ą','ą','Ć','ć','Ę','ę','Ł','ł','Ń','ń','Ó','ó','Ś','ś','Ż','ż','Ź','ź','Á','á','À','à',
            'Â','â','Ä','ä','Å','å','Ā','ā','Ă','ă','Ã','ã',
            'Æ','æ','Ç','ç','Č','č','Ċ','ċ','Ď','ď','É','é','È','è',
            'Ê','ê','Ë','ë','Ē','ē','Ě','ě','Ġ','ġ','Ħ','ħ','Í','í','Î','î',
            'Ī','ī','Ĭ','ĭ','Ľ','ľ','Ñ','ñ','Ň','ň','Ó','ó','Ö','ö',
            'Ô','ô','Ō','ō','Ǒ','ǒ','Œ','œ','Ø','ø','Ř','ř','Š',
            'š','Ş','ş','Ť','ť','Ţ','ţ','Ű','ű','Ú','ú',
            'Ü','ü','Ů','ů','Ū','ū','Û','û','Ŭ','ŭ',
            'Ý','ý','Ž','ž','ß','Ð','ð','Þ','þ','А','а','Б',
            'б','В','в','Г','г','Д','д','Е','е','Ё','ё','Ж',
            'ж','З','з','И','и','Й','й','К','к','Л','л','М',
            'м','Н','н','О','о','П','п','Р','р','С','с',
            'Т','т','У','у','Ф','ф','Х','х','Ц','ц','Ч',
            'ч','Ш','ш','Щ','щ','Ъ','ъ','Ы','ы','Ь','ь','Э',
            'э','Ю','ю','Я','я','ѓ','є','і','ї','ј','љ','њ',
            'Ґ','ґ','Α','α','Β','β','Γ','γ','Δ','δ','Ε','ε',
            'Ζ','ζ','Η','η','Θ','θ','Ι','ι','Κ','κ','Λ','λ','Μ',
            'μ','Ν','ν','Ξ','ξ','Ο','ο','Π','π','Ρ','ρ','Σ','ς','σ',
            'Τ','τ','Υ','υ','Φ','φ','Χ','χ','Ψ','ψ','Ω','ω','–',
            '—','¡','¿','$','¢','£','€','©','®','°','¹','²','³',
            '¼','½','¾','†','§','‰','•','←','↑','→','↓',
            '„”','«»','’','[',']','[','~','|','−','·',
            '×','÷','≈','≠','±','≤','≥','∈'];
            var tableContent = "<tr>";
            
            for(var i in specialChars) {
                if(i % 14 == 0 && i > 0) {
                    tableContent += "</tr><tr>";
                }              
                tableContent += "<td><input type='button' class='specialBtn' value='"+specialChars[i]+"'/></td>";              
            }
            
            tableContent += "</tr>";                                   
            $("#content").append(specialCharsContainer);
            $("#tableSpecialChars").append(tableContent);
            
            /* events */
            
            $('.specialBtn').click(function(){
                insertAtCaret($('div.html-editarea textarea')[0], $(this).val());
                $(specialCharsContainer).remove();
            });         
            $('#specialCharsClose').click(function(){
                $(specialCharsContainer).remove();
            });                   
            
        } else {
            window.alert('Najedź na fragment tekstu, wybierz "Edytuj" i ustaw kursor na miejscu gdzie chcesz wstawić symbol.');
        }
    }

    function insertAtCaret(txtarea,text) { 
        /* http://www.scottklarr.com/topic/425/how-to-insert-text-into-a-textarea-where-the-cursor-is/ */
        var scrollPos = txtarea.scrollTop; 
        var strPos = 0; 
        var br = ((txtarea.selectionStart || txtarea.selectionStart == '0') ? "ff" : (document.selection ? "ie" : false ) );
        if (br == "ie") { 
            txtarea.focus();
            var range = document.selection.createRange(); 
            range.moveStart ('character', -txtarea.value.length); 
            strPos = range.text.length; 
        } else if (br == "ff") strPos = txtarea.selectionStart; 
        var front = (txtarea.value).substring(0,strPos); 
        var back = (txtarea.value).substring(strPos,txtarea.value.length); 
        txtarea.value=front+text+back; 
        strPos = strPos + text.length; 
        if (br == "ie") { 
            txtarea.focus(); 
            var range = document.selection.createRange(); 
            range.moveStart ('character', -txtarea.value.length); 
            range.moveStart ('character', strPos); 
            range.moveEnd ('character', 0); 
            range.select(); 
        } else if (br == "ff") { 
            txtarea.selectionStart = strPos; 
            txtarea.selectionEnd = strPos; 
            txtarea.focus(); 
        } 
        txtarea.scrollTop = scrollPos; 
    } 

    /* open edition window for selected fragment */
    function openForEdit($origin){
        var $box = null

        // annotations overlay their sub box - not their own box //
        if ($origin.is(".annotation-inline-box")) {
            $box = $("*[x-annotation-box]", $origin);
        }
        else {
            $box = $origin;
        }

        /* check sidebar width and display textarea on the right but avoiding interfering with gallery */
        var x = $(document).width() - $("#sidebar").width() - 576 - 100; // and little margin here: 100px
        var y = $origin.offset().top + $("#html-view").scrollTop();
        
        
        var w = $box.outerWidth();
        var h = $box.innerHeight();

        if ($origin.is(".annotation-inline-box")) {
            w = Math.max(w, 400);
            h = Math.max(h, 60);
        }

        // start edition on this node
        var $overlay = $('<div class="html-editarea"><button class="accept-button">Zapisz</button><button class="delete-button">Usuń</button><textarea></textarea></div>').css({
            position: 'absolute',
            height: h,
            left: x,
            top: y,
            width: w
        }).appendTo($('#html-view')).show();  /* appending outside of the document structure */
        

        if ($origin.is('.motyw')) {
            withThemes(function(canonThemes){
                $('textarea', $overlay).autocomplete(canonThemes, {
                    autoFill: true,
                    multiple: true,
                    selectFirst: true,
                    highlight: false
                });
            })
        }

        if ($origin.is('.motyw')){
            $('.delete-button', $overlay).click(function(){
                if (window.confirm("Czy jesteś pewien, że chcesz usunąć ten motyw ?")) {
                    $('[theme-class=' + $origin.attr('theme-class') + ']').remove();
                    $overlay.remove();
                    $(document).unbind('click.blur-overlay');
                    return false;
                };
            });
        }
        else if($box.is('*[x-annotation-box]')) {
            $('.delete-button', $overlay).click(function(){
                if (window.confirm("Czy jesteś pewien, że chcesz usunąć ten przypis?")) {
                    $origin.remove();
                    $overlay.remove();
                    $(document).unbind('click.blur-overlay');
                    return false;
                };
            });
        }
        else {
            $('.delete-button', $overlay).hide();
        }


        var serializer = new XMLSerializer();

        html2text({
            element: $box[0],
            stripOuter: true,
            success: function(text){
                $('textarea', $overlay).val($.trim(text));

                setTimeout(function(){
                    $('textarea', $overlay).elastic().focus();
                }, 50);

                function save(argument){
                    var nodeName = $box.attr('x-node') || 'pe';
                    var insertedText = $('textarea', $overlay).val();

                    if ($origin.is('.motyw')) {
                        insertedText = insertedText.replace(/,\s*$/, '');
                    }

                    xml2html({
                        xml: '<' + nodeName + '>' + insertedText + '</' + nodeName + '>',
                        success: function(element){
                            $origin.html($(element).html());
                            $overlay.remove();
                        },
                        error: function(text){
                            $overlay.remove();
                            alert('Błąd! ' + text);
                        }
                    })
                }

                $('.accept-button', $overlay).click(function(){
                    save();
                });

                $(document).bind('click.blur-overlay', function(event){
                    if ($(event.target).parents('.html-editarea').length > 0) {
                        return;
                    }
                    save();

                    $(document).unbind('click.blur-overlay');
                });

            },
            error: function(text){
                alert('Błąd! ' + text);
            }
        });
    }

    function VisualPerspective(options){

        var old_callback = options.callback;

        options.callback = function(){
            var element = $("#html-view");
            var button = $('<button class="edit-button">Edytuj</button>');

            if (!CurrentDocument.readonly) {
                $('#html-view').bind('mousemove', function(event){
                    var editable = $(event.target).closest('*[x-editable]');
                    $('.active', element).not(editable).removeClass('active').children('.edit-button').remove();

                    if (!editable.hasClass('active')) {
                        editable.addClass('active').append(button);
                    }
                    if (editable.is('.annotation-inline-box')) {
                        $('*[x-annotation-box]', editable).css({
                            position: 'absolute',
                            left: event.clientX - editable.offset().left + 5,
                            top: event.clientY - editable.offset().top + 5
                        }).show();
                    }
                    else {
                        $('*[x-annotation-box]').hide();
                    }
                });

                $('#insert-annotation-button').click(function(){
                    addAnnotation();
                    return false;
                });

                $('#insert-theme-button').click(function(){
                    addTheme();
                    return false;
                });
                
                $('#insert-symbol-button').click(function(){
                    addSymbol();
                    return false;
                });                

                $('.edit-button').live('click', function(event){
                    event.preventDefault();
                    openForEdit($(this).parent());
                });

            }

            $('.motyw').live('click', function(){
                selectTheme($(this).attr('theme-class'));
            });

            old_callback.call(this);
        };

        $.wiki.Perspective.call(this, options);
    };

    VisualPerspective.prototype = new $.wiki.Perspective();

    VisualPerspective.prototype.freezeState = function(){

    };

    VisualPerspective.prototype.onEnter = function(success, failure){
        $.wiki.Perspective.prototype.onEnter.call(this);

        $.blockUI({
            message: 'Uaktualnianie widoku...'
        });

        function _finalize(callback){
            $.unblockUI();
            if (callback)
                callback();
        }

        xml2html({
            xml: this.doc.text,
            success: function(element){
                $('#html-view').html(element);
                _finalize(success);
            },
            error: function(text){
                /* only basic error message */
                var errorArray = text.split("\n");
                if (errorArray.length >= 3) {
                    text = errorArray[2].split(":")[0];
                }
                $('#html-view').html('<p class="error">Wystąpił błąd: '+ text + '</p>');
                _finalize(failure);
            }
        });
    };

    VisualPerspective.prototype.onExit = function(success, failure){
        var self = this;

        $.blockUI({
            message: 'Zapisywanie widoku...'
        });

        function _finalize(callback){
            $.unblockUI();
            if (callback)
                callback();
        }

        if ($('#html-view .error').length > 0)
            return _finalize(failure);

        html2text({
            element: $('#html-view div').get(0),
            success: function(text){
                self.doc.setText(text);
                _finalize(success);
            },
            error: function(text){
                $('#source-editor').html('<p>Wystąpił błąd:</p><pre>' + text + '</pre>');
                _finalize(failure);
            }
        });
    };

    $.wiki.VisualPerspective = VisualPerspective;

})(jQuery);
