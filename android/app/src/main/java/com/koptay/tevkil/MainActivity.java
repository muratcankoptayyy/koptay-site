package com.koptay.tevkil;

import android.os.Bundle;
import android.webkit.WebSettings;
import android.webkit.WebView;
import com.getcapacitor.BridgeActivity;

public class MainActivity extends BridgeActivity {
    
    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        
        // Get the WebView and optimize settings
        WebView webView = getBridge().getWebView();
        if (webView != null) {
            WebSettings settings = webView.getSettings();
            
            // Enable hardware acceleration for better performance
            webView.setLayerType(WebView.LAYER_TYPE_HARDWARE, null);
            
            // Cache settings for better offline performance
            settings.setCacheMode(WebSettings.LOAD_DEFAULT);
            settings.setAppCacheEnabled(true);
            
            // Enable DOM storage (required for modern web apps)
            settings.setDomStorageEnabled(true);
            settings.setDatabaseEnabled(true);
            
            // Allow mixed content (HTTPS page loading HTTP resources)
            // Only if your backend requires it
            settings.setMixedContentMode(WebSettings.MIXED_CONTENT_COMPATIBILITY_MODE);
            
            // Disable text zoom (prevents layout issues)
            settings.setTextZoom(100);
            
            // Enable smooth scrolling
            webView.setScrollBarStyle(WebView.SCROLLBARS_OUTSIDE_OVERLAY);
            webView.setScrollbarFadingEnabled(true);
            
            // Better font rendering
            settings.setMinimumFontSize(8);
            settings.setMinimumLogicalFontSize(8);
            
            // Enable geolocation (if you need location features)
            settings.setGeolocationEnabled(true);
            
            // Enable media playback
            settings.setMediaPlaybackRequiresUserGesture(false);
        }
    }
}
