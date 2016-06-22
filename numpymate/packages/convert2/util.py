#!/usr/bin/env python
# -*- coding: utf-8 -*-

def extract_number_from_string(text):
    """Take number like string out of text.
    """
    numberstr_list = list()
    chunks = list()
    
    for char in text:
        if char.isdigit() or char == ".":
            chunks.append(char)
        else:
            if len(chunks):
                numberstr_list.append("".join(chunks))
                chunks = list()
    
    if len(chunks):
        numberstr_list.append("".join(chunks))
    
    new_numberstr_list = list()
            
    for s in numberstr_list:
        try:
            float(s)
            new_numberstr_list.append(s)
        except:
            pass

    return new_numberstr_list
    