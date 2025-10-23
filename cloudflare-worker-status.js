// Cloudflare Worker for status.callableapis.com
// Proxies requests to Google Cloud Node 1 port 8081

addEventListener('fetch', event => {
  event.respondWith(handleRequest(event.request))
})

async function handleRequest(request) {
  // Target server (Google Cloud Node 1)
  const targetHost = '35.233.161.8'
  const targetPort = '8081'
  
  // Construct the target URL
  const url = new URL(request.url)
  const targetUrl = `http://${targetHost}:${targetPort}${url.pathname}${url.search}`
  
  // Create new request with the target URL
  const modifiedRequest = new Request(targetUrl, {
    method: request.method,
    headers: request.headers,
    body: request.body
  })
  
  try {
    // Forward the request to the target server
    const response = await fetch(modifiedRequest)
    
    // Return the response with CORS headers
    const modifiedResponse = new Response(response.body, {
      status: response.status,
      statusText: response.statusText,
      headers: {
        ...response.headers,
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Methods': 'GET, POST, PUT, DELETE, OPTIONS',
        'Access-Control-Allow-Headers': 'Content-Type, Authorization',
        'X-Forwarded-By': 'Cloudflare-Worker'
      }
    })
    
    return modifiedResponse
  } catch (error) {
    // Return error response if target is unreachable
    return new Response(JSON.stringify({
      error: 'Service Unavailable',
      message: 'Status dashboard is temporarily unavailable',
      details: error.message
    }), {
      status: 503,
      statusText: 'Service Unavailable',
      headers: {
        'Content-Type': 'application/json',
        'Access-Control-Allow-Origin': '*'
      }
    })
  }
}
