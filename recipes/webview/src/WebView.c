#include "WebView.h"
#include <stdlib.h>

// https://people.igalia.com/tsaunier/documentation/WebKitGTK/WebKitWebView.html?gi-language=c#WebKitWebView
static void evaluate_javascript_cb(GObject *obj, GAsyncResult *result, gpointer user_data);
static gboolean web_view_load_failed_cb(WebKitWebView* view, WebKitLoadEvent load_event, gchar* failing_uri, GError* error, gpointer user_data);
char* get_evaluate_javascript_string();

typedef struct web_view{
        WebKitWebView* view;
        WebKitUserContentManager* contentManager;
        WebKitNetworkProxySettings* proxySettings;
        callback_load_changed_evnt_fn load_changed_handler;
        callback_load_failed_evnt_fn load_failed_handler;
        callback_decide_policy_evnt_fn decide_policy_handler;
        callback_js_ready_evnt_fn js_ready_handler;
        callback_context_menu_evnt_fn context_menu_handler;
        callback_script_message_received_evnt_fn script_message_received_handler;
        char* result_eval_js;
        gboolean enable_logging;
        bool executingJavascript;
        bool destroyObject;
} webView;

LAUNCHER_EXPORT const char* webview_get_decision_uri(void* ptr)
{
    WebKitURIRequest* request = NULL;

    if (WEBKIT_IS_NAVIGATION_POLICY_DECISION(ptr))
    {
        WebKitNavigationPolicyDecision* navigationDecision = WEBKIT_NAVIGATION_POLICY_DECISION(ptr);
        WebKitNavigationAction* action = webkit_navigation_policy_decision_get_navigation_action(navigationDecision);

        if(!action)
            return NULL;

        request = webkit_navigation_action_get_request(action);
    }
    else if (WEBKIT_IS_RESPONSE_POLICY_DECISION(ptr))
    {
        WebKitResponsePolicyDecision* responseDecision = WEBKIT_RESPONSE_POLICY_DECISION(ptr);
        request = webkit_response_policy_decision_get_request(responseDecision);
    }

    if(!request)
        return NULL;

    return webkit_uri_request_get_uri(request);
}

LAUNCHER_EXPORT const char* webview_get_uri(void* webview)
{
    return webkit_web_view_get_uri(((webView*)webview)->view);
}

LAUNCHER_EXPORT void* webview_new()
{
    webView* wv = (webView*)calloc(sizeof(webView), 1);
    wv->load_changed_handler = 0;
    wv->load_failed_handler = 0;
    wv->decide_policy_handler = 0;
    wv->js_ready_handler = 0;
    wv->view = WEBKIT_WEB_VIEW(webkit_web_view_new());
    wv->contentManager = webkit_web_view_get_user_content_manager(wv->view);
    g_signal_connect(wv->view, "load-failed", G_CALLBACK(web_view_load_failed_cb), wv);

    webkit_website_data_manager_set_tls_errors_policy(webkit_web_context_get_website_data_manager(webkit_web_view_get_context(wv->view)), WEBKIT_TLS_ERRORS_POLICY_IGNORE);

    return wv;
}

LAUNCHER_EXPORT void* webview_new_ephemeral()
{
    webView* wv = (webView*)calloc(sizeof(webView), 1);
    wv->load_changed_handler = 0;
    wv->load_failed_handler = 0;
    wv->decide_policy_handler = 0;
    wv->js_ready_handler = 0;
    WebKitWebContext* context = webkit_web_context_new_ephemeral ();
    wv->view = WEBKIT_WEB_VIEW(webkit_web_view_new_with_context (context));
    g_signal_connect(wv->view, "load-failed", G_CALLBACK(web_view_load_failed_cb), wv);

    webkit_website_data_manager_set_tls_errors_policy(webkit_web_context_get_website_data_manager(webkit_web_view_get_context(wv->view)), WEBKIT_TLS_ERRORS_POLICY_IGNORE);

    return wv;
}

LAUNCHER_EXPORT void* webview_get_view(void* webview)
{
    return ((webView*)webview)->view;
}

LAUNCHER_EXPORT void load_html(void* webview, char *html)
{
    WebKitWebView* wkwv = ((webView*)webview)->view;
    webkit_web_view_load_html(wkwv, html, NULL);
}

LAUNCHER_EXPORT void load_uri(void* webview, char *uri)
{
    WebKitWebView* wkwv = ((webView*)webview)->view;
    webkit_web_view_load_uri(wkwv, uri);
}

LAUNCHER_EXPORT void close_webview(void* webview)
{
    webView* wv = (webView*)webview;

    if(wv->executingJavascript)
    {
        wv->destroyObject = TRUE;
        return;
    }

    free(wv);
}

LAUNCHER_EXPORT void evaluate_javascript(void* webview, char *script)
{
    webView* wv = (webView*)webview;
    WebKitWebView* wkwebview = wv->view;
    wv->executingJavascript = TRUE;
    webkit_web_view_run_javascript(wkwebview, script, NULL, evaluate_javascript_cb, wv);
}

LAUNCHER_EXPORT void set_cookies_save_path(void* view, const char* path)
{
    webView* wv = (webView*)view;

    WebKitWebContext* context = webkit_web_view_get_context (wv->view);
    WebKitCookieManager* cookiemgr = webkit_web_context_get_cookie_manager (context);
    webkit_cookie_manager_set_persistent_storage (cookiemgr,
        g_build_filename (path, "cookies.txt", NULL),
        WEBKIT_COOKIE_PERSISTENT_STORAGE_SQLITE);
}

LAUNCHER_EXPORT void set_enable_logging(void* view, gboolean enable)
{
    webView* wv = (webView*)view;

    wv->enable_logging = enable;
}

LAUNCHER_EXPORT void set_proxy(void* view, const gchar *proxyUri)
{
    webView* wv = (webView*)view;
    WebKitWebContext* context = webkit_web_view_get_context (wv->view);
    WebKitWebsiteDataManager* dataManager = webkit_web_context_get_website_data_manager(context);
    WebKitNetworkProxySettings* proxySettings = webkit_network_proxy_settings_new(proxyUri, NULL);
    webkit_website_data_manager_set_network_proxy_settings(dataManager, WEBKIT_NETWORK_PROXY_MODE_CUSTOM, proxySettings);
}

static void evaluate_javascript_cb(GObject *obj, GAsyncResult *result, gpointer user_data)
{
    WebKitJavascriptResult* js_result;
    JSCValue* value;
    GError* error = NULL;
    webView* wv = (webView*)user_data;

    if(wv->destroyObject)
    {
        free(wv);
        return;
    }

    js_result = webkit_web_view_run_javascript_finish(wv->view, result, &error);

    wv->executingJavascript = FALSE;

    if(!js_result)
    {
        if(wv->enable_logging)
        {
            g_warning ("Error running javascript: %s", error->message);
        }

        g_error_free (error);
        return;
    }

    value = webkit_javascript_result_get_js_value(js_result);
    if(jsc_value_is_string(value))
    {
        wv->result_eval_js = jsc_value_to_string (value);
        if(wv->js_ready_handler)
            wv->js_ready_handler();
    }

    webkit_javascript_result_unref(js_result);
}

static gboolean web_view_load_failed_cb(WebKitWebView* view, WebKitLoadEvent load_event, gchar* failing_uri, GError* error, gpointer user_data)
{
    webView* wv = (webView*)user_data;

    if(wv->load_failed_handler)
        return wv->load_failed_handler(failing_uri, error->message);

    return FALSE;
}

LAUNCHER_EXPORT bool set_callback_decide_policy(void* view, callback_decide_policy_evnt_fn handler)
{
    webView* wv = (webView*)view;

    if (!handler && wv->decide_policy_handler)
    {
        g_signal_handlers_disconnect_by_func(wv->view, G_CALLBACK(wv->decide_policy_handler), NULL);
        wv->decide_policy_handler = handler;
    }
    else
    {
        wv->decide_policy_handler = handler;
        g_signal_connect(wv->view, "decide-policy", G_CALLBACK(wv->decide_policy_handler), NULL);
    }

    return 1;
}

LAUNCHER_EXPORT bool set_callback_load_changed(void* view, callback_load_changed_evnt_fn handler)
{
    webView* wv = (webView*)view;

    if (!handler && wv->load_changed_handler)
    {
        g_signal_handlers_disconnect_by_func(wv->view, G_CALLBACK(wv->load_changed_handler), NULL);
        wv->load_changed_handler = handler;
    }
    else
    {
        wv->load_changed_handler = handler;
        g_signal_connect(wv->view, "load-changed", G_CALLBACK(wv->load_changed_handler), NULL);
    }

    return 1;
}

LAUNCHER_EXPORT bool set_callback_menu(void* view, callback_context_menu_evnt_fn handler)
{
    webView* wv = (webView*)view;
    if (!handler && wv->context_menu_handler)
    {
        g_signal_handlers_disconnect_by_func(wv->view, G_CALLBACK(wv->context_menu_handler), NULL);
        wv->context_menu_handler = handler;
    }
    else
    {
        wv->context_menu_handler = handler;
        g_signal_connect(wv->view, "context-menu", G_CALLBACK(wv->context_menu_handler), NULL);
    }

    return 1;
}

LAUNCHER_EXPORT bool set_callback_script_message_received(void* view, callback_script_message_received_evnt_fn handler)
{
    webView* wv = (webView*)view;

    if (!handler && wv->script_message_received_handler)
    {
        g_signal_handlers_disconnect_by_func(wv->contentManager, G_CALLBACK(wv->script_message_received_handler), NULL);
        wv->script_message_received_handler = handler;
    }
    else
    {
        wv->script_message_received_handler = handler;
        g_signal_connect(wv->contentManager, "script-message-received", G_CALLBACK(wv->script_message_received_handler), NULL);
    }

    return 1;
}

LAUNCHER_EXPORT bool set_callback_load_failed(void* view, callback_load_failed_evnt_fn handler)
{
    webView* wv = (webView*)view;
    wv->load_failed_handler = handler;
    return 1;
}

LAUNCHER_EXPORT bool set_callback_js_ready(void* view, callback_js_ready_evnt_fn handler)
{
    webView* wv = (webView*)view;
    wv->js_ready_handler = handler;
    return 1;
}

char* get_evaluate_javascript_string(void* view)
{
    webView* wv = (webView*)view;

    if(!wv)
        return "";

    return wv->result_eval_js;
}

LAUNCHER_EXPORT void webview_reload_page(void* webview, bool bypassCache)
{
    webView* wv = (webView*)webview;

    if(bypassCache)
        webkit_web_view_reload_bypass_cache(wv->view);
    else
        webkit_web_view_reload(wv->view);
}

LAUNCHER_EXPORT void webview_stop_loading(void* webview)
{
    webView* wv = (webView*)webview;

    webkit_web_view_stop_loading(wv->view);
}

LAUNCHER_EXPORT gboolean webview_can_go_back(void* webview)
{
    webView* wv = (webView*)webview;

    return webkit_web_view_can_go_back(wv->view);
}

LAUNCHER_EXPORT gboolean webview_can_go_forward(void* webview)
{
    webView* wv = (webView*)webview;

    return webkit_web_view_can_go_forward(wv->view);
}

LAUNCHER_EXPORT void webview_go_back(void* webview)
{
    webView* wv = (webView*)webview;

    webkit_web_view_go_back(wv->view);
}

LAUNCHER_EXPORT void webview_go_forward(void* webview)
{
    webView* wv = (webView*)webview;

    webkit_web_view_go_forward(wv->view);
}

LAUNCHER_EXPORT WebKitFindController* webview_search_start(void* webview, const gchar *search_text, gboolean case_sensitive, gboolean forward, gboolean wrap, gboolean only_word_start, gboolean treat_camelcase_as_word_start)
{
    webView* wv = (webView*)webview;

    WebKitFindController *findController = webkit_web_view_get_find_controller(wv->view);

    gint32 searchOptions = WEBKIT_FIND_OPTIONS_NONE;

    if (!case_sensitive)
        searchOptions |= WEBKIT_FIND_OPTIONS_CASE_INSENSITIVE;

    if (!forward)
        searchOptions |= WEBKIT_FIND_OPTIONS_BACKWARDS;

    if (wrap)
        searchOptions |= WEBKIT_FIND_OPTIONS_WRAP_AROUND;

    if (only_word_start)
        searchOptions |= WEBKIT_FIND_OPTIONS_AT_WORD_STARTS;

    if (treat_camelcase_as_word_start)
        searchOptions |= WEBKIT_FIND_OPTIONS_TREAT_MEDIAL_CAPITAL_AS_WORD_START;

    webkit_find_controller_search(findController, search_text, searchOptions, G_MAXUINT);

    return findController;
}

LAUNCHER_EXPORT void webview_search_finish(void* find_controller)
{
    WebKitFindController* fc = (WebKitFindController*)find_controller;

    webkit_find_controller_search_finish(fc);
}

LAUNCHER_EXPORT void webview_search_next(void* find_controller)
{
    WebKitFindController* fc = (WebKitFindController*)find_controller;

    webkit_find_controller_search_next(fc);
}

LAUNCHER_EXPORT void webview_search_previous(void* find_controller)
{
    WebKitFindController* fc = (WebKitFindController*)find_controller;

    webkit_find_controller_search_previous(fc);
}

LAUNCHER_EXPORT void webview_search_count_matches(void* find_controller)
{
    WebKitFindController* fc = (WebKitFindController*)find_controller;

    webkit_find_controller_count_matches(fc, webkit_find_controller_get_search_text(fc), webkit_find_controller_get_options(fc), webkit_find_controller_get_max_match_count(fc));
}

LAUNCHER_EXPORT WebKitPrintOperationResponse webview_print_operation_run_dialog(void* webview, void* view)
{
    WebKitWebView* wkwv = ((webView*)webview)->view;
    WebKitPrintOperation* po = webkit_print_operation_new(wkwv);
    WebKitPrintOperationResponse response = webkit_print_operation_run_dialog(po, view);
    return response;
}

LAUNCHER_EXPORT gboolean webview_get_allow_file_access_from_file_urls(void* webview)
{
    webView* wv = (webView*)webview;
    WebKitSettings *settings = webkit_web_view_get_settings(wv->view);
    return webkit_settings_get_allow_file_access_from_file_urls(settings);
}

LAUNCHER_EXPORT void webview_set_allow_file_access_from_file_urls(void* webview, gboolean allowed)
{
    webView* wv = (webView*)webview;
    WebKitSettings *settings = webkit_web_view_get_settings(wv->view);
    webkit_settings_set_allow_file_access_from_file_urls(settings, allowed);
}

LAUNCHER_EXPORT gboolean webview_get_allow_universal_access_from_file_urls(void* webview)
{
    webView* wv = (webView*)webview;
    WebKitSettings *settings = webkit_web_view_get_settings(wv->view);
    return webkit_settings_get_allow_universal_access_from_file_urls(settings);
}

LAUNCHER_EXPORT void webview_set_allow_universal_access_from_file_urls(void* webview, gboolean allowed)
{
    webView* wv = (webView*)webview;
    WebKitSettings *settings = webkit_web_view_get_settings(wv->view);
    webkit_settings_set_allow_universal_access_from_file_urls(settings, allowed);
}

LAUNCHER_EXPORT gboolean webview_get_enable_write_console_messages_to_stdout(void* webview)
{
    webView* wv = (webView*)webview;
    WebKitSettings *settings = webkit_web_view_get_settings(wv->view);
    return webkit_settings_get_enable_write_console_messages_to_stdout(settings);
}

LAUNCHER_EXPORT void webview_set_enable_write_console_messages_to_stdout(void* webview, gboolean enabled)
{
    webView* wv = (webView*)webview;
    WebKitSettings *settings = webkit_web_view_get_settings(wv->view);
    webkit_settings_set_enable_write_console_messages_to_stdout(settings, enabled);
}

LAUNCHER_EXPORT void webview_register_script_message_handler(void* webview, const gchar *name, callback_script_message_received_evnt_fn handler)
{
    webView* wv = (webView*)webview;

    if (handler)
    {
        const char* signal_name = "script-message-received::";
        char detail_signal_name[strlen(signal_name)+strlen(name)];

        strcpy(detail_signal_name, signal_name);
        strcat(detail_signal_name, name);

        g_signal_connect (wv->contentManager, detail_signal_name, G_CALLBACK (handler), NULL);
    }

    webkit_user_content_manager_register_script_message_handler(wv->contentManager, name);
}

LAUNCHER_EXPORT void webview_unregister_script_message_handler(void* webview, const gchar *name, callback_script_message_received_evnt_fn handler)
{
    webView* wv = (webView*)webview;

    if (handler)
    {
        g_signal_handlers_disconnect_by_func(wv->view, G_CALLBACK(handler), NULL);
    }

    webkit_user_content_manager_unregister_script_message_handler(wv->contentManager, name);
}

LAUNCHER_EXPORT char* get_js_result_message(void* js_result)
{
    JSCValue *val = webkit_javascript_result_get_js_value((WebKitJavascriptResult*)js_result);
    return jsc_value_to_string(val);
}