def adapt_text_size(text: str, max_size=1.0, min_size=0.625):
    return max(min_size, min(max_size, 1.5 / len(text)))


def truncateText(text, max_chars=10):
    return text if len(text) <= max_chars else text[:max_chars-3] + '...'


def wrapText(text: str, max_chars_per_line=10):
    words = text.split(' ')
    lines = []
    current_line = ''

    for word in words:
        if len(current_line + ' ' + word) <= max_chars_per_line:
            if current_line != '':
                current_line += ' '
            current_line += word
        else:
            lines.append(current_line)
            current_line = word
    lines.append(current_line)

    return '\n'.join(lines)
