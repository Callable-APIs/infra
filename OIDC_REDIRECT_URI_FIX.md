# OIDC Redirect URI Fix - Services Container

## Problem Summary

The OIDC authentication flow is failing because the services container is using an HTTP redirect URI (`http://api.callableapis.com/api/auth/callback`) instead of HTTPS (`https://api.callableapis.com/api/auth/callback`). This causes GitHub OAuth to reject the callback or redirect incorrectly.

## Current Behavior

When accessing `/api/auth/login`, the container:
1. ✅ Successfully reads from AWS Parameter Store
2. ❌ Retrieves the old HTTP value (`http://api.callableapis.com/api/auth/callback`) instead of the updated HTTPS value
3. ❌ Generates OAuth URL with HTTP redirect URI: `https://github.com/login/oauth/authorize?client_id=...&redirect_uri=http%3A%2F%2Fapi.callableapis.com%2Fapi%2Fauth%2Fcallback&...`
4. ❌ GitHub rejects the OAuth request or redirects incorrectly

## Infrastructure Changes (Already Completed)

1. **Parameter Store Updated**: The redirect URI in AWS Parameter Store (`/callableapis/github/redirect-uri`) has been updated to HTTPS:
   - **Current Value**: `https://api.callableapis.com/api/auth/callback`
   - **Parameter Version**: 7
   - **Region**: `us-west-2`

2. **Container Environment**: AWS credentials and region are now properly configured:
   - `AWS_ACCESS_KEY_ID`: Set
   - `AWS_SECRET_ACCESS_KEY`: Set
   - `AWS_DEFAULT_REGION`: `us-west-2`

3. **Verification**: We can confirm Parameter Store has the correct HTTPS value:
   ```bash
   aws ssm get-parameter --name "/callableapis/github/redirect-uri" --region us-west-2
   # Returns: "https://api.callableapis.com/api/auth/callback"
   ```

## Root Cause

The Java `ParameterStoreService` is caching the old HTTP value. Even after:
- Restarting the container
- Updating Parameter Store to HTTPS
- Setting AWS region explicitly

The container logs show it's still fetching the HTTP value:
```
Successfully retrieved parameter from Parameter Store: /callableapis/github/redirect-uri = http://api.callableapis.com/api/auth/callback
```

This suggests the Java SDK is either:
1. Caching aggressively with a long TTL
2. Reading from a different region
3. Not invalidating cache on parameter updates
4. Using a stale cached value that was fetched before the update

## Required Fix

The services agent needs to update the Java code to:

1. **Force cache invalidation** when Parameter Store values change, OR
2. **Reduce cache TTL** for the redirect URI parameter, OR
3. **Add cache-busting mechanism** (e.g., version-based cache keys), OR
4. **Force refresh** the redirect URI parameter on container startup/health check

### Recommended Approach

Add a mechanism to detect parameter version changes and invalidate cache:

```java
// Pseudo-code example
public String getRedirectUri() {
    ParameterStoreService service = getParameterStoreService();
    String cachedValue = cache.get("redirect-uri");
    int cachedVersion = cache.get("redirect-uri-version");
    
    // Check current version in Parameter Store
    int currentVersion = service.getParameterVersion("/callableapis/github/redirect-uri");
    
    if (cachedVersion != currentVersion || cachedValue == null) {
        // Force refresh
        String newValue = service.getParameter("/callableapis/github/redirect-uri");
        cache.put("redirect-uri", newValue);
        cache.put("redirect-uri-version", currentVersion);
        return newValue;
    }
    
    return cachedValue;
}
```

Alternatively, reduce cache TTL or add a manual cache refresh endpoint.

## Expected Behavior After Fix

1. Container reads HTTPS redirect URI from Parameter Store
2. OAuth URL generated with HTTPS: `https://github.com/login/oauth/authorize?client_id=...&redirect_uri=https%3A%2F%2Fapi.callableapis.com%2Fapi%2Fauth%2Fcallback&...`
3. GitHub OAuth flow completes successfully
4. Callback redirects to `https://api.callableapis.com/api/auth/callback` with authorization code

## Verification Steps

After the fix is deployed:

1. **Check container logs** for redirect URI:
   ```bash
   docker logs callableapis-services | grep "redirect-uri"
   # Should show: https://api.callableapis.com/api/auth/callback
   ```

2. **Test OAuth login endpoint**:
   ```bash
   curl -v "https://api.callableapis.com/api/auth/login"
   # Location header should contain: redirect_uri=https%3A%2F%2Fapi.callableapis.com...
   ```

3. **Verify OAuth flow**:
   - Visit `https://api.callableapis.com/api/auth/login`
   - Should redirect to GitHub OAuth
   - After authorization, should redirect back to `https://api.callableapis.com/api/auth/callback` with code

## Additional Context

- **Parameter Store Path**: `/callableapis/github/redirect-uri`
- **Parameter Type**: `String`
- **Current Value**: `https://api.callableapis.com/api/auth/callback`
- **Region**: `us-west-2`
- **Container**: `rl337/callableapis:services`
- **Java Class**: `com.callableapis.api.config.ParameterStoreService`
- **Related Classes**: `com.callableapis.api.handlers.AuthResource`, `com.callableapis.api.config.AppConfig`

## Contact

If you need to verify Parameter Store values or test infrastructure changes, the infra repository has the necessary AWS credentials and tools configured.

