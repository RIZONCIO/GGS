import random
import string

def remover_repetidos(s):
    resultado = ""
    for c in s:
        if c not in resultado:
            resultado += c
    return resultado

def generate_password(keyword, custom_password, uppercase_var, lowercase_var, numbers_var, symbols_var, remove_duplicates, password_length):
    if not keyword:
        return "Por favor, insira uma palavra-chave."

    metade = password_length // 2
    if custom_password:
        allowed_chars = ''
        if uppercase_var:
            allowed_chars += string.ascii_uppercase
        if lowercase_var:
            allowed_chars += string.ascii_lowercase
        if numbers_var:
            allowed_chars += string.digits
        if symbols_var:
            allowed_chars += string.punctuation

        if not allowed_chars:
            return "Por favor, selecione pelo menos uma opção de personalização de senha."

        random_chars_start = ''.join(random.choices(allowed_chars, k=metade))
        random_chars_end = ''.join(random.choices(allowed_chars, k=password_length - metade))
        password = f"{random_chars_start}{keyword}{random_chars_end}"
    else:
        allowed_chars = string.ascii_letters + string.digits + string.punctuation
        random_chars_start = ''.join(random.choices(allowed_chars, k=metade))
        random_chars_end = ''.join(random.choices(allowed_chars, k=password_length - metade))
        password = f"{random_chars_start}{keyword}{random_chars_end}"

    if remove_duplicates:
        password = remover_repetidos(password)

    return password
