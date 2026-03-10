import re
from urllib.parse import urlparse, parse_qs
import ipaddress

def validate_url(text):
    """
    Validates and parses URL structure.
    Returns parsed URL components and validation status.
    """
    try:
        # Add scheme if missing for proper parsing
        url = text.strip()
        if not url.startswith(('http://', 'https://', 'ftp://')):
            if url.startswith('www.'):
                url = 'https://' + url
            else:
                # Try adding https:// for parsing
                url = 'https://' + url
        
        parsed = urlparse(url)
        
        # Check if domain exists
        if not parsed.netloc:
            return None, "Invalid URL structure"
        
        return {
            'scheme': parsed.scheme,
            'domain': parsed.netloc,
            'path': parsed.path,
            'params': parsed.params,
            'query': parsed.query,
            'fragment': parsed.fragment,
            'original': text.strip()
        }, None
    except Exception as e:
        return None, str(e)


def check_suspicious_url_patterns(url_parts, original_text):
    """
    Analyzes URL for phishing patterns and returns risk indicators.
    """
    risks = []
    risk_score = 0
    
    if not url_parts:
        return risks, risk_score
    
    domain = url_parts['domain'].lower()
    scheme = url_parts['scheme'].lower()
    path = url_parts['path'].lower()
    query = url_parts['query'].lower()
    
    # 1. Check for HTTP (insecure protocol)
    if scheme == 'http':
        risks.append({
            'category': 'insecure_protocol',
            'message': 'Uses insecure HTTP protocol (not HTTPS)',
            'score': 25
        })
        risk_score += 25
    
    # 2. Check for IP address instead of domain
    try:
        # Remove port if present
        domain_without_port = domain.split(':')[0]
        ipaddress.ip_address(domain_without_port)
        risks.append({
            'category': 'ip_address',
            'message': 'Uses IP address instead of domain name',
            'score': 35
        })
        risk_score += 35
    except ValueError:
        pass  # Not an IP address, which is good
    
    # 3. Check for suspicious TLDs (top-level domains)
    suspicious_tlds = ['.tk', '.ml', '.ga', '.cf', '.gq', '.xyz', '.top', '.win', 
                       '.loan', '.download', '.click', '.stream', '.review', '.country',
                       '.kim', '.cricket', '.science', '.work', '.party', '.webcam']
    for tld in suspicious_tlds:
        if domain.endswith(tld):
            risks.append({
                'category': 'suspicious_tld',
                'message': f'Uses suspicious top-level domain: {tld}',
                'score': 30
            })
            risk_score += 30
            break
    
    # 4. Check for URL shorteners
    url_shorteners = ['bit.ly', 'tinyurl.com', 'goo.gl', 't.co', 'ow.ly', 
                      'is.gd', 'buff.ly', 'adf.ly', 'short.link', 'cutt.ly',
                      's.id', 'rb.gy', 'tiny.cc', 'clck.ru']
    for shortener in url_shorteners:
        if shortener in domain:
            risks.append({
                'category': 'url_shortener',
                'message': 'Uses URL shortener which can hide true destination',
                'score': 25
            })
            risk_score += 25
            break
    
    # 5. Check for excessive subdomains (potential domain spoofing)
    subdomain_count = domain.count('.')
    if subdomain_count > 3:
        risks.append({
            'category': 'excessive_subdomains',
            'message': f'Excessive subdomains detected ({subdomain_count} dots)',
            'score': 20
        })
        risk_score += 20
    
    # 6. Check for suspicious keywords in domain
    suspicious_domain_keywords = ['login', 'verify', 'account', 'secure', 'update',
                                  'banking', 'paypal', 'amazon', 'microsoft', 'apple',
                                  'signin', 'password', 'confirm', 'validation']
    for keyword in suspicious_domain_keywords:
        if keyword in domain:
            risks.append({
                'category': 'suspicious_domain_keyword',
                'message': f"Domain contains suspicious keyword: '{keyword}'",
                'score': 20
            })
            risk_score += 20
            break
    
    # 7. Check for hyphens in domain (common in phishing)
    if domain.count('-') > 2:
        risks.append({
            'category': 'excessive_hyphens',
            'message': f'Excessive hyphens in domain ({domain.count("-")} hyphens)',
            'score': 15
        })
        risk_score += 15
    elif '-' in domain:
        risks.append({
            'category': 'hyphen_detected',
            'message': 'Hyphen detected in domain (common in phishing)',
            'score': 10
        })
        risk_score += 10
    
    # 8. Check for @ symbol in URL (credential phishing)
    if '@' in original_text:
        risks.append({
            'category': 'at_symbol',
            'message': 'URL contains @ symbol (potential credential phishing)',
            'score': 40
        })
        risk_score += 40
    
    # 9. Check URL length (very long URLs are suspicious)
    if len(original_text) > 75:
        risks.append({
            'category': 'long_url',
            'message': f'Unusually long URL ({len(original_text)} characters)',
            'score': 15
        })
        risk_score += 15
    
    # 10. Check for suspicious path keywords
    suspicious_path_keywords = ['login', 'signin', 'verify', 'account', 'update',
                                'secure', 'banking', 'confirm', 'validate', 'password']
    for keyword in suspicious_path_keywords:
        if keyword in path:
            risks.append({
                'category': 'suspicious_path',
                'message': f"URL path contains suspicious keyword: '{keyword}'",
                'score': 15
            })
            risk_score += 15
            break
    
    # 11. Check for hidden redirects in query parameters
    redirect_params = ['redirect', 'url', 'return', 'goto', 'next', 'callback']
    for param in redirect_params:
        if param in query:
            risks.append({
                'category': 'redirect_parameter',
                'message': 'URL contains redirect parameter (potential phishing)',
                'score': 20
            })
            risk_score += 20
            break
    
    # 12. Check for homograph attacks (lookalike characters)
    # Common substitutions: 0 for O, 1 for l, etc.
    suspicious_chars = ['ߋ', 'о', 'а', 'е', 'с', 'р', 'х', 'у', '0', '1']  # Cyrillic and numbers
    for char in suspicious_chars:
        if char in domain and domain.count(char) > 0:
            risks.append({
                'category': 'homograph_attack',
                'message': 'Potential homograph attack (lookalike characters)',
                'score': 35
            })
            risk_score += 35
            break
    
    return risks, risk_score


def check_message_risk_patterns(text):
    """
    Analyzes text messages for phishing and scam indicators.
    Returns list of risk indicators and risk score.
    """
    risks = []
    risk_score = 0
    text_lower = text.lower()
    
    # 1. Urgency keywords
    urgency_keywords = ['urgent', 'immediately', 'asap', 'right now', 'hurry',
                        'expires today', 'limited time', 'act now', 'don\'t wait',
                        'expire', 'deadline', 'final notice', 'last chance']
    for keyword in urgency_keywords:
        if keyword in text_lower:
            risks.append({
                'category': 'urgency',
                'message': f"Contains urgency keyword: '{keyword}'",
                'score': 20
            })
            risk_score += 20
            break
    
    # 2. Credential/account keywords
    credential_keywords = ['password', 'username', 'login', 'signin', 'sign in',
                          'credentials', 'passcode', 'pin', 'security code',
                          'verify account', 'confirm identity', 'validate']
    for keyword in credential_keywords:
        if keyword in text_lower:
            risks.append({
                'category': 'credential_request',
                'message': f"Requests credentials: '{keyword}'",
                'score': 25
            })
            risk_score += 25
            break
    
    # 3. Financial keywords
    financial_keywords = ['bank', 'credit card', 'debit card', 'account number',
                          'routing number', 'ssn', 'social security', 'tax',
                          'refund', 'payment', 'billing', 'invoice', 'wire transfer']
    for keyword in financial_keywords:
        if keyword in text_lower:
            risks.append({
                'category': 'financial',
                'message': f"Contains financial keyword: '{keyword}'",
                'score': 20
            })
            risk_score += 20
            break
    
    # 4. Threat/fear keywords
    threat_keywords = ['suspended', 'locked', 'blocked', 'closed', 'terminated',
                       'unauthorized', 'illegal', 'fraud', 'compromised',
                       'unusual activity', 'suspicious activity', 'security alert']
    for keyword in threat_keywords:
        if keyword in text_lower:
            risks.append({
                'category': 'threat',
                'message': f"Uses threatening language: '{keyword}'",
                'score': 25
            })
            risk_score += 25
            break
    
    # 5. Reward/prize keywords
    reward_keywords = ['winner', 'won', 'prize', 'reward', 'free', 'gift',
                       'claim', 'congratulations', 'selected', 'lottery',
                       'inheritance', 'million dollars', 'cash']
    for keyword in reward_keywords:
        if keyword in text_lower:
            risks.append({
                'category': 'reward_scam',
                'message': f"Promises rewards/prizes: '{keyword}'",
                'score': 30
            })
            risk_score += 30
            break
    
    # 6. Action keywords (click, download, open)
    action_keywords = ['click here', 'click this', 'download', 'open attachment',
                       'click link', 'follow link', 'tap here', 'install']
    for keyword in action_keywords:
        if keyword in text_lower:
            risks.append({
                'category': 'action_request',
                'message': f"Requests immediate action: '{keyword}'",
                'score': 15
            })
            risk_score += 15
            break
    
    # 7. Verification/update requests
    verification_keywords = ['verify', 'update', 'confirm', 'validate', 'review',
                            'check', 'reactivate', 'restore', 'renew']
    for keyword in verification_keywords:
        if keyword in text_lower:
            risks.append({
                'category': 'verification_request',
                'message': f"Requests verification/update: '{keyword}'",
                'score': 15
            })
            risk_score += 15
            break
    
    # 8. Check for excessive punctuation (!!!, ???)
    if '!!!' in text or '???' in text or text.count('!') > 3:
        risks.append({
            'category': 'excessive_punctuation',
            'message': 'Excessive punctuation detected (common in scams)',
            'score': 10
        })
        risk_score += 10
    
    # 9. Check for ALL CAPS (more than 30% of text)
    caps_count = sum(1 for c in text if c.isupper())
    if len(text) > 10 and caps_count / len(text) > 0.3:
        risks.append({
            'category': 'excessive_caps',
            'message': 'Excessive capitalization detected',
            'score': 10
        })
        risk_score += 10
    
    # 10. Check for suspicious email/phone patterns
    if re.search(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', text):
        risks.append({
            'category': 'contains_email',
            'message': 'Contains email address (verify sender)',
            'score': 5
        })
        risk_score += 5
    
    # 11. Check for phone numbers
    if re.search(r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b', text):
        risks.append({
            'category': 'contains_phone',
            'message': 'Contains phone number (verify legitimacy)',
            'score': 5
        })
        risk_score += 5
    
    # 12. Very short messages with links (suspicious)
    if len(text) < 20 and ('http' in text_lower or 'www' in text_lower):
        risks.append({
            'category': 'short_with_link',
            'message': 'Very short message with link (suspicious)',
            'score': 15
        })
        risk_score += 15
    
    return risks, risk_score


def detect_input_type(text):
    """
    Enhanced input detection that determines if input is URL or MESSAGE,
    and performs comprehensive risk analysis.
    
    Returns:
        dict: {
            'type': 'URL' or 'MESSAGE',
            'analysis': detailed analysis results,
            'risks': list of risk indicators,
            'risk_score': total risk score from detection
        }
    """
    # URL pattern detection
    url_pattern = re.compile(
        r'^(https?://|ftp://|www\.)|'  # Starts with protocol or www
        r'[a-zA-Z0-9-]+\.[a-zA-Z]{2,}',  # Or contains domain pattern
        re.IGNORECASE
    )
    
    is_url = bool(url_pattern.match(text.strip()))
    
    # If it looks like a URL, validate and analyze it
    if is_url:
        url_parts, error = validate_url(text)
        if url_parts:
            risks, risk_score = check_suspicious_url_patterns(url_parts, text)
            return {
                'type': 'URL',
                'analysis': url_parts,
                'risks': risks,
                'risk_score': risk_score,
                'error': None
            }
        else:
            # Invalid URL format
            return {
                'type': 'URL',
                'analysis': None,
                'risks': [{'category': 'invalid_url', 'message': 'Invalid URL format', 'score': 20}],
                'risk_score': 20,
                'error': error
            }
    else:
        # Treat as message and analyze for phishing patterns
        risks, risk_score = check_message_risk_patterns(text)
        return {
            'type': 'MESSAGE',
            'analysis': {'text': text},
            'risks': risks,
            'risk_score': risk_score,
            'error': None
        }
