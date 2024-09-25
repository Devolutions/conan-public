#ifndef WebView_h
#define WebView_h

#include <gtk/gtk.h>
#include <webkit2/webkit2.h>
#include <JavaScriptCore/JavaScript.h>

#ifndef LAUNCHER_EXPORT
    #define LAUNCHER_EXPORT __attribute__ ((visibility("default")))
#endif

typedef bool (*callback_authenticate_fn)(WebKitWebView* view, WebKitAuthenticationRequest* request, gpointer user_data);
typedef void (*callback_js_ready_evnt_fn)();
typedef void (*callback_js_error_evnt_fn)(char* error_message);
typedef bool (*callback_load_failed_evnt_fn)(char* failed_uri, char* message);
typedef bool (*callback_load_changed_evnt_fn)(WebKitWebView* view, WebKitLoadEvent load_event, gpointer user_data);
typedef bool (*callback_decide_policy_evnt_fn)(WebKitWebView* view, gpointer decision, WebKitPolicyDecisionType type);
typedef void* (*callback_decide_new_window_policy_evnt_fn)(WebKitWebView* view, gpointer action, WebKitNavigationType type);
typedef void (*callback_get_cookies_evnt_fn)(char* header);
typedef void (*callback_script_message_received_evnt_fn)(WebKitUserContentManager* contentManager, WebKitJavascriptResult* js_result);
typedef void (*callback_context_menu_evnt_fn)(WebKitWebView* view, WebKitContextMenu* context_menu, WebKitHitTestResult* hit_test_result, gpointer user_data);
typedef void (*callback_download_started_evnt_fn)(WebKitContextMenu* context_menu, WebKitDownload* download, gpointer user_data);
typedef void (*callback_clear_data_manager_finish_evnt_fn)(gboolean clear_successful);

LAUNCHER_EXPORT void* webview_new();
LAUNCHER_EXPORT void* webview_new_ephemeral();
LAUNCHER_EXPORT void load_uri(void* view, char *uri);
LAUNCHER_EXPORT void load_html(void* view, char *html);
LAUNCHER_EXPORT void close_webview(void* webview);
LAUNCHER_EXPORT void evaluate_javascript(void* view, char *script);
LAUNCHER_EXPORT char* get_evaluate_javascript_string(void* view);
LAUNCHER_EXPORT bool set_callback_authenticate(void* view, callback_authenticate_fn handler);
LAUNCHER_EXPORT bool set_callback_decide_policy(void* view, callback_decide_policy_evnt_fn handler);
LAUNCHER_EXPORT bool set_callback_decide_new_window_policy(void* view, callback_decide_new_window_policy_evnt_fn handler);
LAUNCHER_EXPORT bool set_callback_js_ready(void* view, callback_js_ready_evnt_fn handler);
LAUNCHER_EXPORT bool set_callback_js_error(void* view, callback_js_error_evnt_fn handler);
LAUNCHER_EXPORT bool set_callback_clear_data_manager_finish(void* view, callback_clear_data_manager_finish_evnt_fn handler);
LAUNCHER_EXPORT bool set_callback_load_changed(void* view, callback_load_changed_evnt_fn handler);
LAUNCHER_EXPORT bool set_callback_menu(void* view, callback_context_menu_evnt_fn handler);
LAUNCHER_EXPORT bool set_callback_script_message_received(void* view, callback_script_message_received_evnt_fn handler);
LAUNCHER_EXPORT bool set_callback_download_started(void* view, callback_download_started_evnt_fn handler);
LAUNCHER_EXPORT bool set_callback_load_failed(void* view, callback_load_failed_evnt_fn handler);
LAUNCHER_EXPORT bool set_callback_get_cookie(void* view, callback_get_cookies_evnt_fn handler);
LAUNCHER_EXPORT void set_cookies_save_path(void* view, const char* path);
LAUNCHER_EXPORT void set_enable_logging(void* view, gboolean enable);
LAUNCHER_EXPORT void set_proxy(void* view, const gchar *proxyUri, const gchar * const *ignore_hosts, WebKitNetworkProxyMode proxyMode);
LAUNCHER_EXPORT const char* webview_get_uri(void* view);
LAUNCHER_EXPORT const char* webview_get_decision_uri(void* decision);
LAUNCHER_EXPORT void webkit_authenticate_request(void* req, void* cred);
LAUNCHER_EXPORT gboolean webkit_authentication_is_retry(void* req);
LAUNCHER_EXPORT WebKitCredential* webkit_create_credential(const gchar* username, const gchar* password, WebKitCredentialPersistence persistence);
LAUNCHER_EXPORT WebKitAuthenticationScheme get_webKit_authentication_request_authentication_scheme(void* request);
LAUNCHER_EXPORT const char* webview_get_navigation_action_request_uri(void* decision);
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
LAUNCHER_EXPORT WebKitHardwareAccelerationPolicy webview_get_hardware_acceleration_policy(void* webview);
LAUNCHER_EXPORT void webview_set_hardware_acceleration_policy(void* webview, WebKitHardwareAccelerationPolicy policy);
LAUNCHER_EXPORT gboolean webview_get_enable_developer_extras(void* webview);
LAUNCHER_EXPORT void webview_set_enable_developer_extras(void* webview, gboolean enabled);
LAUNCHER_EXPORT WebKitCacheModel webview_get_cache_model(void* webview);
LAUNCHER_EXPORT void webview_set_cache_model(void* webview, WebKitCacheModel cache_model);
LAUNCHER_EXPORT gdouble webview_get_zoom_level(void* webview);
LAUNCHER_EXPORT void webview_set_zoom_level(void* webview, gdouble zoom_level);
LAUNCHER_EXPORT void webview_register_script_message_handler(void* webview, const gchar *name, callback_script_message_received_evnt_fn handler);
LAUNCHER_EXPORT void webview_unregister_script_message_handler(void* webview, const gchar *name, callback_script_message_received_evnt_fn handler);
LAUNCHER_EXPORT void webview_get_cookies(void* webview, const gchar* uri);
LAUNCHER_EXPORT char* get_js_result_message(void* js_result);
LAUNCHER_EXPORT void* webview_add_script(void* webview, const gchar* source, WebKitUserContentInjectedFrames injected_frames, WebKitUserScriptInjectionTime injection_time, const gchar* const* allow_list, const gchar* const* block_list);
LAUNCHER_EXPORT void webview_remove_script(void* webview, void* script);
LAUNCHER_EXPORT void webview_remove_all_scripts(void* webview);
LAUNCHER_EXPORT void webview_show_inspector(void* webview);
LAUNCHER_EXPORT void webview_website_data_manager_clear(void* webview, WebKitWebsiteDataTypes types, GTimeSpan timespan);
LAUNCHER_EXPORT gboolean webview_website_data_manager_clear_finish(void* webview, GAsyncResult* result, GError** error);

#endif