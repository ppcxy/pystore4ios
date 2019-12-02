# !/usr/bin/python3
# -*- coding: utf-8 -*-
from objc_util import *
import time
import ui, requests, json, time, pickle
from os import path, makedirs, remove

app = UIApplication.sharedApplication()

BOOK_DATA_DIR = path.expanduser('~/Documents/.pystore/eBook')


def bookcase_data_write(data):
    # print(data)
    data_path = path.join(BOOK_DATA_DIR, '.cache/index.data')
    with open(data_path, 'wb') as file:
        pickle.dump(data, file)


if app.zssq != None:
    try:
        bookcase_data = app.zssq.bookcase_data
        app.zssq.close()
        app.zssq = None
        time.sleep(3)
    except:
        None

from random import choice
from math import radians
from dialogs import hud_alert, share_url

SYSTEM_STYLE_DATA = {
    '追书红': '#992300',
    '青草绿': '#1c7b37',
    '少女粉': '#b43e82',
    '水鸭青': '#008080',
    '摩卡棕': '#605300'
}
READER_STYLE_DATA = {
    '羊皮棕': '#a28a6a',
    '豆沙绿': '#c7edcc',
    '杏仁黄': '#ccc8ad',
    '玫瑰棕': '#a27b7b',
    '白银灰': '#C0C0C0'
}

requests.adapters.DEFAULT_RETRIES = 5
r = requests.Session()
head = {
    "User-Agent": "YouShaQi/2.25.1 (iPhone; iOS 10.3.1; Scale/2.00)",
    "X-User-Agent": "YouShaQi/2.25.1 (iPhone; iOS 10.3.1; Scale/2.00)"
}
r.headers.update(head)


def system_config(mode='read'):
    global SYSTEM_STYLE, READER_STYLE, INFO_STYLE
    config_path = path.join(BOOK_DATA_DIR, '.cache/config.data')
    if mode == 'read' and path.isfile(config_path):
        with open(config_path, 'rb') as file:
            data = pickle.load(file)
            SYSTEM_STYLE = data['system_style']
            READER_STYLE = data['reader_style']
            INFO_STYLE = data['info_style']
    elif mode == 'read' and not path.isfile(config_path):
        makedirs(path.join(BOOK_DATA_DIR, '.cache'))
        with open(config_path, 'wb') as file:
            data = {}
            data['system_style'] = SYSTEM_STYLE = '#008080'
            data['reader_style'] = READER_STYLE = '#c5c1a7'
            data['info_style'] = INFO_STYLE = '#fdf6e5'
            pickle.dump(data, file)
    elif mode == 'write':
        data = {}
        data['system_style'] = SYSTEM_STYLE
        data['reader_style'] = READER_STYLE
        data['info_style'] = INFO_STYLE
        with open(config_path, 'wb') as file:
            pickle.dump(data, file)


def api(url):
    root_view.network_status.start()
    try:
        return r.get(url, timeout=12).text
    except:
        hud_alert('网络连接失败', 'error', 1)
        return False
    finally:
        root_view.network_status.stop()


def cover_url_encode(url):
    decode_url = requests.utils.unquote(url)
    encode_url = requests.utils.quote(decode_url)
    img_url = 'http://statics.zhuishushenqi.com{}'.format(encode_url)
    return img_url


def search_books(keywords):
    global booksearch_data, booksearch_list
    url = 'http://api.zhuishushenqi.com/book/fuzzy-search?query={}&start=0&limit=100'.format(
        keywords)
    res = api(url) or exit()
    books = json.loads(res)['books']
    booksearch_data = {book['_id']: book for book in books}
    booksearch_list = [book['_id'] for book in books]


def get_book_list(mode, num):
    urls = {
        'week':
            'https://api.zhuishushenqi.com/book-list?sort=collectorCount&duration=last-seven-days&start=',
        'new':
            'https://api.zhuishushenqi.com/book-list?sort=created&duration=all&start=',
        'top':
            'https://api.zhuishushenqi.com/book-list?sort=collectorCount&duration=all&start='
    }
    url = urls[mode] + str(num)
    res = api(url) or exit()
    res_data = json.loads(res)['bookLists']
    book_list = [data['_id'] for data in res_data]
    book_data = {data['_id']: data for data in res_data}
    global book_lists_list, book_lists_data
    book_lists_list += book_list
    book_lists_data = dict(book_lists_data, **book_data)
    booklistview.list.reload_data()


def get_booklist_books(booklist_id):
    url = 'https://api.zhuishushenqi.com/book-list/' + booklist_id
    res = api(url) or exit()
    global booklist_data, booklist_books_list, booklist_books_data
    booklist_data = json.loads(res)['bookList']
    booklist_books_list = [
        item['book']['_id'] for item in booklist_data['books']
    ]
    booklist_books_data = {
        item['book']['_id']: item['book']
        for item in booklist_data['books']
    }


@ui.in_background
def get_top_book():
    global booktop_list, booktop_data, booktop_name
    url1 = 'http://api.zhuishushenqi.com/ranking/gender'
    res1 = api(url1) or exit()
    top_id = choice(json.loads(res1)['male'])['_id']
    booktop_name = [
        top['title'] for top in json.loads(res1)['male']
        if top['_id'] == top_id
    ][0]
    url2 = 'http://api.zhuishushenqi.com/ranking/{}'.format(top_id)
    res2 = api(url2) or exit()
    res_books = json.loads(res2)['ranking']['books']
    booktop_list = [book['_id'] for book in res_books]
    booktop_data = {book['_id']: book for book in res_books}
    searchview_refresh()


def get_book_sources(book_id):
    global sources_list, sources_data
    url = 'http://api.zhuishushenqi.com/toc?view=summary&book={}'.format(
        book_id)
    res = api(url) or exit()
    sources = json.loads(res)
    sources_data = {source['name']: source for source in sources}
    sources_list = [source for source in sources_data.keys()]
    return sources_data


def get_book_chapters(source_id):
    global chapters_list, chapters_data
    url = 'http://api.zhuishushenqi.com/toc/{}?view=chapters'.format(source_id)
    res = api(url) or exit()
    chapters = json.loads(res)['chapters']
    chapterslist = [
        '{}#{}'.format(idx, val['title']) for idx, val in enumerate(chapters)
    ]
    chapters_data = {idx: val for idx, val in enumerate(chapters)}
    chapters_list = chapterslist[::-1]


def get_chapter_content(chapter_link):
    chapter_url = requests.utils.quote(chapter_link)
    url = 'http://chapterup01.zhuishushenqi.com/chapter/{}?t={}'.format(
        chapter_url, int(time.time() + 7200))
    res = api(url) or exit()
    try:
        chapter_content = json.loads(res)['chapter']['body']
        return chapter_content
    except KeyError:
        return '<none>正文无内容</none>'


def bookcase_data_update(book_id, mode='add'):
    data_path = path.join(BOOK_DATA_DIR, '.cache/index.data')
    cover_path = path.join(BOOK_DATA_DIR, '.cache/{}.jpg'.format(book_id))
    if path.isfile(data_path):
        with open(data_path, 'rb') as file:
            data = pickle.load(file)
    else:
        data = {}
    if mode == 'del':

        del data[book_id]
        remove(cover_path)
    else:
        url = 'http://api.zhuishushenqi.com/book/{}'.format(book_id)
        res = api(url) or exit()
        res_data = json.loads(res)
        data[res_data['_id']] = res_data
        img_url = 'http://statics.zhuishushenqi.com{cover}'.format(**res_data)
        with open(cover_path, 'wb') as img:
            img.write(r.get(img_url).content)
    bookcase_data_write(data)
    bookcase_data_load()
    root_view.bookcase.reload_data()


def bookcase_data_load():
    global bookcase_list, bookcase_data
    data_path = path.join(BOOK_DATA_DIR, '.cache/index.data')
    if path.isfile(data_path):
        with open(data_path, 'rb') as file:
            data = pickle.load(file)
        bookcase_data = data
        bookcase_list = [id for id in bookcase_data.keys()]
        bookcase_list.sort()
    else:
        bookcase_list = []
        bookcase_data = {}


def searchview_refresh():
    if not searchview.keywords.text:
        searchview.table.reload_data()


def string_split(string):
    str_list = [
        '&#12288;&#12288;{}<br/>'.format(str) for str in string.split('\n')
    ]
    return ''.join(str_list)


def theme(mode='bookcase'):
    global system_setting, style_data, style_list, style_mode
    if mode == 'reader':
        style_data = READER_STYLE_DATA
        style_list = [style for style in style_data.keys()]
        style_mode = 'reader_theme'
        system_setting = SystemSettingsView()
        readerview.add_subview(system_setting)
    else:
        style_data = SYSTEM_STYLE_DATA
        style_list = [style for style in style_data.keys()]
        style_mode = 'system_theme'
        system_setting = SystemSettingsView()
        root_view.add_subview(system_setting)


def auto_open_book(book_id):
    global readerview
    if 'chapter_log' in bookcase_data[book_id]:
        chapter_title = bookcase_data[book_id]['chapter_log']
        readerview = ReaderView(chapter_title)
        readerview.present(hide_title_bar=True)


@ui.in_background
def bookcase_refresh():
    if not bookcase_data: exit()
    before_data = bookcase_data
    ids = ','.join(bookcase_list)
    url = 'http://api.zhuishushenqi.com/book?view=updated&id={}'.format(ids)
    res = api(url) or exit()
    after_data = json.loads(res)
    after_data = {book['_id']: book for book in after_data}
    for id in bookcase_list:
        befor_time = before_data[id]['updated'].split('.')[0].replace('T', ' ')
        after_time = after_data[id]['updated'].split('.')[0].replace('T', ' ')
        befor_time = time.mktime(
            time.strptime(befor_time, '%Y-%m-%d %H:%M:%S'))
        after_time = time.mktime(
            time.strptime(after_time, '%Y-%m-%d %H:%M:%S'))
        now_time = time.time()
        t = now_time - after_time
        if after_time > befor_time:
            bookcase_data[id]['lastChapter'] = after_data[id]['lastChapter']
            bookcase_data[id]['updated'] = after_data[id]['updated']
            global update_data
            update_data = {}
            if 60 * 60 > t > 60:
                update_info = '{:.0f}分钟前更新'.format(t / 60)
                update_data[id] = update_info
            elif 60 * 60 * 24 > t > 60 * 60:
                update_info = '{:.0f}小时前更新'.format(t / 60 / 60)
                update_data[id] = update_info
            elif t > 60 * 60 * 24:
                update_info = '{:.0f}天前更新'.format(t / 60 / 60 / 24)
                update_data[id] = update_info
            bookcase_data[id]['update_info'] = update_info
    if 'update_data' in globals():
        bookcase_data_write(bookcase_data)
        root_view.bookcase.reload_data()


def button1_tapped(sender):
    global searchview, booktop_list, booktop_data
    if root_view.bookcase.on_screen or 'searchview' not in globals():
        booktop_list = []
        booktop_data = {}
        searchview = SearchView()
        get_top_book()
    elif not searchview.table.on_screen:
        searchview = SearchView()


@ui.in_background
def get_booklist(mode, num):
    get_book_list(mode, num)


def button2_tapped(sender):
    global booklistview, book_list_mode, book_lists_list, book_lists_data
    if root_view.bookcase.on_screen or 'booklistview' not in globals():
        book_list_mode = 'week'
        book_lists_list = []
        book_lists_data = {}
        booklistview = BookListView()
        get_booklist(book_list_mode, 0)
    elif not booklistview.list.on_screen:
        booklistview = BookListView()


@ui.in_background
def button3_tapped(sender):
    while True:
        if root_view.bookcase.on_screen == True:
            break
        root_view.view.pop_view(False)


def button4_tapped(sender):
    try:
        root_view.remove_subview(root_view['system_setting'])
    except:
        theme()


def button5_tapped(sender):
    root_view.close()


class SearchViewButton(object):
    def __init__(self, mode, row):
        self.mode = mode
        self.row = row
        if self.mode == 'search':
            self.book_id = booksearch_list[self.row]
        elif self.mode == 'top':
            self.book_id = booktop_list[self.row]
        else:
            self.book_id = booklist_books_list[self.row]

    def detail_tapped(self, sender):
        BookDetailView(self.book_id, self.mode)

    def add_tapped(self, sender):
        bookcase_data_update(self.book_id)
        sender.enabled = False


class KeyWordsDelegate(object):
    def textfield_did_end_editing(self, textfield):
        searchview.search_button_tapped(searchview.done_button)

    def textfield_did_change(self, textfield):
        if not textfield.text:
            searchview.done_button.image = ui.Image.named(
                'iow:ios7_refresh_32')
            searchview.done_button.title = '刷新'
            searchview.table.data_source = SearchDataSource('top')
            searchview.table.delegate = TableViewDelegate('top')
            searchview.table.reload_data()
        else:
            searchview.done_button.image = ui.Image.named(
                'iob:ios7_search_strong_32')
            searchview.done_button.title = '搜索'


class SystemSettingsView(ui.View):
    def __init__(self):
        self.frame = (87.5, 180, 200, 290)
        self.corner_radius = 6
        self.name = 'system_setting'
        self.border_width = 3

        self.button1 = ui.Button()
        self.button1.name = 'system_theme'
        self.button1.frame = (0, 0, 100, 40)
        self.button1.font = ('<System-Bold>', 18)
        self.button1.bg_color = '#9fa38a'
        self.button1.tint_color = '#114f5a'
        self.button1.title = '系统主题'
        self.button1.action = self.button_tapped

        self.button2 = ui.Button()
        self.button2.name = 'reader_theme'
        self.button2.frame = (100, 0, 100, 40)
        self.button2.font = ('<System-Bold>', 18)
        self.button2.bg_color = self.button1.tint_color
        self.button2.tint_color = self.button1.bg_color
        self.button2.title = '阅读主题'
        self.button2.action = self.button_tapped

        self.table = ui.TableView()
        self.table.frame = (0, 40, self.width, 250)
        self.table.row_height = 50
        self.table.scroll_enabled = False
        self.table.data_source = SystemSettingsDataSource()
        self.table.delegate = SystemSettingsDelegate()

        self.add_subview(self.button1)
        self.add_subview(self.button2)
        self.add_subview(self.table)

    def draw(self):
        self.border_color = SYSTEM_STYLE

    def button_tapped(self, sender):
        global style_data, style_list, style_mode
        style_mode = sender.name
        style_data = SYSTEM_STYLE_DATA if sender.name == 'system_theme' else READER_STYLE_DATA
        style_list = [style for style in style_data.keys()]
        self.table.reload_data()


class SystemSettingsDataSource(object):
    def tableview_number_of_rows(self, tableview, section):
        return 5

    def tableview_cell_for_row(self, tableview, section, row):
        style = style_list[row]
        cell = ui.TableViewCell()
        cell.bg_color = style_data[style]
        cell.border_width = 0.3
        cell.border_color = 'white'

        cell_selected_icon = ui.ImageView()
        cell_selected_icon.image = ui.Image.named('iow:checkmark_round_24')
        cell_selected_icon.frame = (30, 15, 20, 20)

        cell_bg = ui.View()
        cell_bg.frame = (0, 0, 200, 50)
        cell_bg.bg_color = style_data[style]
        cell_bg.corner_radius = 6

        cell_title = ui.Label()
        cell_title.frame = (0, 0, 200, 50)
        cell_title.alignment = ui.ALIGN_CENTER
        cell_title.number_of_lines = 3
        cell_title.font = ('<System-Bold>', 20)
        cell_title.text_color = 'white' if style_mode == 'system_theme' else 'black'
        cell_title.text = style
        cell.content_view.add_subview(cell_bg)
        cell.content_view.add_subview(cell_title)

        if style_data[style] == SYSTEM_STYLE or style_data[style] == READER_STYLE:
            cell.content_view.add_subview(cell_selected_icon)
        return cell


class SystemSettingsDelegate(object):
    def tableview_did_select(self, tableview, section, row):
        global SYSTEM_STYLE, READER_STYLE
        item = style_list[row]
        if style_mode == 'system_theme':
            SYSTEM_STYLE = style_data[item]
        else:
            READER_STYLE = style_data[item]
        system_config(mode='write')
        system_setting.table.reload_data()
        system_setting.set_needs_display()
        root_view.set_needs_display()
        root_view.bookcase.reload_data()
        try:
            searchview.set_needs_display()
        except:
            pass
        try:
            readerview.set_needs_display()
            js = "theme({})".format(READER_STYLE)
            readerview.webview.eval_js(js)
        except:
            pass


class ReaderView(ui.View):
    def __init__(self, chapter_title, mode=None):
        self.mode = mode
        self.chapter_title = chapter_title
        self.chapter_num = int(self.chapter_title.split('#')[0])
        self.TEMPLATE = '''
		<!doctype html>
		<html>
		<head>
		<meta charset="utf-8">
		<meta name="viewport" content="width=device-width">
		<style type="text/css">
		body {
		background-color:{{STYLE}};
		font-family: <System>;
		margin:0px;
		margin-left:15px;
		margin-right:15px;
		padding:0px;
		border:0px; }
		</style>
		</head>
		<body>
		<div id="text" style="font-size:22px;line-height:35px;letter-spacing:2px;text-indent:2em;">
		{{chapter}}<br/>{{CONTENT}}
		</div>
		</body>
		<script type="text/javascript">
		var PageH = document.body.scrollHeight;
		var ClientH = document.documentElement.clientHeight;
		var ScrollH = 630;
		function seth()
		{
			if (PageH%ScrollH > 0)
			{
				FillH = ScrollH - PageH%ScrollH;
				NewH = PageH + FillH;
				document.getElementById("text").style.height = NewH + "px";
			}
		}
		function auto()
		{
			scrollTo(0,{{page}}*ScrollH)
		}
		function theme(color)
		{
			document.body.style.backgroundColor = color;
		}
		seth();
		auto();
		</script>
		</html>
		'''

        self.top_lable = ui.Label()
        self.top_lable.frame = (0, 0, w, 25)
        self.bottom_lable = ui.Label()
        self.bottom_lable.frame = (0, h - 10, w, 10)

        self.webview = ui.WebView()
        self.webview.frame = (0, 5, w, h - 10)
        self.webview.touch_enabled = False
        self.add_subview(self.webview)
        self.add_subview(self.top_lable)
        self.add_subview(self.bottom_lable)

    def draw(self):
        self.bg_color = self.top_lable.bg_color = self.bottom_lable.bg_color = self.webview.bg_color = READER_STYLE
        if self.mode == 'source':
            chapters_count = len(chapters_data) - 1
            self.chapter_title = '{}#{}'.format(
                chapters_count, chapters_data[chapters_count]['title'])
            self.chapter_num = int(self.chapter_title.split('#')[0])
            self.mode = None
        else:
            self.chapter_title = '{}#{}'.format(
                self.chapter_num, chapters_data[self.chapter_num]['title'])
        self.link = chapters_data[self.chapter_num]['link']
        self.chapter_content = get_chapter_content(self.link)
        self.txt = string_split(self.chapter_content)
        if chapterview.mode == 'local' and 'page_log' in bookcase_data[chapterview.
                book_id] and bookcase_data[chapterview.
                book_id]['chapter_log'] == self.chapter_title:
            self.page = bookcase_data[chapterview.book_id]['page_log']
        else:
            self.page = 0
        self.html = self.TEMPLATE.replace('{{CONTENT}}', self.txt).replace(
            '{{STYLE}}',
            READER_STYLE).replace('{{chapter}}',
                                  self.chapter_title.split('#')[1]).replace(
            '{{page}}', str(self.page))
        self.webview.load_html(self.html)

    def will_close(self):
        if chapterview.mode == 'local':
            book_id = chapterview.book_id
            bookcase_data[book_id]['chapter_log'] = self.chapter_title
            bookcase_data[book_id]['source_log'] = chapterview.source_name
            try:
                bookcase_data[chapterview.book_id]['page_log'] = self.page
            except:
                pass

    def touch_began(self, touch):
        if self['sourceview']:
            self.remove_subview(self['sourceview'])
            exit()

        if self['system_setting']:
            self.remove_subview(system_setting)
            exit()
        x = touch.location[0]
        y = touch.location[1]
        if x < w / 3 and y > h * 2 / 3:
            # 下左触摸上一页
            self.webview.eval_js('scrollBy(0,-ScrollH)')
            if self.page != 0:
                self.page -= 1
        elif x > w * 2 / 3 and y > h * 2 / 3:
            # 下右触摸下一页
            self.webview.eval_js('scrollBy(0,ScrollH)')
            self.page += 1
        elif x < w / 3 and h / 3 < y < h * 2 / 3:
            # 中左触摸上一章
            if self.chapter_num == 0:
                self.chapter_num = len(chapters_list) - 1
            else:
                self.chapter_num -= 1
            self.set_needs_display()
        elif x > w * 2 / 3 and h / 3 < y < h * 2 / 3:
            # 中右触摸下一章
            if self.chapter_num == len(chapters_list) - 1:
                self.chapter_num = 0
            else:
                self.chapter_num += 1
            self.set_needs_display()

        elif x < w / 3 and y < h / 3:
            # 上左触摸换源
            global booksourceview
            booksourceview = BookSourceView('reader')
            self.add_subview(booksourceview)
        elif x > w * 2 / 3 and y < h / 3:
            # 上右触摸关闭阅读界面
            self.close()
        elif w / 3 < x < w * 2 / 3 and h / 5 * 2 < y < h / 5 * 3:
            # 中间触摸弹出主题设置
            theme(mode='reader')

    def touch_ended(self, touch):
        x = touch.location[0]
        y = touch.location[1]
        if w / 3 * 2 > x > w / 3 and y > h / 3 * 2:
            global touch_time
            if 'touch_time' not in globals():
                touch_time = [touch.timestamp]
            else:
                touch_time.append(touch.timestamp)
            if 'touch_time' in globals() and len(
                    touch_time) == 2 and touch_time[1] - touch_time[0] <= 0.2:
                self.close()
                del touch_time[0]
            elif 'touch_time' in globals() and len(
                    touch_time) == 2 and touch_time[1] - touch_time[0] > 0.2:
                del touch_time[0]


class ChapterView(ui.View):
    # 生成章节显示界面
    def __init__(self, book_id, mode):
        self.book_id = book_id
        self.mode = mode
        if self.mode == 'local':
            self.book_data = bookcase_data
        elif self.mode == 'search':
            self.book_data = booksearch_data
        elif self.mode == 'top':
            self.book_data = booktop_data
        elif self.mode == 'booklist':
            self.book_data = booklist_books_data
        try:
            self.source_name = bookcase_data[self.book_id]['source_log']
            self.source_id = get_book_sources(
                self.book_id)[self.source_name]['_id']
        except:
            get_book_sources(self.book_id)
            self.source_name = choice(sources_list)
            self.source_id = sources_data[self.source_name]['_id']
        self.chapter = ui.TableView()
        self.chapter.frame = (0, 0, w, h - 120)
        self.chapter.row_height = 50
        self.chapter.data_source = ChapterDataSource()
        self.chapter.delegate = ChapterDelegate()

        self.sort_button = ui.Button()
        self.sort_button.frame = (310, 250, 50, 50)
        self.sort_button.tint_color = '#89ffcd'
        self.sort_button.image = ui.Image.named('iow:arrow_swap_256')
        self.sort_button.transform = ui.Transform.rotation(radians(90))
        self.sort_button.action = self.sort_button_tapped

        self.name = self.book_data[self.book_id]['title']
        self.add_subview(self.chapter)
        self.add_subview(self.sort_button)
        get_book_chapters(self.source_id)
        root_view.view.push_view(self)

    def sort_button_tapped(self, sender):
        global chapters_list
        chapters_list = chapters_list[::-1]
        self.chapter.reload_data()


class ChapterDataSource(object):
    # 章节数据显示设置
    def tableview_number_of_rows(self, tableview, section):
        return len(chapters_list)

    def tableview_title_for_header(self, tableview, section):
        return chapterview.source_name

    def tableview_cell_for_row(self, tableview, section, row):
        cell = ui.TableViewCell('subtitle')
        cell.border_width = 0.22
        cell.border_color = SYSTEM_STYLE
        chapter = chapters_list[row].split('#')[1]
        cell.text_label.text = chapter
        cell.detail_text_label.text_color = '#008923'
        cell.accessory_type = 'disclosure_indicator'
        return cell


class ChapterDelegate(object):
    # 点击章节触发动作
    def tableview_did_select(self, tableview, section, row):
        chapter_title = chapters_list[row]
        global readerview
        readerview = ReaderView(chapter_title)
        readerview.present(hide_title_bar=True)

    def scrollview_did_scroll(self, scroll):
        y = scroll.content_offset[1]
        if not chapterview['sourceview'] and y < -50:
            global booksourceview
            booksourceview = BookSourceView('chapter')
            chapterview.add_subview(booksourceview)


class SearchView(ui.View):
    # 生成搜索界面
    def __init__(self):
        self.name = '小说搜索'
        self.frame = (0, 60, w, h)
        self.icon = ui.ImageView()
        self.icon.frame = (4, 3, 37, 37)
        self.icon.image = ui.Image.named('iob:ios7_search_strong_32')

        self.keywords = ui.TextField()
        self.keywords.placeholder = ' 输入书名或作者名...'
        self.keywords.text_color = 'black'
        self.keywords.border_width = 1
        self.keywords.border_color = '#26a291'
        self.keywords.corner_radius = 8
        self.keywords.frame = (5, 5, 290, 40)
        self.keywords.clear_button_mode = 'while_editing'
        self.keywords.delegate = KeyWordsDelegate()

        self.done_button = ui.Button()
        self.done_button.image = ui.Image.named('iow:ios7_refresh_32')
        self.done_button.title = '刷新'
        self.done_button.font = ('<System-Bold>', 18)
        self.done_button.frame = (300, 5, 70, 40)
        self.done_button.action = self.search_button_tapped

        self.table = ui.TableView()
        self.table.frame = (0, 50, w, h - 165)
        self.table.row_height = 80
        self.table.data_source = SearchDataSource('top')
        self.table.delegate = TableViewDelegate('top')

        self.keywords.tint_color = self.keywords.bg_color = self.bg_color = self.table.bg_color = INFO_STYLE

        self.add_subview(self.keywords)
        self.add_subview(self.table)
        self.add_subview(self.done_button)
        root_view.view.push_view(self)

    def draw(self):
        self.done_button.tint_color = SYSTEM_STYLE

    def search_button_tapped(self, sender):
        keywords = self.keywords.text
        if keywords:
            search_books(keywords)
            self.table.data_source = SearchDataSource('search')
            self.table.delegate = TableViewDelegate('search')
            self.table.reload_data()
        else:
            get_top_book()
            self.table.data_source = SearchDataSource('top')
            self.table.delegate = TableViewDelegate('top')


class SearchDataSource(object):
    # 搜索数据显示设置
    def __init__(self, mode):
        self.mode = mode

    def tableview_number_of_rows(self, tableview, section):
        if self.mode == 'search':
            return len(booksearch_list)
        elif self.mode == 'top':
            return len(booktop_list)
        elif self.mode == 'booklist':
            return len(booklist_books_list)

    def tableview_title_for_header(self, tableview, section):
        if self.mode == 'search':
            return '搜索到{}本符合要求的书'.format(len(booksearch_list))
        elif self.mode == 'top':
            title = booktop_name if 'booktop_name' in globals(
            ) else '正在加载Top数据...'
            return title
        else:
            return False

    def tableview_cell_for_row(self, tableview, section, row):
        if self.mode == 'search':
            self.book_id = booksearch_list[row]
            self.book_info = booksearch_data[self.book_id]
        elif self.mode == 'top':
            self.book_id = booktop_list[row]
            self.book_info = booktop_data[self.book_id]
        elif self.mode == 'booklist':
            self.book_id = booklist_books_list[row]
            self.book_info = booklist_books_data[self.book_id]
        cell = ui.TableViewCell('subtitle')
        cell.bg_color = INFO_STYLE
        cell.tint_color = SYSTEM_STYLE

        bg = ui.View()
        bg.bg_color = '#badf89'
        cover = ui.ImageView()
        cover.frame = (15, 10, 45, 60)
        cover.load_from_url(cover_url_encode(self.book_info['cover']))

        title = ui.Label()
        title.frame = (70, 0, 205, 50)
        title.number_of_lines = 0
        title.font = ('<System-Bold>', 18)
        title.text = self.book_info['title']

        author = ui.Label()
        author.frame = (70, 45, 205, 30)
        author.number_of_lines = 0
        author.font = ('<System>', 16)
        author.text_color = '#44a179'
        author.text = '作者:{author}'.format(**self.book_info)

        add_button = ui.Button()
        add_button.frame = (330, 20, 40, 40)
        add_button.image = ui.Image.named('iow:ios7_plus_outline_32')
        add_button.tint_color = SYSTEM_STYLE
        add_button.enabled = True if self.book_id not in bookcase_data else False

        detail_button = ui.Button()
        detail_button.frame = (280, 20, 40, 40)
        detail_button.tint_color = SYSTEM_STYLE
        detail_button.image = ui.Image.named('iow:ios7_information_outline_32')

        handler = SearchViewButton(self.mode, row)
        detail_button.action = handler.detail_tapped
        add_button.action = handler.add_tapped

        cell.selected_background_view = bg
        cell.content_view.add_subview(cover)
        cell.content_view.add_subview(title)
        cell.content_view.add_subview(author)
        cell.content_view.add_subview(add_button)

        cell.content_view.add_subview(detail_button)
        cell.detail_text_label.text_color = '#008923'
        return cell


class BookDetailView(ui.View):
    # 生成书本详情界面
    def __init__(self, book_id, mode):
        self.book_id = book_id
        self.mode = mode
        if self.mode == 'local':
            self.book_list = bookcase_list
            self.book_data = bookcase_data
        elif self.mode == 'search':
            self.book_list = booksearch_list
            self.book_data = booksearch_data
        elif self.mode == 'top':
            url = 'http://api.zhuishushenqi.com/book/{}'.format(self.book_id)
            res = api(url) or exit()
            res = json.loads(res)
            self.book_list = booktop_list
            self.book_data = {res['_id']: res}
        elif self.mode == 'booklist':
            self.book_list = booklist_books_list
            self.book_data = booklist_books_data
        self.book_info = self.book_data[self.book_id]
        self.name = self.book_info['title']

        self.frame = (0, 0, w, h)

        self.cover = ui.ImageView()
        self.cover.frame = (20, 20, 110, 150)
        self.cover.load_from_url(cover_url_encode(self.book_info['cover']))

        self.detail = ui.TextView()
        self.detail.frame = (150, 20, 205, 170)
        self.detail.text = '作者：{}\n\n分类：{}\n\n总字数：{}\n\n最新章节：{}'.format(
            self.book_info.get('author', '无信息'),
            self.book_info.get('cat', '无信息'),
            self.book_info.get('wordCount', '无信息'),
            self.book_info.get('lastChapter', '无信息'))
        self.detail.font = ('<System-Bold>', 16)
        self.detail.editable = False
        self.detail.selectable = False
        self.detail.scroll_enabled = True

        self.summary = ui.TextView()
        self.summary.frame = (20, 210, 335, 220)
        self.summary.font = ('<System-Bold>', 14)
        self.summary.editable = False
        self.summary.selectable = False
        if self.mode == 'local' or self.mode == 'top' or self.mode == 'booklist':
            self.summary.text = self.book_info['longIntro']
        else:
            self.summary.text = self.book_info['shortIntro']

        self.follower = ui.Label()
        self.follower.frame = (20, 180, 110, 14)
        self.follower.text_color = 'red'
        self.follower.font = ('<System>', 14)
        self.follower.alignment = ui.ALIGN_CENTER
        self.follower.text = '{:.1f}万人气'.format(
            self.book_info['latelyFollower'] / 1000)

        self.add = ui.Button()
        self.add.frame = (30, 450, 140, 40)
        self.add.tint_color = 'white'
        self.add.font = ('<System-Bold>', 16)
        self.add.border_width = 1
        self.add.corner_radius = 3
        self.add.action = self.add_button_tapped
        if self.book_id in bookcase_data:
            self.add.title = '－ 不追了'
            self.add.bg_color = '#b4b4b4'
        else:
            self.add.title = '+ 追更新'
            self.add.bg_color = '#992300'

        self.share = ui.Button()
        self.share.bg_color = '#992300'
        self.share.tint_color = 'white'
        self.share.frame = (205, 450, 140, 40)
        self.share.font = ('<System-Bold>', 16)
        self.share.title = '分享链接'
        self.share.border_width = 1
        self.share.corner_radius = 3
        self.share.action = self.share_button_tapped

        self.cover.bg_color = self.detail.bg_color = self.summary.bg_color = self.bg_color = INFO_STYLE
        self.add_subview(self.cover)
        self.add_subview(self.detail)
        self.add_subview(self.follower)
        self.add_subview(self.summary)
        self.add_subview(self.add)
        self.add_subview(self.share)
        root_view.view.push_view(self)

    def add_button_tapped(self, sender):
        if self.book_id in bookcase_data:
            bookcase_data_update(self.book_id, mode='del')
            self.add.title = '+ 追更新'
            self.add.bg_color = '#992300'
        else:
            bookcase_data_update(self.book_id)
            self.add.title = '－ 不追了'
            self.add.bg_color = '#b4b4b4'
        if self.mode == 'search':
            searchview.table.reload_data()
        elif self.mode == 'booklist':
            booklist_booksview.table.reload_data()

    def share_button_tapped(self, sender):
        url = 'https://m.zhuishushenqi.com/books/{}'.format(self.book_id)
        share_url(url)


class BookListView(ui.View):
    def __init__(self):
        self.name = '书单'
        self.tags = ui.SegmentedControl()
        self.tags.frame = (-10, 0, w + 20, 30)
        self.tags.bg_color = 'white'
        self.tags.tint_color = '#f99157'
        self.tags.segments = ('本周最热', '最新发布', '收藏最多')
        self.tags.selected_index = 0
        self.tags.action = self.tags_tapped

        self.list = ui.TableView()
        self.list.bg_color = '#f5f9f0'
        self.list.frame = (0, 30, w, h - 143)
        self.list.row_height = 100
        self.list.data_source = BookListDataSource()
        self.list.delegate = BookListDelegate()

        self.top_button = ui.Button()
        self.top_button.name = 'top'
        self.top_button.frame = (325, 250, 40, 40)
        self.top_button.tint_color = 'green'
        self.top_button.image = ui.Image.named('typb:Up')
        self.top_button.border_width = 1
        self.top_button.border_color = 'green'
        self.top_button.corner_radius = 20
        self.top_button.action = self.button_tapped

        self.down_button = ui.Button()
        self.down_button.name = 'down'
        self.down_button.frame = (325, 295, 40, 40)
        self.down_button.tint_color = 'green'
        self.down_button.image = ui.Image.named('typb:Down')
        self.down_button.border_width = 1
        self.down_button.border_color = 'green'
        self.down_button.corner_radius = 20
        self.down_button.action = self.button_tapped

        self.add_subview(self.tags)

        self.add_subview(self.list)
        self.add_subview(self.top_button)
        self.add_subview(self.down_button)
        root_view.view.push_view(self)

    def button_tapped(self, sender):
        if sender.name == 'top':

            self.list.content_offset = (0, 0)
        else:
            self.list.content_offset = (
                0, self.list.content_size[1] - self.list.height)

    def tags_tapped(self, sender):
        global book_lists_list, book_lists_data, book_list_mode
        book_lists_list = []
        book_lists_data = {}
        if sender.selected_index == 0:
            book_list_mode = 'week'
        elif sender.selected_index == 1:
            book_list_mode = 'new'
        elif sender.selected_index == 2:
            book_list_mode = 'top'
        get_book_list(book_list_mode, 0)
        self.list.reload_data()


class BookListDataSource(object):
    def tableview_number_of_rows(self, tableview, section):
        return len(book_lists_list)

    def tableview_cell_for_row(self, tableview, section, row):
        id = book_lists_list[row]
        item = book_lists_data[id]

        cell = ui.TableViewCell()
        cell.bg_color = INFO_STYLE

        cover = ui.ImageView()
        cover.frame = (10, 20, 40, 60)
        cover.load_from_url(cover_url_encode(item['cover']))

        title = ui.Label()
        title.frame = (60, 8, 305, 18)
        title.font = ('<System-Bold>', 16)
        title.text_color = SYSTEM_STYLE
        title.text = item['title']

        desc = ui.Label()
        desc.frame = (60, 24, 305, 56)
        desc.number_of_lines = 0
        desc.font = ('<System>', 12)
        desc.text_color = '#6e6e6e'
        desc.text = '作者：{author}\n简介：{desc}'.format(**item)

        info = ui.Label()
        info.frame = (60, 80, 305, 12)
        info.font = ('<System>', 12)
        info.text_color = 'red'
        info.text = '共{bookCount}本书  ｜  {collectorCount}人收藏'.format(**item)
        cell.content_view.add_subview(cover)
        cell.content_view.add_subview(title)
        cell.content_view.add_subview(desc)
        cell.content_view.add_subview(info)
        return cell


class BookListDelegate(object):
    def tableview_did_select(self, tableview, section, row):
        id = book_lists_list[row]
        get_booklist_books(id)
        global booklist_booksview
        booklist_booksview = BookListBooksView()

    def scrollview_did_scroll(self, scroll):
        if scroll.content_offset[1] > (
                len(book_lists_list) - 20) * 100 + 1483 + 60:
            get_book_list(book_list_mode, len(book_lists_list))


class Oval(ui.View):
    def __init__(self, color, *frame):
        self.size = frame
        self.color = color

    def draw(self):
        oval = ui.Path.oval(*self.size)
        rect = ui.Path.rect(*self.size)
        oval.append_path(rect)
        oval.eo_fill_rule = True
        oval.add_clip()
        ui.set_color(self.color)
        rect.fill()


class BookListBooksView(ui.View):
    def __init__(self):
        self.name = '书单详情'
        self.bg_color = INFO_STYLE

        author = booklist_data.get('author')
        self.avatar = ui.ImageView()
        self.avatar.frame = (10, 10, 50, 50)
        self.avatar.border_width = 0.1
        self.avatar.corner_radius = 25
        self.avatar.load_from_url(cover_url_encode(author['avatar']))

        self.title = ui.Label()
        self.title.frame = (10, 70, w - 20, 20)
        self.title.text_color = SYSTEM_STYLE
        self.title.font = ('<System-Bold>', 18)
        self.title.text = booklist_data.get('title', '')

        self.author = ui.Label()
        self.author.frame = (70, 10, w - 160, 50)
        self.author.number_of_lines = 0
        self.author.text_color = 'red'
        self.author.text = '{nickname}   Lv.{lv}'.format(**author)

        self.info = ui.Label()
        self.info.frame = (10, 93, w - 20, 14)
        self.info.number_of_lines = 0
        self.info.font = ('<System>', 14)
        self.info.text_color = '#575a5a'
        self.info.text = booklist_data.get('desc', '')
        self.info.size_to_fit()

        self.share = ui.Button()
        self.share.frame = (w - 85, 17.5, 70, 35)
        self.share.image = ui.Image.named('iow:ionic_24')
        self.share.tint_color = SYSTEM_STYLE
        self.share.font = ('<System-Bold>', 15)
        self.share.title = '分享'
        self.share.border_width = 1
        self.share.border_color = SYSTEM_STYLE
        self.share.corner_radius = 8
        self.share.action = self.booklist_share_tapped

        self.table = ui.TableView()
        self.table.frame = (0, self.info.y + self.info.height + 0, w,
                            h - self.info.y - self.info.height - 125)
        self.table.bg_color = INFO_STYLE
        self.table.row_height = 80
        self.table.data_source = SearchDataSource('booklist')
        self.table.delegate = TableViewDelegate('booklist')

        self.add_subview(self.avatar)
        oval = Oval(self.bg_color, self.avatar.x, self.avatar.y,
                    self.avatar.width, self.avatar.height)

        self.add_subview(oval)
        self.add_subview(self.title)
        self.add_subview(self.author)
        self.add_subview(self.info)
        self.add_subview(self.share)
        self.add_subview(self.table)
        root_view.view.push_view(self)

    def top_hide(self):
        self.table.y = 0
        self.table.height = h - 120

    def top_display(self):
        self.table.frame = (0, self.info.y + self.info.height + 10, w,
                            h - self.info.y - self.info.height - 125)

    def booklist_share_tapped(self, sender):
        share_url(booklist_data.get('shareLink', ''))


class BookSourceView(ui.View):
    def __init__(self, mode):
        self.mode = mode
        self.name = 'sourceview'
        self.bg_color = 'white'
        self.corner_radius = 15
        self.border_width = 1
        self.border_color = SYSTEM_STYLE

        self.close = ui.ImageView()
        self.close.image = ui.Image.named('iob:close_round_24')
        self.close.frame = (115, 260, 30, 30)

        self.table = ui.TableView()
        self.table.frame = (0, 0, 250, 350)
        self.table.row_height = 50
        self.table.shows_vertical_scroll_indicator = False
        self.table.bg_color = 'white'
        self.table.data_source = BookSourceDataSource(self.mode)
        self.table.delegate = BookSourceDelegate()

        if self.mode == 'reader':
            self.frame = (w / 2 - 250 / 2, h / 2 - 350 / 2, 250, 350)
        elif self.mode == 'chapter':
            self.frame = (65, 120, 250, 300)
            self.table.height = 250
            self.add_subview(self.close)
        self.add_subview(self.table)

    def touch_began(self, touch):
        chapterview.remove_subview(chapterview['sourceview'])


class BookSourceDataSource(object):
    def __init__(self, mode):
        self.mode = mode

    def tableview_number_of_rows(self, tableview, section):
        return len(sources_list)

    def tableview_cell_for_row(self, tableview, section, row):
        source = sources_list[row]
        cell = ui.TableViewCell()
        cell.text_label.text = source
        cell.text_label.font = ('<System-Bold>', 14)
        cell.text_label.text_color = '#006f82'

        cell_selected = ui.View()
        cell_selected.bg_color = '#f7ffc4'
        cell_selected.corner_radius = 15
        cell_selected.border_width = 3
        cell_selected.border_color = '#00c4a8'

        cell_logo = ui.View()
        cell_logo.frame = (5, 8, 5, cell.height - 16)
        cell_logo.bg_color = 'red'

        cell_detail = ui.Label()
        cell_detail.frame = (100, 0, 140, 50)
        cell_detail.number_of_lines = 3
        cell_detail.bg_color = 'white'
        cell_detail.font = ('<System>', 12)
        cell_detail.text_color = '#c400a7'
        cell_detail.text = sources_data[source]['lastChapter']
        cell.selected_background_view = cell_selected
        cell.content_view.add_subview(cell_detail)
        if source == chapterview.source_name:
            cell.content_view.add_subview(cell_logo)
        return cell


class BookSourceDelegate(object):
    # 选择源触发动作
    def tableview_did_select(self, tableview, section, row):
        source_name = sources_list[row]
        try:
            bookcase_data[chapterview.book_id]['source_log'] = source_name
        except:
            pass
        source_id = sources_data[source_name]['_id']
        get_book_chapters(source_id)
        chapterview.source_name = source_name
        booksourceview.table.reload_data()
        chapterview.chapter.reload_data()
        try:
            readerview.mode = 'source'
            readerview.set_needs_display()
        except:
            pass


class BookCaseDataSource(object):
    # 书架数据显示设置
    def __init__(self, mode):
        self.mode = mode

    def tableview_number_of_rows(self, tableview, section):
        return len(bookcase_list)

    def tableview_title_for_header(self, tableview, section):
        return '书架共{}本藏书'.format(len(bookcase_list))

    def tableview_can_delete(self, tableview, section, row):
        return True

    def tableview_delete(self, tableview, section, row):
        id = bookcase_list[row]

        bookcase_data_update(id, mode='del')
        bookcase_data_load()

    def tableview_cell_for_row(self, tableview, section, row):
        self.book_id = bookcase_list[row]
        self.book_info = bookcase_data[self.book_id]
        cell = ui.TableViewCell('subtitle')
        cell.bg_color = INFO_STYLE
        cell.tint_color = SYSTEM_STYLE
        cell.detail_text_label.text_color = '#008923'
        cell.accessory_type = 'detail_button'

        cover = ui.ImageView()
        cover.frame = (15, 10, 45, 60)
        img_path = path.join(BOOK_DATA_DIR,
                             '.cache/{}.jpg'.format(self.book_id))

        cover.image = ui.Image.named(img_path)

        title = ui.Label()
        title.frame = (70, 5, 255, 40)
        title.font = ('<System-Bold>', 18)
        title.text = self.book_info['title']

        status = ui.Label()
        status.frame = (70, 35, 255, 40)
        status.number_of_lines = 0
        status.font = ('<System>', 16)
        status.text_color = '#44a179'
        status.number_of_lines = 2
        if 'update_data' in globals() and self.book_id in update_data:
            title.text_color = status.text_color = '#ff00d9'
            status.text = update_data[self.book_id]
        else:
            status.text = self.book_info['lastChapter']
        cell.content_view.add_subview(cover)
        cell.content_view.add_subview(title)
        cell.content_view.add_subview(status)
        return cell


class TableViewDelegate(object):
    # 选中小说后触发动作
    def __init__(self, mode):
        self.mode = mode

    def tableview_did_select(self, tableview, section, row):
        global chapterview
        if self.mode == 'local':
            self.book_id = bookcase_list[row]
            if 'update_data' in globals() and self.book_id in update_data:
                del update_data[self.book_id]
                root_view.bookcase.reload_data()
            if 'update_info' in bookcase_data[self.book_id]:
                del bookcase_data[self.book_id]['update_info']
                root_view.bookcase.reload_data()
            chapterview = ChapterView(self.book_id, mode=self.mode)
            auto_open_book(self.book_id)
        elif self.mode == 'search':
            self.book_id = booksearch_list[row]
            chapterview = ChapterView(self.book_id, mode=self.mode)
        elif self.mode == 'top':
            self.book_id = booktop_list[row]
            chapterview = ChapterView(self.book_id, mode=self.mode)
        elif self.mode == 'booklist':
            self.book_id = booklist_books_list[row]
            chapterview = ChapterView(self.book_id, mode=self.mode)

    def tableview_accessory_button_tapped(self, tableview, section, row):
        global bookdetailview
        if self.mode == 'local':
            bookdetailview = BookDetailView(bookcase_list[row], self.mode)
        elif self.mode == 'search':
            bookdetailview = BookDetailView(booksearch_list[row], self.mode)

    def scrollview_did_scroll(self, scroll):
        y = scroll.content_offset[1]
        if self.mode == 'local':
            if root_view.bookcase.on_screen and not root_view['refresh'] and y < -50:
                root_view.add_subview(root_view.refresh)
            elif root_view['refresh'] and y > -20:
                bookcase_refresh()
                root_view.remove_subview(root_view.refresh)
        if self.mode == 'booklist':
            if scroll.dragging:
                ui.animate(booklist_booksview.top_hide, 1)
            elif not scroll.dragging and y == 0:
                ui.animate(booklist_booksview.top_display, 1)


class SuperRootView(ui.View):
    # 生成程序根视图界面
    def __init__(self):
        self.bg_color = SYSTEM_STYLE

        self.bookcase = ui.TableView()
        self.bookcase.bg_color = INFO_STYLE
        self.bookcase.name = '追书神器'
        self.bookcase.row_height = 80
        self.bookcase.height = h - 50
        self.bookcase.data_source = BookCaseDataSource('local')
        self.bookcase.delegate = TableViewDelegate('local')

        self.refresh = ui.Label()
        self.refresh.name = 'refresh'
        self.refresh.frame = (w / 2 - 30, 80, 60, 12)
        self.refresh.font = ('<System-Bold>', 12)
        self.refresh.text_color = 'red'
        self.refresh.text = '检查更新...'

        self.menubar = ui.View()
        self.menubar.frame = (0, h - 50, w, 50)

        self.button1 = ui.Button()
        self.button1.frame = (0, 5, 75, 40)
        self.button1.tint_color = 'white'
        self.button1.image = ui.Image.named('typw:Search')
        self.button1.action = button1_tapped

        self.button2 = ui.Button()
        self.button2.frame = (75, 5, 75, 40)
        self.button2.tint_color = 'white'
        self.button2.image = ui.Image.named('iow:ios7_bookmarks_32')
        self.button2.action = button2_tapped

        self.button3 = ui.Button()
        self.button3.frame = (150, 5, 75, 40)
        self.button3.image = ui.Image.named('typw:Home')
        self.button3.tint_color = 'white'
        self.button3.action = button3_tapped

        self.button4 = ui.Button()
        self.button4.frame = (225, 5, 75, 40)
        self.button4.image = ui.Image.named('iow:gear_b_32')
        self.button4.tint_color = 'white'
        self.button4.action = button4_tapped

        self.button5 = ui.Button()
        self.button5.frame = (300, 5, 75, 40)
        self.button5.image = ui.Image.named('iow:ios7_close_32')
        self.button5.tint_color = 'white'
        self.button5.action = button5_tapped

        self.view = ui.NavigationView(self.bookcase)
        self.view.frame = (0, 0, w, h - 50)
        self.view.tint_color = 'white'
        self.view.title_color = 'white'

        self.network_status = ui.ActivityIndicator()
        self.network_status.center = (w / 2, h / 2)
        self.menubar.add_subview(self.button1)
        self.menubar.add_subview(self.button2)
        self.menubar.add_subview(self.button3)
        self.menubar.add_subview(self.button4)
        self.menubar.add_subview(self.button5)
        self.add_subview(self.menubar)
        self.add_subview(self.view)
        self.add_subview(self.network_status)

    def draw(self):
        self.view.bg_color = SYSTEM_STYLE
        self.view.bar_tint_color = SYSTEM_STYLE
        self.menubar.bg_color = SYSTEM_STYLE

    def will_close(self):
        if bookcase_data: bookcase_data_write(bookcase_data)


if __name__ == '__main__':
    system_config()
    bookcase_data_load()
    w, h = ui.get_screen_size()
    root_view = SuperRootView()
    root_view.present(hide_title_bar=True)
    app.zssq = root_view
    app.zssq.bookcase_data = bookcase_data
