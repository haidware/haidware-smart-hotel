from django import template
register=template.Library()
@register.filter
def currency(v):
 try:return f'₦{int(v):,}'
 except:return v
@register.simple_tag(takes_context=True)
def nav_active(context,name):
 r=context.get('request')
 return 'active' if r and r.resolver_match and r.resolver_match.url_name==name else ''
