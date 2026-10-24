import ipaddress
import socket
import re
from urllib.parse import urlparse
import httpx

BLOCKED_IP_NETWORKS = [
    ipaddress.ip_network("127.0.0.0/8"),
    ipaddress.ip_network("10.0.0.0/8"),
    ipaddress.ip_network("172.16.0.0/12"),
    ipaddress.ip_network("192.168.0.0/16"),
    ipaddress.ip_network("169.254.0.0/16"),  # Link-local / Cloud Metadata
    ipaddress.ip_network("0.0.0.0/8"),
    ipaddress.ip_network("224.0.0.0/4"),     # Multicast
    ipaddress.ip_network("240.0.0.0/4"),     # Reserved
    ipaddress.ip_network("::1/128"),
    ipaddress.ip_network("fc00::/7"),        # Unique Local
    ipaddress.ip_network("fe80::/10"),       # Link-local IPv6
]

def is_ip_blocked(ip_str: str) -> bool:
    try:
        ip = ipaddress.ip_address(ip_str)
        return any(ip in network for network in BLOCKED_IP_NETWORKS)
    except ValueError:
        return True

def validate_target_url(url: str) -> str:
    parsed = urlparse(url)
    if parsed.scheme.lower() not in ("http", "https"):
        raise ValueError("Only HTTP and HTTPS URLs are permitted.")
    
    hostname = parsed.hostname
    if not hostname:
        raise ValueError("Invalid target URL: missing hostname.")
    
    # Check for direct IP address
    try:
        if is_ip_blocked(hostname):
            raise ValueError("Access to local, private, or metadata network addresses is prohibited.")
    except ValueError:
        pass
    
    # Resolve hostname to verify DNS does not resolve to private IP
    try:
        addr_info = socket.getaddrinfo(hostname, None)
        for family, _, _, _, sockaddr in addr_info:
            ip_candidate = sockaddr[0]
            if is_ip_blocked(ip_candidate):
                raise ValueError(f"Target domain resolves to prohibited address ({ip_candidate}).")
    except socket.gaierror:
        raise ValueError(f"Unable to resolve host: {hostname}")
    
    return url

async def fetch_job_url_safely(url: str) -> dict:
    validated_url = validate_target_url(url)
    
    headers = {
        "User-Agent": "Careerloom-JobVerifier/1.0 (+https://careerloom.gov.in/bot)",
        "Accept": "text/html,application/xhtml+xml,text/plain"
    }
    
    async with httpx.AsyncClient(timeout=8.0, follow_redirects=True, max_redirects=3) as client:
        try:
            response = await client.get(validated_url, headers=headers)
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to retrieve URL: {str(e)}",
                "content": "",
                "title": "",
                "url": url
            }
            
        if response.status_code >= 400:
            return {
                "success": False,
                "error": f"Server responded with status code {response.status_code}",
                "content": "",
                "title": "",
                "url": str(response.url)
            }
            
        # Enforce size limit (max 500 KB)
        content_bytes = response.content[:500_000]
        text_content = content_bytes.decode('utf-8', errors='ignore')
        
        # Extract title
        title_match = re.search(r'<title>(.*?)</title>', text_content, re.IGNORECASE | re.DOTALL)
        title = title_match.group(1).strip() if title_match else ""
        
        # Clean HTML tags to text
        clean_text = re.sub(r'<(script|style).*?</\1>', ' ', text_content, flags=re.IGNORECASE | re.DOTALL)
        clean_text = re.sub(r'<[^>]+>', ' ', clean_text)
        clean_text = re.sub(r'\s+', ' ', clean_text).strip()
        
        return {
            "success": True,
            "error": None,
            "url": str(response.url),
            "title": title,
            "content": clean_text[:10000],  # Return first 10,000 chars for processing
            "content_length": len(clean_text)
        }
