# -*- coding: utf-8 -*-
"""博客构建配置文件
"""

# For Maverick
site_prefix = "/"
source_dir = "../src/"
build_dir = "../dist/"
index_page_size = 10
archives_page_size = 20
template = {
    "name": "Prism",
    "type": "local",
    "path": "../Galileo"
}
enable_jsdelivr = {
    "enabled": True,
    "repo": "z1137254268/Blog-With-GitHub-Boilerplate@gh-pages"
}

# 站点设置
site_name = "Neu"
site_logo = "${static_prefix}logo.png"
site_build_date = "2019-12-18T16:51+08:00"
author = "Neu"
email = "1137254268@qq.com"
author_homepage = "http://banszd.top"
description = "只坚持一种正义。我的正义。"
key_words = ['Maverick', 'Neu', 'Galileo', 'blog']
language = 'zh-CN'
external_links = [
    {
        "name": "Neu",
        "url": "https://blong.banszd.top/",
        "brief": "笨比。"
    }
]
nav = [
    {
        "name": "首页",
        "url": "${site_prefix}",
        "target": "_self"
    },
    {
        "name": "归档",
        "url": "${site_prefix}archives/",
        "target": "_self"
    },
    {
        "name": "关于",
        "url": "${site_prefix}about/",
        "target": "_self"
    }
]

social_links = [
    {
        "name": "GitHub",
        "url": "",
        "icon": "gi gi-github"
    }
]

head_addon = r'''
<meta http-equiv="x-dns-prefetch-control" content="on">
<link rel="dns-prefetch" href="//cdn.jsdelivr.net" />
'''

valine = {
    "enable": True,
    "el": '#vcomments',
    "appId": "5xzvxkmRLmbFJaYon5mOUndy-MdYXbMMI",
    "appKey": "7ExQ25scyIqACsvqGeITqr7S",
    "visitor": True,
    "recordIP": True
}

footer_addon = ''

body_addon = ''
