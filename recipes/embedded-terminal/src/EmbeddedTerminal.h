#ifndef EmbeddedTerminal_h
#define EmbeddedTerminal_h

#include <gtk/gtk.h>
#include <vte-2.91/vte/vte.h>
#include <stdbool.h>

#ifndef LAUNCHER_EXPORT
    #define LAUNCHER_EXPORT __attribute__ ((visibility("default")))
#endif

typedef struct EmbeddedTerminal
{
    GtkWidget* widget;
    VteTerminal* terminal;
} EmbeddedTerminal_t;

LAUNCHER_EXPORT char* get_default_shell();
LAUNCHER_EXPORT EmbeddedTerminal_t embedded_terminal_new();
LAUNCHER_EXPORT const PangoFontDescription* embedded_terminal_get_font(VteTerminal* terminal);
LAUNCHER_EXPORT void embedded_terminal_set_background_color(VteTerminal* terminal, GdkRGBA* color);
LAUNCHER_EXPORT void embedded_terminal_set_foreground_color(VteTerminal* terminal, GdkRGBA* color);
LAUNCHER_EXPORT void embedded_terminal_set_font(VteTerminal* terminal, const PangoFontDescription* font);
LAUNCHER_EXPORT void embedded_terminal_reset(VteTerminal* terminal, bool clear_tabstops, bool clear_history);
LAUNCHER_EXPORT void embedded_terminal_feed_child(VteTerminal* terminal, const char* data);
LAUNCHER_EXPORT void embedded_terminal_feed(VteTerminal* terminal, const char* data);
LAUNCHER_EXPORT void embedded_terminal_launch(VteTerminal* terminal, const char* exec, const char* working_directory, const char* args, void* callback_ready);

#endif

