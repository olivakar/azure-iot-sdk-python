# Developing a pythonic wrapper for a C Header file

As the developer of the library we have access to the header file written in C. The header file is the contract between us and the customer who may have an implementation that we are not aware of. We use a native python library called `ctypes` which would help us to do this.

## The main function in C

The main function from the contract that must be implemented is :-
`extern const HSM_CLIENT_X509_INTERFACE* hsm_client_x509_interface();`
It is observed that this function does not take any input argument and returns pointer to `HSM_CLIENT_X509_INTERFACE`.

Looking inside the header file we find that the above `HSM_CLIENT_X509_INTERFACE` is a structure consisting of 5 items of 5 different types. The types are :-
* HSM_CLIENT_CREATE
* HSM_CLIENT_DESTROY
* HSM_CLIENT_GET_CERTIFICATE
* HSM_CLIENT_GET_ALIAS_KEY
* HSM_CLIENT_GET_COMMON_NAME

Looking at each of those type we find they all represent types of function pointer.

### Defining callable in Python

#### STEP 1 - Retrieve address of compiled function

After loading the C library , the main function is accessed by the same name from the contract.
We need to obtain the raw, low-level address of this compiled C function and turn it back into a python callable object wrapping the arbitrary memory address.

Getting the address requires us to do cast the compiled fucntion into a `void` pointer :-
```python
address = ctypes.cast(compiled_function, ctypes.c_void_p).value 
```

#### STEP 2 - Define return type

Since the main function returns a structure containing 5 items , we have defined our own structure called `StructX509` which serves as the return type for our main function. The `StructX509` has been defined to be consisting of 5 void type pointers.

#### STEP 3 - Define the functype

A CFUNCTYPE instance has to be created next to make a callable. The first argument to CFUNCTYPE() is the return type followed by the input argument types. After defining the function type, it is wrapped around the integer memory address to create a callable object. The resulting object is used like any normal function accessed through ctypes.

```python
functype = ctypes.CFUNCTYPE(ctypes.POINTER(StructX509))
callable = functype(address)
```
#### STEP 4 - Execute callable

Call the callable by doing `result = callable()`.
This result is actually a pointer to `StructX509` and to get to the structure we have to do `struct_of_fn_pointers = result[0]`.

## Function pointers in C

Looking at each of those type we find they all represent types of function pointer. The 5 function pointers are :-

* HSM_CLIENT_HANDLE (*HSM_CLIENT_CREATE)()
  * No input param but returns `HSM_CLIENT_HANDLE`
* void (*HSM_CLIENT_DESTROY)(HSM_CLIENT_HANDLE handle)
   * Takes the above structure as an input and returns a pointer to `HSM_CLIENT_DESTROY`.
* char* (*HSM_CLIENT_GET_CERTIFICATE)(HSM_CLIENT_HANDLE handle)
   * Takes the above structure as an input and returns a pointer to `HSM_CLIENT_GET_CERTIFICATE`.
* char* (*HSM_CLIENT_GET_ALIAS_KEY)(HSM_CLIENT_HANDLE handle)
  * Takes the above structure as an input and returns a pointer to `HSM_CLIENT_GET_ALIAS_KEY`.
* char* (*HSM_CLIENT_GET_COMMON_NAME)(HSM_CLIENT_HANDLE handle)
  * Takes the above structure as an input and returns a pointer to `HSM_CLIENT_GET_COMMON_NAME`.

Except the first function pointer all of them takes the structure returned by the first function one.

### Executing the real functions pointed by the function pointers

#### STEP 1 - Call first function which returns handle

The first function pointer is accessed via `func_pointer_handle = struct_of_fn_pointers.handle_create`. The left side of the equation already represents an address. Again a CFUNCTYPE needs to be defined to make it into a callable following the same process as above. The return type of this function type is a `void` pointer.

`functype_handle = ctypes.CFUNCTYPE(restype=ctypes.c_void_p)`

Getting the callable is `callable_handle = functype_handle(fn_pointer_handle)`
Calling this would be `created_handle_value = callable_handle()` which returns the handle that must be further used for the other function pointers.

#### STEP 2 - Using the handle to call another function

Let us consider the function for retrieving common name.  As usual we access the function pointer from the sturcture like 

`func_pointer_get_name = struct_of_fn_pointers.name_get`

The left side of the equation already represents an address. Again a CFUNCTYPE needs to be defined to make it into a callable following the same process as above. In this case the result type is a string (common name) and the input argument takes the pointer to handle as input param.

`functype_get_name = ctypes.CFUNCTYPE(ctypes.c_char_p, ctypes.c_void_p)`

Getting the callable is `callable_get_name = functype_get_name(func_pointer_get_name)`

Calling the callable is done via
```python
created_name_val = function_get_name(created_handle_value)
print(created_name_val)
```
The last print statement prints the common name of the certificate.

#### STEP 3 - Destroying the handle

The other interesting thing that we can do with functype is to destroy the handle that we created in the first function. All the steps are same as above, with the noticeable difference in defining functype. Here the result type is `None` as this function will not return anything.

`functype_destroy_handle = ctypes.CFUNCTYPE(None, ctypes.c_void_p)`

# Compilation into a static object library

`gcc -shared -o libcustom_hsm_example.so -fPIC custom_hsm_example.c`

# Call the python script

`python call_hsm.py`