package org.telegram.messenger;

import java.net.URI;

/** Transport validation shared by AI requests which may carry private text or keys. */
public final class SecureAiUrl {
    private SecureAiUrl() {}

    public static String requireHttps(String value) {
        final URI uri;
        try {
            uri = URI.create(value);
        } catch (Exception e) {
            throw new IllegalArgumentException("Invalid AI endpoint");
        }
        if (!"https".equalsIgnoreCase(uri.getScheme()) || uri.getHost() == null
                || uri.getRawUserInfo() != null || uri.getRawFragment() != null) {
            throw new IllegalArgumentException("AI endpoint must use HTTPS without URL credentials");
        }
        return value;
    }
}
