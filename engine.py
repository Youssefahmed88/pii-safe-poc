import re

EMAIL_REGEX = re.compile(r'([a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+)')
IP_REGEX = re.compile(r'(\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b)')

def scrub_fast_path(text: str) -> tuple[str, int]:
    caught = [0]
    def ip_repl(match):
        caught[0] += 1
        return '[REDACTED_IP]'
    text = IP_REGEX.sub(ip_repl, text)
    def email_repl(match):
        caught[0] += 1
        return '[REDACTED_EMAIL]'
    text = EMAIL_REGEX.sub(email_repl, text)
    return text, caught[0]

def traverse_ast_and_sanitize(node: any) -> tuple[any, int]:
    total_caught = 0
    if isinstance(node, dict):
        clean_dict = {}
        for k, v in node.items():
            if isinstance(v, str):
                safe_val, count = scrub_fast_path(v)
                clean_dict[k] = safe_val
                total_caught += count
            elif isinstance(v, (dict, list)):
                safe_val, count = traverse_ast_and_sanitize(v)
                clean_dict[k] = safe_val
                total_caught += count
            else:
                clean_dict[k] = v
        return clean_dict, total_caught
    return node, 0
