from django import template

register = template.Library()

@register.filter(name="add_attributes")
def add_attributes(value, arg):
    # print(f"--->{value}")
    # print(f"--->{arg}")

    # split attributes passed as args
    attrs = arg.split(',')
    
    # create an empty dictionary for attributes passed as args
    new_attrs={}
    for val in attrs:
        # split every single attribute and convert it a to tuple
        k,v = tuple(val.split('='))

        # remove trailing and leading whitespace
        k = k.strip()

        new_attrs[k]=v
    # print(new_attrs)
    # print(attrs)

    # get all the default attributes 
    attributes = value.field.widget.attrs.items()

    # convert dict_items to dictionary
    new_attributes = dict(attributes)

    # update attributes dictionary
    new_attributes.update(new_attrs)

    # print(attributes)
    # print(list(new_attributes.items()))
    
    # convert attributes to list of tuple
    attributes = list(new_attributes.items()) 

    return value.as_widget(attrs=attributes)