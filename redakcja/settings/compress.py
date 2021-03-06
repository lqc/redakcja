# CSS and JS files to compress
COMPRESS_CSS = {
    'detail': {
         'source_filenames': (
            'css/master.css',
            'css/toolbar.css',
            'css/gallery.css',
            'css/history.css',
            'css/summary.css',
            'css/html.css',
            'css/jquery.autocomplete.css',
            'css/dialogs.css',
        ),
        'output_filename': 'compressed/detail_styles_?.css',
    },
    'listing': {
        'source_filenames': (
            'css/filelist.css',
        ),
        'output_filename': 'compressed/listing_styles_?.css',
     }
}

COMPRESS_JS = {
    # everything except codemirror
    'detail': {
        'source_filenames': (
                # libraries
                'js/lib/jquery-1.4.2.min.js',
                'js/lib/jquery/jquery.autocomplete.js',
                'js/lib/jquery/jquery.blockui.js',
                'js/lib/jquery/jquery.elastic.js',
                'js/button_scripts.js',
                'js/slugify.js',

                # wiki scripts
                'js/wiki/wikiapi.js',
                'js/wiki/xslt.js',

                # base UI
                'js/wiki/base.js',
                'js/wiki/toolbar.js',

                # dialogs
                'js/wiki/dialog_save.js',
                'js/wiki/dialog_addtag.js',

                # views
                'js/wiki/view_history.js',
                'js/wiki/view_summary.js',
                'js/wiki/view_editor_source.js',
                'js/wiki/view_editor_wysiwyg.js',
                'js/wiki/view_gallery.js',
                'js/wiki/view_search.js',
                'js/wiki/view_column_diff.js',
        ),
        'output_filename': 'compressed/detail_scripts_?.js',
     },
    'listing': {
        'source_filenames': (
                'js/lib/jquery-1.4.2.min.js',
                'js/slugify.js',
        ),
        'output_filename': 'compressed/listing_scripts_?.js',
     }
}

COMPRESS = True
COMPRESS_CSS_FILTERS = None
COMPRESS_JS_FILTERS = None
COMPRESS_AUTO = True
COMPRESS_VERSION = True
COMPRESS_VERSIONING = 'compress.versioning.hash.MD5Versioning'
