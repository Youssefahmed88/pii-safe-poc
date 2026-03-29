import re

# keeping it simple for the mvp with python's standard 're'
# in the actual gsoc project this gets swapped out for the native rust 'rure' bindings for max speed
EMAIL_REGEX = re.compile(r"([a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+)")
IP_REGEX = re.compile(r"(\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b)")

def scrub_fast_path(text: str) -> tuple[str, int]:
    # quick sweep for obvious pii marker (ips and email for now)
    # return cleaned text and how much things we actualy catch
    caught = [0] # using list to avoid closure scope issue
    
    # redact ips
    def ip_repl(match):
        caught[0] += 1
        return "[REDACTED_IP]"
        
    text = IP_REGEX.sub(ip_repl, text)

    # redact email
    def email_repl(match):
        caught[0] += 1
        return "[REDACTED_EMAIL]"
        
    text = EMAIL_REGEX.sub(email_repl, text)
    
    return text, caught[0]

def traverse_ast_and_sanitize(node: any) -> tuple[any, int]:
    # magical recursive function. we walk json tree keeping structural key intact
    # but deeply scrub any raw string value we stumble across
    total_caught = 0
    
    if isinstance(node, dict):
        clean_dict = {}
        for k, v in node.items():
            # if it string scrub it. if it another dict/list dive deep
            if isinstance(v, str):
                safe_val, count = scrub_fast_path(v)
                clean_dict[k] = safe_val
                total_caught += count
            elif isinstance(v, (dict, list)):
                safe_val, count = traverse_ast_and_sanitize(v)
                clean_dict[k] = safe_val
                total_caught += count
            else:
                # int, bool etc is implicit safe from regex injection
                clean_dict[k] = v
        return clean_dict, total_caught
        
    elif isinstance(node, list):
        clean_list = []
        for item in node:
            if isinstance(item, str):
                safe_item, count = scrub_fast_path(item)
                clean_list.append(safe_item)
                total_caught += count
            elif isinstance(item, (dict, list)):
                safe_item, count = traverse_ast_and_sanitize(item)
                clean_list.append(safe_item)
                total_caught += count
            else:
                clean_list.append(item)
        return clean_list, total_caught
        
    elif isinstance(node, str):
        # we hit raw string right at root (rare but happen)
        return scrub_fast_path(node)
        
    # catch all for basic type like none int bool
    return node, 0
