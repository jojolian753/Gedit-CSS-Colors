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

import gedit
import re

Colors_Hex_RE = "(#[0-9a-fA-F]{6})|(#[0-9a-fA-F]{3})"
Colors = [
    "marron",
    "red",
    "yellow",
    "olive",
    "purple",
    "fuchsia",
    "white",
    "lime",
    "green",
    "navy",
    "blue",
    "aqua",
    "teal"
    "black",
    "silver",
    "grey",
    "orange",
    "black"
]

class CSSColorsPlugin(gedit.Plugin):

    def activate(self, window):
        all_colors_re = Colors_Hex_RE
        for c in Colors : 
            all_colors_re += "|" + c
        self.__colors_re = re.compile(all_colors_re)
        window.connect("tab-added", self.__tab_added_cb)

    def deactivate(self, window):
        pass

    def update_ui(self, window):
        pass
            
    def __tab_added_cb(self, w, tab) :
        tab.get_document().connect("loaded", self.__doc_loaded)

    def __add_tag_if_not_exists(self, doc, tag) :
        if doc.get_tag_table().lookup(tag) == None :
            doc.create_tag(tag, background=tag)


    def __doc_loaded(self, doc, whatever) :
        if doc.get_mime_type() == "text/css" :
            self.__colorify(doc, doc.get_start_iter(), doc.get_end_iter())
            doc.connect("changed", self.__doc_changed)

    def __doc_changed(self, doc) :
        fun_rmtag = lambda tag, _ : doc.remove_tag(tag, start, end)
        end = doc.get_iter_at_mark(doc.get_insert()).forward_to_line_end()
        start = doc.get_iter_at_line(end.get_line())
        doc.get_tag_table().foreach(fun_rmtag)
        self.__colorify(doc, start, end)

    def __colorify(self, doc, i_start, i_end) :
        txt = doc.get_text(i_start, i_end)
        for m in self.__colors_re.finditer(txt):
            start = doc.get_iter_at_offset(i_start.get_offset() + m.start())
            end = doc.get_iter_at_offset(i_start.get_offset() + m.end())
            self.__add_tag_if_not_exists(doc, m.group(0))
            doc.apply_tag_by_name(m.group(0),start, end)

