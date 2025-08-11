from inspect import signature
from functools import wraps

def enforce_types(func):
    '''
    Decorator to enforce PEP484 type annotations on function arguments and return values.
    
    This decorator checks the types of the arguments passed to the function and the type of the return value against the annotations specified in the function's signature.
    If the types do not match, it raises a TypeError.
    Args:
        func (callable): The function to be decorated.
                        (optional) PEP484 type annotations for its parameters and return value.
    '''

    # Get annotations and signature of the function
    sig = signature(func)
    PEP484_annotations = func.__annotations__
    
    @wraps(func)
    def wrapper(*args, **kwargs):
        # gets the variable names and variable values from the function call
        bound_args = sig.bind(*args, **kwargs)
        bound_args.apply_defaults()

        # Check in-comming arguments against PEP484 annotations
        for var_name, var_value in bound_args.arguments.items():
            expected_type = PEP484_annotations.get(var_name)
            if expected_type and not isinstance(var_value, expected_type):
                raise TypeError(f"Argument '{var_name}' must be {expected_type}, got {var_value}")  
        else:
            returns = func(*args, **kwargs)
        
        # Check return value against PEP484 annotations
        expected_return_type = PEP484_annotations.get('return')
        if expected_return_type and not isinstance(returns, expected_return_type):
            raise TypeError(f"Return value must be {expected_return_type}, got {type(returns)}")

        return returns
    return wrapper