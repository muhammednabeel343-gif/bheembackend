import google.generativeai as ggen

API_KEY = 'AIzaSyDIuHxlHA5matmNwb_73dVCZJW3AqDzl0Q'

ggen.configure(api_key=API_KEY)
print('module', ggen)
print('has list_models', hasattr(ggen, 'list_models'))
print('list_models type', type(ggen.list_models()))

models = ggen.list_models()
for i, m in enumerate(models):
    if i >= 80:
        break
    name = getattr(m, 'name', None)
    print(i, repr(name), type(m))
