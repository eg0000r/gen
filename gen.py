# Script by eg0000r
# 5/6/20
# Usage: run this file in your shell. First argument - *.xml file, second argument - output directory
# Dependencies: lxml
# Components: gen_res/handler_imports.txt, gen_res/imports.txt, gen_res/View.java

from lxml import etree
import sys
import os
from data import *

###
imports = imports_dot_txt
###


class View:
    handler_text = 'text'
    handler_custom = 'custom'
    indent = '    '

    def __init__(self, name, handler_type, handler_content):
        self.name = name
        self.handler_type = handler_type
        self.handler_content = handler_content
        self.children = []

    def add_child(self, child):
        self.children.append(child)

    def generate_code(self, root_view_name, output_dir):
        _file = open(output_dir + '/' + self.name + '.java', 'w')
        _file.write(self.get_class(root_view_name))
        _file.close()
        for child in self.children:
            self.recursive_generation(root_view_name, child, output_dir)

    def recursive_generation(self, root_view_name, child, output_dir):
        _file = open(output_dir + '/' + child.name + '.java', 'w')
        _file.write(child.get_class(root_view_name))
        _file.close()
        for grand in child.children:
            self.recursive_generation(root_view_name, grand, output_dir)

    # DEBUG
    def to_stdout(self):
        print('name: ' + self.name + ', type: ' + self.handler_type + ', content: ' + self.handler_content)
        for child in self.children:
            self.recursive_printing(child)

    def recursive_printing(self, child):
        print('name: ' + child.name + ', type: ' + child.handler_type + ', content: ' + child.handler_content)
        for grand in child.children:
            self.recursive_printing(grand)
    # END_DEBUG

    def get_class(self, root_view_name):
        body = ''
        body += imports
        body += '\n'
        body += 'public class ' + self.name + ' extends View {\n'
        body += self.indent + 'public ' + self.name + '() {\n'
        body += 2 * self.indent + 'super(\"' + self.name + '\");\n'
        body += self.indent + '}\n\n'
        body += self.indent + 'private ReplyKeyboardMarkup markup = ' + self.get_markup(root_view_name) + '\n\n'
        body += self.indent + '@Override\n'
        body += self.indent + 'public String handle(TelegramBot bot, Update update) {\n'
        for child in self.children:
            body += 2 * self.indent + 'if (update.message().text().equals(\"' + child.name + '\")) {\n'
            body += 3 * self.indent + 'return \"' + child.name + '\";\n'
            body += 2 * self.indent + '}\n\n'
        if self.name != root_view_name:
            body += 2 * self.indent + 'if (update.message().text().equals(\"' + root_view_name + '\")) {\n'
            body += 3 * self.indent + 'return \"' + root_view_name + '\";\n'
            body += 2 * self.indent + '}\n\n'
        if self.handler_type == self.handler_text:
            body += 2 * self.indent + 'bot.execute(new SendMessage(update.message().chat().id(), \"'\
                    + self.handler_content + '\").replyMarkup(markup).resizeKeyboard(true);\n'
        else:
            body += self.handler_content + '\n'
        body += 2 * self.indent + 'return \"' + self.name + '\";\n'
        body += self.indent + '}\n'
        body += '}\n'
        return body

    def get_markup(self, root_view_name):
        markup = 'new ReplyKeyboardMarkup(\n'
        for child in self.children:
            markup += 2 * self.indent + 'new String[]{new InlineKeyboardButton(\"' + child.name + '\").text()},\n'
        if self.name != root_view_name:
            markup += 2 * self.indent + 'new String[]{new InlineKeyboardButton(\"' + root_view_name + '\").text()}\n'
        else:
            markup = markup[0: -2] + '\n'
        markup += self.indent + ');'
        return markup


class Generate:
    indent = '    '

    def __init__(self, xml, output_dir):
        self.names_flat = []
        root = etree.fromstring(xml)
        root_view = root[0]
        instance = self.recursive_parse(root_view, self.get_instance(root_view))
        # DEBUG
        instance.to_stdout()
        instance.generate_code(root_view.get('name'), output_dir)
        self.copy_resources(output_dir)
        self.generate_handler(output_dir)
        # END_DEBUG

    def get_instance(self, element):
        handler_content = ''
        self.names_flat.append(element.get('name'))
        for child in element:
            if child.tag == 'handler':
                handler_content = child.text
        return View(element.get('name'), element.get('handlerType'), handler_content)

    def recursive_parse(self, element, instance):
        for child in element:
            if child.tag == 'view':
                instance.add_child(self.get_instance(child))
            if len(child) > 1:
                self.recursive_parse(child, instance)
        return instance

    def copy_resources(self, output_dir):
        ###
        view_base_class = view_dot_java
        ###
        _file = open(output_dir + '/View.java', 'w')
        _file.write(view_base_class)
        _file.close()

    def generate_handler(self, output_dir):
        body = 'package ' + output_dir + ';\n\n'
        ###
        body += handler_imports_dot_txt
        ###
        for name in self.names_flat:
            body += 'import ' + output_dir + '.' + name + ';\n'
        body += '\n'
        body += 'public class Storyboard {\n'
        body += self.indent + 'public static void handle(TelegramBot bot, Update update) {\n'
        body += 2 * self.indent + 'Map<String, View> views = new HashMap<String, View>() {\n'
        for name in self.names_flat:
            body += 3 * self.indent + 'put(new ' + name + '().getIdentifier(), ' + 'new ' + name + '());\n'
        body += 2 * self.indent + '};\n'
        body += 2 * self.indent + 'long chatId = update.message().chat.id();\n'
        body += 2 * self.indent + 'try {\n'
        body += 3 * self.indent + 'String prevStory = State.getState(chatId).getNextStoryBoard();\n'
        body += 3 * self.indent + 'String nextStory = views.get(prevStory).handle(bot, update);\n'
        body += 3 * self.indent + 'State.nextStoryBoard(chatId, nextStory);\n'
        body += 3 * self.indent + 'if (!views.containsKey(nextStory)) {\n'
        body += 4 * self.indent + 'return;\n'
        body += 3 * self.indent + '}\n'
        body += 3 * self.indent + 'if (!prevStory.equals(nextStory) {\n'
        body += 4 * self.indent + 'State.nextStoryBoard(chatId, views.get(State.getState(chatId).getNextStoryBoard())' \
                                  '.updateReceived(bot, update));\n'
        body += 3 * self.indent + '}\n'
        body += 2 * self.indent + '} catch (Exception e) {\n'
        body += 3 * self.indent + 'e.printStackTrace()\n'
        body += 2 * self.indent + '}\n'
        body += self.indent + '}\n'
        body += '}\n'
        _file = open(output_dir + '/Storyboard.java', 'w')
        _file.write(body)
        _file.close()


def invoke_generator(xml, output_dir):
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    _file = open(xml, 'r')
    content = _file.read()
    _file.close()
    _ = Generate(content, output_dir)


invoke_generator(sys.argv[1], sys.argv[2])
