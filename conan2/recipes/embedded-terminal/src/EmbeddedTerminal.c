#include "EmbeddedTerminal.h"

// VTE doc: https://developer-old.gnome.org/vte/unstable/VteTerminal.html

#define HOME_DIRECTORY "~/"
#define str_is_null_or_empty(str) ((str) == NULL || (str)[0] == '\0')
#define APPEND(arr, str, size) arr = realloc(arr, (size + 1) * sizeof(char*)); arr[size++] = str ? strdup(str?str:"") : NULL;

char** format_args(const char* executable, const char* args_str) {
    int size = 0;
    char** args = NULL;

    APPEND(args, executable, size);

    if (!str_is_null_or_empty(args_str)){
        char* copy = strdup(args_str);    
        char* token = strtok(copy, " ");
        int i = 0;

        while (token != NULL) {
            APPEND(args, token, size);
            token = strtok(NULL, " ");
            i++;
        }
        
        free(token);
        free(copy);
    }
    
    APPEND(args, NULL, size);

    return args;
}

LAUNCHER_EXPORT char* get_default_shell(){
    return vte_get_user_shell();
}

LAUNCHER_EXPORT void embedded_terminal_set_background_color(VteTerminal* term, GdkRGBA* color){
    vte_terminal_set_color_background(term, color);
}

LAUNCHER_EXPORT void embedded_terminal_set_foreground_color(VteTerminal* term, GdkRGBA* color){
    vte_terminal_set_color_foreground(term, color);
}

LAUNCHER_EXPORT void embedded_terminal_reset(VteTerminal* term, bool clear_tabstops, bool clear_history){
    vte_terminal_reset(term, clear_tabstops, clear_history);
}

LAUNCHER_EXPORT void embedded_terminal_feed(VteTerminal* term, const char* data){
    vte_terminal_feed(term, data, strlen(data));
}

LAUNCHER_EXPORT void embedded_terminal_feed_child(VteTerminal* term, const char* data){
    vte_terminal_feed_child(term, data, strlen(data));
}

LAUNCHER_EXPORT void embedded_terminal_set_font(VteTerminal* term, const PangoFontDescription* font ){
    vte_terminal_set_font(term, font);
}

LAUNCHER_EXPORT const PangoFontDescription* embedded_terminal_get_font(VteTerminal* term){
    return vte_terminal_get_font(term);
}

LAUNCHER_EXPORT void embedded_terminal_launch(VteTerminal* terminal, const char* executable, const char* working_directory, const char* args, void* callback_ready){
    vte_terminal_spawn_async(terminal, VTE_PTY_DEFAULT, str_is_null_or_empty(working_directory) ? HOME_DIRECTORY : working_directory, format_args(str_is_null_or_empty(executable) ? get_default_shell() : executable, args), NULL, G_SPAWN_SEARCH_PATH, NULL, NULL, NULL, -1, NULL, callback_ready, NULL);
}

LAUNCHER_EXPORT EmbeddedTerminal_t embedded_terminal_new() {
    GtkWidget* w = vte_terminal_new();
    EmbeddedTerminal_t embedded = { .widget = w, .terminal = VTE_TERMINAL(w)};
    return embedded;
}