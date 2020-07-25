def Function(value):
    if(value >=10):
        return
    value = value + 1
    Function(value)
    value = value - 1
    print(value)

Function(1)
