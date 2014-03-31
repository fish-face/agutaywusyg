# encoding=utf-8
from util.stringgenerator import NameGenerator

tolkien_names = open('src/util/tolkien_names.txt', 'r').readlines()

tolkien_gen = NameGenerator(tolkien_names)
