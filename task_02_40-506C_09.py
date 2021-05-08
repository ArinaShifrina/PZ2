import numpy as np
import matplotlib.pyplot as plt
import os
import requests as rqst
import re
import scipy.special as sc
import xml.etree.ElementTree as ET

# сферическая функция Бесселя третьего рода

def h(n, x):
    return sc.spherical_jn(n, x) + 1j * sc.spherical_yn(n, x)

# Коэффициент, определяемый отношением сферической функции Бесселя
# первого рода порядка n к сферической функции Бесселя третьго рода

def a(n, x):
    return sc.spherical_jn(n, x) / h(n, x)

# Коэффициент, который определяется с помощью волнового числа (k),
# радиуса сферы (r), сферической функции Бесселя первого рода,
# сферической функции Бесселя третьего рода

def b(n, x):
    return ((x * sc.spherical_jn(n - 1, x) - n * sc.spherical_jn(n, x))
            / (x * h(n - 1, x) - n * h(n, x)))

# Функция для выходного файла с результатами в формате XML (9 вариант)

def XML(frequency, Lambda, rcs):

    # Формирование файловой структуры
    data = ET.Element('data')
    frequencydata = ET.SubElement(data, 'frequencydata')
    for i in frequency:
        frequency1 = ET.SubElement(frequencydata, 'f')
        frequency1.text = str(i)
    lambdadata = ET.SubElement(data, 'lambdadata')
    for i in Lambda:
        lambda1 = ET.SubElement(lambdadata, 'lambda')
        lambda1.text = str(i)
    rcsdata = ET.SubElement(data, 'rcsdata')
    for i in rcs:
        rcs1 = ET.SubElement(rcsdata, 'rcs')
        rcs1.text = str(i)

    # Формирование файла XML с результатами 
    myfile = open('results/task_02_40-506C_09.xml', 'w')
    myfile.write(ET.tostring(data, method='xml').decode(encoding='utf-8'))
    myfile.close()

# Функция, которая определяет ЭПР идеально проводящей сферы от частоты

def RCS(D, fmin, fmax):

    # Скорость света
    c = 3e8

    # Радиус сферы
    r = D/2

    # Диапазон частот, определяемый заданием
    f = np.arange(fmin, fmax+1e7, 1e7)

    # Диапазон длин волн, исходя из диапазона частот
    Lambda = c/f
    sigma = []

    # Вычисление ЭПР на каждой длине волны из диапазона
    for i in Lambda:
        k = 2 * np.pi / i
        summa = []
        for n in range(1,100):
            summa.append((-1) ** n * (n + 0.5) * (b(n, k * r) - a(n, k * r)))
        sigma.append((i ** 2 / np.pi) * abs(sum(summa)) ** 2)

    # Вывод результатов в XML файл
    XML(f, Lambda, sigma)

    # Построение графика
    plt.plot(f, sigma)
    plt.grid()
    plt.xlabel('$f$, [Гц]')
    plt.ylabel('$sigma$, [$м^2$]')
    plt.show()
           
if __name__ == '__main__':

    # Создание директории "results" для сохранения файла
    # с результатами расчета в директории скрипта
    try: os.mkdir('results')
    except OSError: pass

    # Загрузка файла с заданием из Интернета с помощью библиотеки requests
    # согласно адресу варианта 9
    r = rqst.get('https://jenyay.net/uploads/Student/Modelling/task_02_01.txt')

    # Выбор строки задания согласно номеру варианта
    for i in r.text.splitlines():
        if re.match(r'9\.', i): z = i

    # Формирование списка из 3х заданных параметров D, fmin, fmax
    # выбранной строки с помощью регулярных выражений
    match = list(map(lambda z:float(z), re.findall(r'=(\d+\.?\d*[e-]*\d+)',z)))
    D, fmin, fmax = match[0], match[1], match[2]

    # Выполнение функции, вычисляющей ЭПР и строящей график
    RCS(D, fmin, fmax)
