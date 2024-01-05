import binaryninja

if binaryninja.core_ui_enabled():
    from .CommentsAndSymbols import comments_and_symbols

    binaryninja.PluginCommand.register(
        'Comments And Symbols',
        'Show comments and symbols renamed during the analysis process.',
        comments_and_symbols
    )