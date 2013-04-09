#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import argparse
import re
from cStringIO import StringIO

from lxml import html, etree

from pygments.formatters import HtmlFormatter
from pygments.lexers import DjangoLexer
from pygments import highlight
from pygments.styles import get_style_by_name


CLOSE_TAG = ('</', '!!!CLOSETAG!!!')
SELFCLOSE_TAG = ('/>', '!!!SELFCLOSETAG!!!')
OPEN_TAG = ('<', '!!!OPENTAG!!!')
END_TAG = ('>', '!!!CLOSE_TAG!!!')


class Block(object):

    def __init__(self, name, comment='', default_value='', blocks=[]):
        self._name = name
        self._comment = comment
        self._default_value = default_value
        self._blocks = blocks or []

    @property
    def name(self):
        return self._name

    @property
    def comment(self):
        return self._comment

    @property
    def blocks(self):
        return self._blocks

    @property
    def default_value(self):
        return self._default_value

    @property
    def documentation(self):
        pass

    def __str__(self):
        blocks_text = "\t\t".join(re.subn('\n', '\n\t', str(b))[0] for b in self.blocks)

        return """
            Name: %s,
            Comment: %s
            Default Value: %s
            Blocks: %s
        """ % (self.name, self.comment, self.default_value, blocks_text or 'NO SUB BLOCKS FOUND!!')


def unescape_comment(comment):
    return unescape_tags(re.subn(r'</?comment>', '', comment)[0])


def escape_tags(template_content):
    new_content = str(template_content)
    new_content = re.subn(CLOSE_TAG[0], CLOSE_TAG[1], new_content)[0]
    new_content = re.subn(SELFCLOSE_TAG[0], SELFCLOSE_TAG[1], new_content)[0]
    new_content = re.subn(OPEN_TAG[0], OPEN_TAG[1], new_content)[0]
    new_content = re.subn(END_TAG[0], END_TAG[1], new_content)[0]

    return new_content.strip()


def unescape_default_value(default_value):
    new_content = str(default_value).strip()
    new_content = re.sub(r'^<block[^>]*/?>', '', new_content)
    new_content = re.sub(r'</block>$', '', new_content)
    new_content = re.subn(r'<block[^>]*>.*?</block>', '', new_content, 0, re.DOTALL)[0]
    new_content = re.subn(r'<comment>.*?</comment>', '', new_content, 0, re.DOTALL)[0]
    new_content = re.subn(r'\n+', '\n', new_content, 0, re.DOTALL)[0]

    return unescape_tags(new_content) or None


def unescape_tags(template_content):
    new_content = str(template_content)
    new_content = re.subn(CLOSE_TAG[1], CLOSE_TAG[0], new_content)[0]
    new_content = re.subn(SELFCLOSE_TAG[1], SELFCLOSE_TAG[0], new_content)[0]
    new_content = re.subn(OPEN_TAG[1], OPEN_TAG[0], new_content)[0]
    new_content = re.subn(END_TAG[1], END_TAG[0], new_content)[0]

    return new_content.strip()


def translate_template_content(template_content):
    new_content = escape_tags(template_content)

    new_content = re.subn('\{%\s*block\s*(\w+)[^%]*%\}', '<block data-name="\g<1>">', new_content)[0]
    new_content = re.subn('\{%\s*endblock\s*[^%]*%\}', '</block>', new_content)[0]

    new_content = re.subn('\{#', '<comment>', new_content)[0]
    new_content = re.subn('#\}', '</comment>', new_content)[0]

    return "<main>%s</main>" % new_content


def build_blocks_from_xml_el(block_elements):
    blocks = []

    for block_el in block_elements:
        comment = ''
        comment_el = block_el.find('comment')

        if comment_el is not None:
            comment = unescape_comment(etree.tostring(comment_el, with_tail=False))

        block = Block(
            name=block_el.attrib.get('data-name'),
            default_value=unescape_default_value(etree.tostring(block_el, with_tail=False)),
            comment=comment,
            blocks=build_blocks_from_xml_el(block_el.findall('block'))
        )

        blocks.append(block)

    return blocks


def build_template_tags(blocks):
    content = StringIO()
    block_template = '''
    {%% block %(name)s %%}
        %(comment)s

        Default:
            %(default_value)s

        %(blocks)s
    {%% endblock %(name)s %%}

    '''

    for block in blocks:
        subblocks = re.subn("\n", "\n\t", build_template_tags(block.blocks))

        if subblocks:
            subblocks = subblocks[0]

        content.write(block_template % {
            'name': block.name,
            'comment': block.comment,
            'default_value': re.subn("\n", "\n\t", str(block.default_value))[0],
            'blocks': subblocks,
        })

    return content.getvalue()


def build_code(template_content):
    new_content = translate_template_content(template_content)
    doc_root = html.fromstring(new_content)
    blocks = build_blocks_from_xml_el(doc_root.findall('block'))

    return build_template_tags(blocks)


def main(args):
    with open(args.file_path) as f:
        code = build_code(f.read())

    formatter = HtmlFormatter(style=get_style_by_name(args.pygments_style))
    lexer = DjangoLexer(tabsize=4)
    css = formatter.get_style_defs()

    docs = highlight(code, lexer, formatter)
    docs += "<style>%s</style>" % css

    if args.output:
        with open(args.output, 'w') as f:
            f.write(docs)
    else:
        sys.stdout.write(docs)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("file_path")
    parser.add_argument("--output")
    parser.add_argument("--pygments-style", default="colorful")

    args = parser.parse_args()

    main(args)

