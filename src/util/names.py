# encoding=utf-8
from codecs import open

from stringgenerator import NameGenerator

tolkien_names = open('src/util/tolkien_names.txt', 'r', encoding='utf-8').readlines()

tolkien_gen = NameGenerator(tolkien_names)
