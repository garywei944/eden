class A:
    def __new__(cls, *args, **kwargs):
        # Check some condition to replace with B
        if cls is A:  # Ensure that we only replace when creating A, not subclasses
            instance = super().__new__(B)
            return instance
        return super().__new__(cls)

    def __init__(self):
        print(f"Initializing class A: {self}")


class B(A):
    def __init__(self):
        print(f"Initializing class B: {self}")


# When you try to create an instance of A, it will return an instance of B
a = A()
print(f"Type of a: {type(a)}")
