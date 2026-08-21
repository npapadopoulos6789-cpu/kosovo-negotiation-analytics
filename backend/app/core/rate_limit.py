"""
Βασικό rate limiting για τα endpoints που καλούν πραγματικό, πληρωμένο
Anthropic API (POST /synthesis, /compare, /negotiation-analyses/) -- ένα
δημόσιο site χωρίς όριο εδώ σημαίνει απεριόριστο κόστος από οποιονδήποτε
επισκέπτη. Key ανά IP (`get_remote_address`), 5/hour ανά endpoint (ξεχωριστό
όριο το καθένα, όχι κοινό budget των τριών μαζί). Τα υπόλοιπα (GET)
endpoints δεν έχουν όριο.
"""
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)
