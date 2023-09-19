#ifndef WebView_h
#define WebView_h

#include <gtk/gtk.h>
#include <webkit2/webkit2.h>
#include <JavaScriptCore/JavaScript.h>

#ifndef LAUNCHER_EXPORT
    #define LAUNCHER_EXPORT __attribute__ ((visibility("default")))
#endif

typedef void (*callback_js_ready_evnt_fn)();
typedef bool (*callback_load_failed_evnt_fn)(char* failed_uri, char* message);
typedef bool (*callback_load_changed_evnt_fn)(WebKitLoadEvent evnt);
typedef bool (*callback_decide_policy_evnt_fn)(WebKitWebView* view, gpointer decision, WebKitPolicyDecisionType type);
typedef void (*callback_get_cookies_evnt_fn)(char* header);
typedef void (*callback_script_message_received_evnt_fn)(WebKitUserContentManager* contentManager, WebKitJavascriptResult* js_result);
typedef void (*callback_context_menu_evnt_fn)(WebKitWebView* view, WebKitContextMenu* context_menu, WebKitHitTestResult* hit_test_result, gpointer user_data);

LAUNCHER_EXPORT void* webview_new();
LAUNCHER_EXPORT void* webview_new_ephemeral();
LAUNCHER_EXPORT void load_uri(void* view, char *uri);
LAUNCHER_EXPORT void load_html(void* view, char *html);
LAUNCHER_EXPORT void close_webview();
LAUNCHER_EXPORT void evaluate_javascript(void* view, char *script);
LAUNCHER_EXPORT char* get_evaluate_javascript_string(void* view);
LAUNCHER_EXPORT bool set_callback_decide_policy(void* view, callback_decide_policy_evnt_fn handler);
LAUNCHER_EXPORT bool set_callback_js_ready(void* view, callback_js_ready_evnt_fn handler);
LAUNCHER_EXPORT bool set_callback_load_changed(void* view, callback_load_changed_evnt_fn handler);
LAUNCHER_EXPORT bool set_callback_menu(void* view, callback_context_menu_evnt_fn handler);
LAUNCHER_EXPORT bool set_callback_script_message_received(void* view, callback_script_message_received_evnt_fn handler);
LAUNCHER_EXPORT bool set_callback_load_failed(void* view, callback_load_failed_evnt_fn handler);
LAUNCHER_EXPORT bool set_callback_get_cookie(void* view, callback_get_cookies_evnt_fn handler);
LAUNCHER_EXPORT void set_cookies_save_path(void* view, const char* path);
LAUNCHER_EXPORT void set_enable_logging(void* view, gboolean enable);
LAUNCHER_EXPORT void set_proxy(void* view, const gchar *proxyUri);
LAUNCHER_EXPORT const char* webview_get_uri(void* view);
LAUNCHER_EXPORT const char* webview_get_decision_uri(void* decision);
LAUNCHER_EXPORT void* webview_get_view(void* webview);
LAUNCHER_EXPORT void webview_reload_page(void* webview, bool bypassCache);
LAUNCHER_EXPORT void webview_stop_loading(void* webview);
LAUNCHER_EXPORT gboolean webview_can_go_back(void* webview);
LAUNCHER_EXPORT gboolean webview_can_go_forward(void* webview);
LAUNCHER_EXPORT void webview_go_back(void* webview);
LAUNCHER_EXPORT void webview_go_forward(void* webview);
LAUNCHER_EXPORT WebKitFindController* webview_search_start(void* webview, const gchar *search_text, gboolean case_sensitive, gboolean forward, gboolean wrap, gboolean only_word_start, gboolean treat_camelcase_as_word_start);
LAUNCHER_EXPORT void webview_search_finish(void* find_controller);
LAUNCHER_EXPORT void webview_search_next(void* find_controller);
LAUNCHER_EXPORT void webview_search_previous(void* find_controller);
LAUNCHER_EXPORT void webview_search_count_matches(void* find_controller);
LAUNCHER_EXPORT WebKitPrintOperationResponse webview_print_operation_run_dialog(void* webview, void* parent);
LAUNCHER_EXPORT gboolean webview_get_allow_file_access_from_file_urls(void* webview);
LAUNCHER_EXPORT void webview_set_allow_file_access_from_file_urls(void* webview, gboolean allowed);
LAUNCHER_EXPORT gboolean webview_get_allow_universal_access_from_file_urls(void* webview);
LAUNCHER_EXPORT void webview_set_allow_universal_access_from_file_urls(void* webview, gboolean allowed);
LAUNCHER_EXPORT gboolean webview_get_enable_write_console_messages_to_stdout(void* webview);
LAUNCHER_EXPORT void webview_set_enable_write_console_messages_to_stdout(void* webview, gboolean enabled);
LAUNCHER_EXPORT void webview_register_script_message_handler(void* webview, const gchar *name, callback_script_message_received_evnt_fn handler);
LAUNCHER_EXPORT void webview_unregister_script_message_handler(void* webview, const gchar *name, callback_script_message_received_evnt_fn handler);
LAUNCHER_EXPORT void webview_get_cookies(void* webview, const gchar* uri);
LAUNCHER_EXPORT char* get_js_result_message(void* js_result);

#endif