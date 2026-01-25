def chunk_text(text: str, max_chars=1000):
    """
    Chunk text into manageable pieces, respecting natural boundaries where possible.
    """
    # First split by double newlines (paragraphs)
    paragraphs = text.split("\n\n")
    
    refined_paragraphs = []
    
    # Second pass: break down large paragraphs
    for p in paragraphs:
        if len(p) <= max_chars:
            refined_paragraphs.append(p)
        else:
            # Split by single newline
            lines = p.split("\n")
            for line in lines:
                if len(line) <= max_chars:
                    refined_paragraphs.append(line)
                else:
                    # Split by sentences (naive)
                    sentences = line.split(". ")
                    for sent in sentences:
                        # Re-add the dot if it wasn't the last one
                        if sent != sentences[-1]:
                            sent += "."
                        
                        if len(sent) <= max_chars:
                            refined_paragraphs.append(sent)
                        else:
                            # Hard split
                            for i in range(0, len(sent), max_chars):
                                refined_paragraphs.append(sent[i:i + max_chars])

    chunks = []
    current = ""

    for p in refined_paragraphs:
        # +2 for the separator (e.g. \n\n or \n) we effectively add back
        if len(current) + len(p) + 2 < max_chars:
            current += p + "\n\n"
        else:
            if current.strip():
                chunks.append(current.strip())
            current = p + "\n\n"

    if current.strip():
        chunks.append(current.strip())

    return chunks
