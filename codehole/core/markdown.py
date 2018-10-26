# pylint: disable=all
import re
import html
from io import StringIO

NODE_KINDS = [
    'br', 'text', 'link', 'img', 'bold', 'italic',
    'h1', 'h2', 'h3', 'h4', 'h5', 'h6',
    'code', 'pre', 'blockquote', 'ul', 'ol', 'li', 'p', 'root']


class Node:

    kind = None
    is_leaf = True

    def html(self):
        raise NotImplementedError


class TextNode(Node):
    kind = 'text'
    is_leaf = True

    def __init__(self, text):
        self.text = text

    def html(self):
        return self.text


class LineBreakNode(Node):
    kind = 'br'
    is_leaf = True

    def html(self):
        return '<br/>'


class LinkNode(Node):
    kind = 'link'
    is_leaf = True

    def __init__(self, text, url):
        self.text = text
        self.url = url

    def html(self):
        return '<a href="%s" target="_blank">%s</a>' % (self.url, self.text)


class ImageNode(Node):
    kind = 'img'
    is_leaf = True

    def __init__(self, alt, src):
        self.alt = alt
        self.src = src

    def html(self):
        return '<img src="%s" alt="%s"/>' % (self.src, self.alt)


class BoldNode(Node):
    kind = 'bold'
    is_leaf = True

    def __init__(self, text):
        self.text = text

    def html(self):
        return '<strong>%s</strong>' % self.text


class ItalicNode(Node):
    kind = 'italic'
    is_leaf = True

    def __init__(self, text):
        self.text = text

    def html(self):
        return '<i>%s</i>' % self.text


class HeadingNode(Node):
    kind = None
    is_leaf = True

    def __init__(self, text):
        self.text = text

    def html(self):
        return '<%s>%s</%s>' % (self.kind, self.text, self.kind)


class H1Node(HeadingNode):
    kind = 'h1'


class H2Node(HeadingNode):
    kind = 'h2'


class H3Node(HeadingNode):
    kind = 'h3'


class H4Node(HeadingNode):
    kind = 'h4'


class H5Node(HeadingNode):
    kind = 'h5'


class H6Node(HeadingNode):
    kind = 'h6'


class BlockQuoteNode(Node):
    kind = 'blockquote'
    is_leaf = True

    def __init__(self, text):
        self.text = text

    def html(self):
        return '<blockquote>%s</blockquote>' % self.text


class CodeNode(Node):
    kind = 'code'
    is_leaf = True

    def __init__(self, text):
        self.text = text

    def html(self):
        return '<code>%s</code>' % self.text


class PreNode(Node):
    kind = 'pre'
    is_leaf = True

    def __init__(self, text, language):
        self.text = text
        self.language = language

    def html(self):
        return '<pre><code>%s</code></pre>' % html.escape(self.text)


class OlNode(Node):
    kind = 'ul'
    is_leaf = False
    regex = re.compile('[0-9]+\.')

    def __init__(self, children):
        self.children = children

    def append(self, child):
        self.children.append(child)

    @classmethod
    def match(cls, line):
        return bool(cls.regex.match(line))

    @staticmethod
    def left(line):
        return line[line.index('.')+1:].strip()

    def html(self):
        childs = []
        for child in self.children:
            childs.append(child.html())
        return '<ol>%s</ol>' % ''.join(childs)


class UlNode(Node):
    kind = 'ol'
    is_leaf = False

    def __init__(self, children):
        self.children = children

    def append(self, child):
        self.children.append(child)

    @staticmethod
    def match(line):
        return (
            line.startswith('* ')
            or line.startswith('+ ')
            or line.startswith('- '))

    @staticmethod
    def left(line):
        return line[2:].strip()

    def html(self):
        childs = []
        for child in self.children:
            childs.append(child.html())
        return '<ul>%s</ul>' % ''.join(childs)


class LiNode(Node):
    kind = 'li'
    is_leaf = False

    def __init__(self, children):
        self.children = children

    def append(self, child):
        self.children.append(child)

    def html(self):
        childs = []
        for child in self.children:
            childs.append(child.html())
        return '<li>%s</li>' % ''.join(childs)


class BlockNode(Node):
    kind = 'p'
    is_leaf = False

    def __init__(self):
        self.children = []

    def append(self, child):
        self.children.append(child)

    def html(self):
        childs = []
        for child in self.children:
            childs.append(child.html())
        return '<p>%s</p>' % ''.join(childs)


class RootNode(Node):
    kind = 'root'
    is_leaf = False

    def __init__(self, children):
        self.children = children

    def append(self, child):
        self.children.append(child)

    def html(self):
        childs = []
        for child in self.children:
            childs.append(child.html())
        return ''.join(childs)


class Context:

    def __init__(self):
        self.root = RootNode([])

    def render(self):
        return self.root.html()


def markdown(source):
    ctx = Context()
    lines = source.strip().split("\n")
    lines = [line for line in lines]
    i = 0
    while i < len(lines):
        line = lines[i].strip()
        # 空行
        if not line:
            ctx.root.append(LineBreakNode())
            i += 1
            continue
        # h1~h6
        if line.startswith('######'):
            ctx.root.append(H6Node(line[6:].strip()))
            i += 1
            continue
        elif line.startswith('#####'):
            ctx.root.append(H5Node(line[5:].strip()))
            i += 1
            continue
        elif line.startswith('####'):
            ctx.root.append(H4Node(line[4:].strip()))
            i += 1
            continue
        elif line.startswith('###'):
            ctx.root.append(H3Node(line[3:].strip()))
            i += 1
            continue
        elif line.startswith('##'):
            ctx.root.append(H2Node(line[2:].strip()))
            i += 1
            continue
        elif line.startswith('#'):
            ctx.root.append(H1Node(line[1:].strip()))
            i += 1
            continue
        # blockquote
        if line.startswith('>'):
            ctx.root.append(BlockQuoteNode(line[1:].strip()))
            i += 1
            continue
        # pre code
        if line.startswith('```'):
            if line.find('```', 3) == -1:  # not inline code
                language = line[3:].strip()
                i += 1
                codes = []
                while i < len(lines):
                    if not lines[i].startswith('```'):  # scan til code end
                        codes.append(lines[i])
                        i += 1
                        continue
                    i += 1
                    break
                ctx.root.append(PreNode('\n'.join(codes), language))
                continue
        # image node
        if line.startswith('!['):
            idx = line.find(']', 2)
            if idx > 0:
                alt = line[2: idx].strip()
                if idx == len(line) - 1 or line[idx+1] != '(':
                    ctx.root.append(ImageNode(alt, ""))
                    i += 1
                    continue
                end = line.find(')', idx+2)
                # end=-1 means end of line
                if end > 0:
                    url = line[idx+2:end].strip()
                else:
                    url = line[idx+2:].strip()
                ctx.root.append(ImageNode(alt, url))
                i += 1
                continue
            else:
                alt = line[2:].strip()
                url = ""
                ctx.root.append(ImageNode(alt, url))
                i += 1
                continue
        # ol
        if OlNode.match(line):
            ol = OlNode([])
            while i < len(lines):
                line = lines[i]
                if OlNode.match(line):
                    li = LiNode([])
                    for node in md_inline(OlNode.left(line)):
                        li.append(node)
                    ol.append(li)
                    i += 1
                    continue
                break
            ctx.root.append(ol)
            continue
        # ul
        if UlNode.match(line):
            ul = UlNode([])
            while i < len(lines):
                line = lines[i]
                if UlNode.match(line):
                    li = LiNode([])
                    for node in md_inline(UlNode.left(line)):
                        li.append(node)
                    ul.append(li)
                    i += 1
                    continue
                break
            ctx.root.append(ul)
            continue
        block = BlockNode()
        for node in md_inline(line):
            block.append(node)
        ctx.root.append(block)
        i += 1
    return ctx.render()


def md_inline(line):
    nodes = []
    text = StringIO()
    i = 0
    while i < len(line):
        if line[i] == '\\' and i < len(line) - 1:
            text.write(line[i+1])
            i += 2
            continue
        if line[i] not in('*', '[', '`'):
            text.write(line[i])
            i += 1
            continue
        if line[i] == '`' and line[i:i+3] != '```':
            text.write(line[i])
            i += 1
            continue
        nodes.append(TextNode(text.getvalue()))
        if line[i] == '*':
            nodes.extend(md_strong(line[i+1:]))
            return nodes
        if line[i] == '[':
            nodes.extend(md_link(line[i+1:]))
            return nodes
        if line[i] == '`':
            nodes.extend(md_code(line[i+3:]))
            return nodes
    if text.getvalue():
        nodes.append(TextNode(text.getvalue()))
    return nodes


def md_link(line):
    nodes = []
    text = StringIO()
    for i in range(len(line)):
        if line[i] == '\\' and i < len(line) - 1:
            text.write(line[i+1])
            i += 2
            continue
        if line[i] != ']':
            text.write(line[i])
            i += 1
            continue
        break
    if i >= len(line) - 1:
        nodes.append(LinkNode(text.getvalue(), ""))
        return nodes
    i += 1
    if line[i] != '(':
        nodes.append(LinkNode(text.getvalue(), ""))
        nodes.extend(md_inline(line[i:]))
        return nodes
    label = text.getvalue()
    text = StringIO()
    line = line[i+1:]
    for i in range(len(line)):
        if line[i] == '\\' and i < len(line) - 1:
            text.write(line[i+1])
            i += 2
            continue
        if line[i] != ')':
            text.write(line[i])
            i += 1
            continue
        nodes.append(LinkNode(label, text.getvalue()))
        nodes.extend(md_inline(line[i+1:]))
        return nodes
    nodes.append(LinkNode(label, text.getvalue()))
    return nodes


def md_strong(line):
    nodes = []
    text = StringIO()
    i = 0
    # skip multple *
    while i < len(line):
        if line[i] == '*':
            i += 1
            continue
        break
    while i < len(line):
        if line[i] == '\\' and i < len(line) - 1:
            text.write(line[i+1])
            i += 2
            continue
        if line[i] != '*':
            text.write(line[i])
            i += 1
            continue
        i += 1
        while i < len(line):
            if line[i] == '*':
                i += 1
                continue
            break
        nodes.append(BoldNode(text.getvalue()))
        nodes.extend(md_inline(line[i:]))
        return nodes
    nodes.append(BoldNode(text.getvalue()))
    return nodes


def md_code(line):
    nodes = []
    text = StringIO()
    i = 0
    while i < len(line):
        if line[i] == '\\' and i < len(line) - 1:
            text.write(line[i+1])
            i += 2
            continue
        if line[i:i+3] != '```':
            text.write(line[i])
            i += 1
            continue
        nodes.append(CodeNode(text.getvalue()))
        nodes.extend(md_inline(line[i+3:]))
        return nodes
    nodes.append(CodeNode(text.getvalue()))
    return nodes


if __name__ == '__main__':
    assert markdown('abcdefg') == '<p>abcdefg</p>'
    assert markdown('*ab*cdefg') == '<p><strong>ab</strong>cdefg</p>'
    assert markdown('*ab\*cdefg') == '<p><strong>ab*cdefg</strong></p>'
    assert markdown('\*ab*cdefg') == '<p>*ab<strong>cdefg</strong></p>'
    assert markdown('\*ab\*cdefg') == '<p>*ab*cdefg</p>'

    assert markdown('```abc```') == '<p><code>abc</code></p>'
    assert markdown('\```abc```') == '<p>```abc<code></code></p>'

    assert markdown('[]') == '<p><a href="" target="_blank"></a></p>'
    assert markdown('[abc]') == '<p><a href="" target="_blank">abc</a></p>'
    assert markdown('[abc](def') == '<p><a href="def" target="_blank">abc</a></p>'
    assert markdown('[abc](def)') == '<p><a href="def" target="_blank">abc</a></p>'
    assert markdown('[abc] (def)') == '<p><a href="" target="_blank">abc</a> (def)</p>'
    assert markdown('uwv[abc](def)') == '<p>uwv<a href="def" target="_blank">abc</a></p>'
    assert markdown('uwv[abc](def)mnp') == '<p>uwv<a href="def" target="_blank">abc</a>mnp</p>'

    assert markdown('abcd*efg*hij```klm```nopq[rst](uvw)xyz') == '<p>abcd<strong>efg</strong>hij<code>klm</code>nopq<a href="uvw" target="_blank">rst</a>xyz</p>'

    assert markdown('') == '<br/>'
    assert markdown('#hello') == '<h1>hello</h1>'
    assert markdown('##hello') == '<h2>hello</h2>'
    assert markdown('###hello') == '<h3>hello</h3>'
    assert markdown('####hello') == '<h4>hello</h4>'
    assert markdown('#####hello') == '<h5>hello</h5>'
    assert markdown('######hello') == '<h6>hello</h6>'

    assert markdown('```\nhello\nworld\n```') == '<pre><code>hello\nworld</code></pre>'
    assert markdown('```\nhello\nworld```') == '<pre><code>hello\nworld```</code></pre>'

    assert markdown('![abc](def)') == '<img src="def" alt="abc"/>'
    assert markdown('![abc](def') == '<img src="def" alt="abc"/>'
    assert markdown('![abc') == '<img src="" alt="abc"/>'
    assert markdown('![abc] def') == '<img src="" alt="abc"/>'

    assert markdown('* hello\n* world\n') == '<ul><li>hello</li><li>world</li></ul>'
    assert markdown('+ hello\n+ world\n') == '<ul><li>hello</li><li>world</li></ul>'
    assert markdown('- hello\n- world\n') == '<ul><li>hello</li><li>world</li></ul>'
    assert markdown('* hello\n* world\n* universe') == '<ul><li>hello</li><li>world</li><li>universe</li></ul>'
    assert markdown('1. hello\n2. world\n') == '<ol><li>hello</li><li>world</li></ol>'
    assert markdown('1. hello\n2. world\n2. universe') == '<ol><li>hello</li><li>world</li><li>universe</li></ol>'

    assert markdown('> hello') == '<blockquote>hello</blockquote>'
    assert markdown('> hello \n> world') == '<blockquote>hello</blockquote><blockquote>world</blockquote>'
