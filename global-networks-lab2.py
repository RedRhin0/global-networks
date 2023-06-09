# -*- coding: utf-8 -*-
import random
import numpy as np
import binascii

word_lenght = 46

def calculate_crc32(text):
    message_bytes = text.encode('utf-8')
    crc32 = binascii.crc32(message_bytes)
    crc32_hex = format(crc32 & 0xFFFFFFFF, '08x')
    return crc32_hex

def text_to_bits(text, encoding='utf-8', errors='surrogatepass'):
    bits = bin(int.from_bytes(text.encode(encoding, errors), 'big'))[2:]
    return bits.zfill(8 * ((len(bits) + 7) // 8))

def text_from_bits(bits, encoding='utf-8', errors='surrogatepass'):
    n = int(bits, 2)
    return n.to_bytes((n.bit_length() + 7) // 8, 'big').decode(encoding, errors) or '\0'

def read_f(path, length_w):
    text = ""
    with open(path, "r", encoding='utf-8') as fale:
        for line in fale.readlines():
            text += line

    text_in_bits = ''
    word = ''
    end = False
    i = 0
    while i < len(text):
        w = text_to_bits(text[i])
        if len(word) + len(w) > length_w:
            new_word = ''
            for j in range(len(word), length_w):
                new_word += '0'
            new_word += word
            text_in_bits += new_word
            word = ''
        else:
            word += w
            i += 1
            if i == len(text):
                new_word = ''
                for j in range(len(word), length_w):
                    new_word += '0'
                new_word += word
                text_in_bits += new_word
                i += 1
    return text, text_in_bits

def needed_k(m):  # m - длина битовой строки
    k = 0
    while 2 ** k - k < m + 1:
        k += 1
    return k

def enter_control(line, k):  # вставка контрольных битов
    old_line = line
    mas_of_index = []
    for i in range(k):
        mas_of_index.append(2 ** i - 1)
        new_line = old_line[:2 ** i - 1] + '0' + old_line[2 ** i - 1:]
        old_line = new_line
    return new_line

def to_bin(n, k):  # n - дес. число, k - кол-во конт.бит
    ans = np.zeros((k), dtype=int)
    b = bin(n)[2:]
    while len(b) < k:
        b = '0' + b
    for i in range(len(b)):
        ans[k - i - 1] = int(b[i])
    return (ans)

def calc_control(word, k):  # k - к-во контрольных битов
    matr = np.zeros((k + 1, len(word)), dtype=int)
    for i in range(0, len(word)):
        matr[0, i] = int(word[i])
    for i in range(1, len(word) + 1):
        matr[1:, i - 1] = to_bin(i, k)
    for i in range(k):
        matr[0, 2 ** i - 1] = sum(matr[i + 1, :] * matr[0, :]) % 2
    ans = ''
    for i in matr[0, :]:
        ans += i.astype(str)
    return ans

def code_word(word):
    k = needed_k(len(word))
    return calc_control(enter_control(word, k), k)

def enter_errors(word, num):
    a = random.sample(range(len(word)), num)
    old_word = word
    for i in a:
        new_word = old_word[:i]
        if word[i] == '0':
            new_word += '1'
        else:
            new_word += '0'
        new_word += old_word[i + 1:]
        old_word = new_word
    return len(a), new_word

def decode_word(word, k):
    ind = [2 ** i - 1 for i in range(k)]
    i = 0
    true_word = ''
    for j in ind:
        true_word += word[i:j]
        i = j + 1
    true_word += word[j + 1:]
    return true_word

def correct_control(word, k):  # k - к-во контрольных битов
    matr = np.zeros((k + 1, len(word)), dtype=int)
    for i in range(0, len(word)):
        matr[0, i] = int(word[i])
    for i in range(1, len(word) + 1):
        matr[1:, i - 1] = to_bin(i, k)
    s = np.zeros((k), dtype=int)
    for i in range(k):
        s[i] = sum(matr[i + 1, :] * matr[0, :]) % 2
    if (s == 0).all():
        return True, word
    else:
        for i in range(len(word)):
            new_word = ''
            if (matr[1:, i] == s).all():
                new_word += word[:i]
                matr[0, i] = (matr[0, i] + 1) % 2
                new_word += matr[0, i].astype(str)
                new_word += word[i + 1:]
                return False, new_word
        return False, word

def decode_bits(text_in_bits, length_w):
    text = ''
    found_err = []
    found_multi_err = []
    ind = -1;

    for i in range(0, len(text_in_bits), length_w):
        # закодированное одно слово
        word = text_in_bits[i:i + length_w]
        ind += 1

        # корректировка
        bol, correct_word = correct_control(word, needed_k(length_w))

        if not bol:
            found_err.append(ind)
        
        correct_word = decode_word(correct_word, needed_k(length_w))
        try:
            cur_word = text_from_bits(correct_word[len(correct_word) % 8:])
            text += cur_word
        except:
            found_multi_err.append(ind)
            continue
    return text, len(found_err), len(found_multi_err)


word_length = 46
length = 46

# const_err:
# 1. Без ошибок
# 2. С возможными ошибками (не более 1 на слово)
# 3. С множественными ошибками (более 1 на слово, но не обязательно во всех словах)
const_err = 3

input_text, text_in_bits = read_f("text.txt", length)
message = ''
ind = -1
ind_errors = []
ind_multi_errors = []


if const_err == 2 or const_err == 3:
    # количество ошибок
    count = random.randint(1, len(text_in_bits) / length)
    # индексы слов, в которых вставляется ошибка
    a = random.sample(range(int(len(text_in_bits) / length)), count)

for begin_word in range(0, len(text_in_bits), length):
    # закодированное слово
    word = code_word(text_in_bits[begin_word:begin_word + length])
    ind += 1
    # вставка ошибок
    if const_err == 2:
        if ind in a:
            count_err, word = enter_errors(word, 1)
            ind_errors.append(ind)
    if const_err == 3:
        if ind in a:
            current_err = random.randint(1, len(word))
            count_err, word = enter_errors(word, current_err)
            ind_errors.append(ind)
            if count_err > 1:
                ind_multi_errors.append(ind)
    message += word

print("CRC32 исходного текста: {}".format(calculate_crc32(input_text)))
print("Всего {} слов".format(ind))
print("Слов с ошибками: {} ".format(len(ind_errors)))
print("Слов с множественными ошибками: {} ".format(len(ind_multi_errors)))
recieved_text, found_err, found_multi_err = decode_bits(message, length + needed_k(length))
print("Было найдено {} ошибок".format(found_err))
print("Было найдено {} множественных ошибок".format(found_multi_err))
print("CRC32 раскодированного текста: {}".format(calculate_crc32(recieved_text)))
print("Совпадают ли CRC32 : {}".format(input_text==recieved_text))
