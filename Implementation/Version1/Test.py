class Test:
    def __init__(self,value):
        self.value = value

dict = {}
dict['a'] = Test(10)
b = dict['a']
print(id(dict['a']))
print(id(b))
del b

if(dict.get('a') == None):
    print("NONE")
else:
    print("NOT deleted")
    print(dict['a'].value)
print(b.value)
