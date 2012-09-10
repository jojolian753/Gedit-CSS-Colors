#This program is free software: you can redistribute it and/or modify
#it under the terms of the GNU General Public License as published by
#the Free Software Foundation, either version 3 of the License, or
#(at your option) any later version.

#This program is distributed in the hope that it will be useful,
#but WITHOUT ANY WARRANTY; without even the implied warranty of
#MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#GNU General Public License for more details.

#You should have received a copy of the GNU General Public License
#along with this program.  If not, see <http://www.gnu.org/licenses/>.

import re

from gi.repository import GObject, Gedit

from colors import colors

Colors_Hex_RE = r"#[0-9A-Fa-f]{3}\b|#[0-9A-Fa-f]{6}\b|"


class CSSColorsPlugin(GObject.Object, Gedit.ViewActivatable):

    __gtype_name__ = "CSSColorsPlugin"

    view = GObject.property(type=Gedit.View)

    def __init__(self):
        super(CSSColorsPlugin, self).__init__()

    def do_activate(self):
        all_colors_re = Colors_Hex_RE

        all_colors_re += r"|".join(colors.keys())
        self.__colors_re = re.compile(all_colors_re)

        self.doc = self.view.get_buffer()

        # Connect signals to corresponding callbacks
        self.edit_handler = \
            self.view.connect(
                'notify::editable',
                self.do_language_notify
            )

        self.lang_handler = \
            self.doc.connect(
                'notify::language',
                self.do_language_notify
            )

    def do_deactivate(self):
#        if self.lang_handler:
#            self.view.disconnect(self.lang_handler)
        pass


    def do_document_changed(self, view):
        print("CSSColors: document changed")
        self.on_update_active(self.doc)

    def do_language_notify(self, view, pspec):
        print("CSSColors: language changed")

        if self.__is_css_doc():
            print("notify: document is css and is editable")
            self.update_handler = \
                self.doc.connect(
                    "changed",
                    self.do_document_changed
                )
            self.__colorify(self.doc)
        elif self.lang_handler:
                self.view.disconnect(self.lang_handler)

    # -------------------------------------------------------------------------

    def __is_css_doc(self):
        """
        Tests whether the document's language is CSS
        
        :returns: True if document is CSS, False otherwise
        """
        return self.doc.get_mime_type() == "text/css"

    def __add_tag_if_not_exists(self, tag):
        print("adding tag if it doesn't exist")

        if self.doc.get_tag_table().lookup(tag) == None:
            self.doc.create_tag(tag, background=tag)

    def __colorify(self, doc):
        print("colorifying")

        astart, anend = doc.get_bounds()
        self.__colorify_range(doc, astart, anend)

    def __colorify_range(self, doc, i_start, i_end):
        print("colorifying range")

        txt = doc.get_text(i_start, i_end, False)
        print("text is {0}".format(txt))
        for m in self.__colors_re.finditer(txt):
            print("m is {0}".format(m))
            start = doc.get_iter_at_offset(
                i_start.get_offset() + m.start()
            )

            end = self.doc.get_iter_at_offset(
                i_start.get_offset() + m.end()
            )

            print("m.group(0) is {0}".format(m.group(0)))
            self.__add_tag_if_not_exists(m.group(0))
            self.doc.apply_tag_by_name(m.group(0), start, end)

    # -------------------------------------------------------------------------

    def on_update_active(self, doc):
        print("updating active")

        rmtags = lambda tag, _: doc.remove_tag(tag, start, end)

        end = doc.get_iter_at_mark(doc.get_insert())
        end.forward_to_line_end()

        start = doc.get_iter_at_line(end.get_line())

        doc.get_tag_table().foreach(rmtags, None)

        self.__colorify_range(doc, start, end)
