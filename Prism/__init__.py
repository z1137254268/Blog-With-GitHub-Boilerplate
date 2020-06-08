# -*- coding: utf-8 -*-
"""Prism

A theme for Maverick
"""

from Maverick.Template import Template, Pager
from Maverick.Content import ContentList, group_by_category, group_by_tagname
from Maverick.Utils import logged_func, gen_hash, unify_joinpath, copytree
from Maverick.Utils import safe_write, safe_read
from .utils import tr, build_navs, build_links, filterPrefix

import os
import re
import json
import math


def render(conf, posts, pages):
    """Override this
    """
    Prism(conf, posts, pages)()


class Prism(Template):
    def render(self):
        self._env.globals['tr'] = tr
        self._env.globals['len'] = len
        self._env.globals['build_navs'] = build_navs
        self._env.globals['build_links'] = build_links
        self._env.globals['get_path'] = filterPrefix

        try:
            from Maverick.Markdown import g_hooks
            g_hooks.add_hook('output_image', self.output_image)
        except BaseException:
            pass

        self.build_search_cache()
        self.gather_meta()
        self.build_posts()
        self.build_pages()

        # filter out hidden posts before building post list
        self._posts = ContentList(
            [item for item in self._posts if not item.skip])
        self._pages = ContentList(
            [item for item in self._pages if not item.skip])

        self.build_index()
        self.build_archives()
        self.build_categories()
        self.build_tags()

        # copy static files to build_dir
        def copy_assets(src, dist):
            source_dir = unify_joinpath(os.path.dirname(__file__), src)
            dist_dir = unify_joinpath(self._config.build_dir, dist)

            if not os.path.exists(source_dir):
                return

            if not os.path.exists(dist_dir):
                os.mkdir(dist_dir)
            copytree(source_dir, dist_dir)
        copy_assets('assets', 'assets')

    def output_image(self, image):
        figcaption = image['title'] or ''

        src = image['src']

        classname = ''
        style = ''
        attr = ''
        if image['width'] != -1 and image['height'] != -1:
            style = 'style="flex: %s"' % str(image['width'] * 50 / image['height'])
            if image['width'] < image['height']:
                classname = 'class="vertical-figure"'
        else:
            attr = 'size-undefined'

        if figcaption != "":
            figcaption = '<figcaption>%s</figcaption>' % figcaption

        return '<figure %s %s %s><img width="%s" height="%s" src="%s" alt="%s"/>%s</figure>' \
            % (classname, style, attr, image['width'], image['height'], src, image['alt'], figcaption)

    def gather_meta(self):
        self._tags = set()
        self._categories = set()
        for content in self._posts:
            meta = content.meta
            self._tags = set(meta["tags"]) | self._tags
            self._categories = set(meta["categories"]) | self._categories

    @logged_func('')
    def build_index(self):
        pager = Pager(self._posts, self._config.index_page_size)
        total_pages = pager.get_total_pages()

        for current_page, current_list in pager:
            _, local_path = self._router.gen("index", "", current_page)
            local_path += "index.html"

            template = self._env.get_template("index.html")
            output = template.render(
                content_list=current_list,
                current_page=current_page,
                max_pages=total_pages)
            safe_write(local_path, output)

    @logged_func('')
    def build_archives(self):
        pager = Pager(self._posts, self._config.archives_page_size)
        total_pages = pager.get_total_pages()

        for current_page, current_list in pager:
            _, local_path = self._router.gen("archives", "", current_page)
            local_path += "index.html"

            template = self._env.get_template("archives.html")
            output = template.render(
                content_list=current_list,
                current_page=current_page,
                max_pages=total_pages)
            safe_write(local_path, output)

    @logged_func('')
    def build_tags(self):
        for tag in self._tags:
            posts = self._posts.re_group(group_by_tagname(tag))

            pager = Pager(posts, self._config.archives_page_size)
            total_pages = pager.get_total_pages()

            for current_page, current_list in pager:
                _, local_path = self._router.gen("tag", tag, current_page)
                local_path += "index.html"

                template = self._env.get_template("tags.html")
                output = template.render(
                    tag_name=tag,
                    content_list=current_list,
                    current_page=current_page,
                    max_pages=total_pages)
                safe_write(local_path, output)

    @logged_func('')
    def build_categories(self):
        for category in self._categories:
            posts = self._posts.re_group(group_by_category(category))

            pager = Pager(posts, self._config.archives_page_size)
            total_pages = pager.get_total_pages()

            for current_page, current_list in pager:
                _, local_path = self._router.gen("category", category, current_page)
                local_path += "index.html"

                template = self._env.get_template("categories.html")
                output = template.render(
                    cate_name=category,
                    content_list=current_list,
                    current_page=current_page,
                    max_pages=total_pages)
                safe_write(local_path, output)

    @logged_func()
    def build_posts(self):
        total_posts = len(self._posts)
        for index in range(total_posts):
            content = self._posts[index]

            # find visible prev and next
            index_next = index
            content_next = None
            while content_next is None and index_next > 0:
                index_next -= 1
                if not self._posts[index_next].skip:
                    content_next = self._posts[index_next]

            index_prev = index
            content_prev = None
            while content_prev is None and index_prev < total_posts-1:
                index_prev += 1
                if not self._posts[index_prev].skip:
                    content_prev = self._posts[index_prev]

            meta = content.meta
            _, local_path = self._router.gen_by_meta(meta)
            local_path += "index.html"

            template = self._env.get_template("post.html")
            output = template.render(
                content=content,
                content_prev=content_prev,
                content_next=content_next
            )
            safe_write(local_path, output)
            print('Finished: ' + content.get_meta('title'))

    @logged_func()
    def build_pages(self):
        total_pages = len(self._pages)
        for index in range(total_pages):
            content = self._pages[index]
            content_next = self._pages[index-1] if index > 0 else None
            content_prev = self._posts[index +
                                       1] if index < total_pages-1 else None

            _, local_path = self._router.gen_by_content(content)
            local_path += "index.html"

            template = self._env.get_template("page.html")
            output = template.render(
                content=content,
                content_prev=content_prev,
                content_next=content_next
            )
            safe_write(local_path, output)
            print('Finished: ' + content.get_meta('title'))

    @logged_func()
    def build_search_cache(self):
        """build search cache json
        """
        def render_search_cache(post_list, page_list):
            router = self._router

            def strip(text):
                r = re.compile(r'<[^>]+>', re.S)
                return r.sub('', text)

            def gen_entry(content):
                entry = {
                    "title": content.get_meta('title'),
                    "date": str(content.get_meta('date')),
                    "path": router.gen_permalink_by_content(content),
                    "text": strip(content.parsed),
                    "categories": [],
                    "tags": []
                }
                if (content.get_meta('layout') == 'post'):
                    for cate in content.get_meta('categories'):
                        entry['categories'].append({
                            "name": cate,
                            "slug": cate,
                            "permalink": router.gen_permalink('category', cate, 1)
                        })
                    for tag in content.get_meta('tags'):
                        entry['tags'].append({
                            "name": tag,
                            "slug": tag,
                            "permalink": router.gen_permalink('tag', tag, 1)
                        })
                return entry

            posts = [gen_entry(post) for post in post_list if not post.skip]
            pages = [gen_entry(page) for page in page_list if not page.skip]

            cache = json.dumps({
                "posts": posts,
                "pages": pages
            })

            return cache

        cache_str = render_search_cache(self._posts, self._pages)
        search_cache_hash = gen_hash(cache_str)
        safe_write(unify_joinpath(
            self._config.build_dir, search_cache_hash + '.json'), cache_str)

        self._env.globals['search_cache_hash'] = search_cache_hash
