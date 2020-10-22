import ctypes

# This structure defines fields which are all void pointers.
# 1. That function name is 'hsm_client_x509_interface()'
# 2. This function returns a single pointer(*) to a structure called 'HSM_CLIENT_X509_INTERFACE'
# 3. This 'HSM_CLIENT_X509_INTERFACE' structure contains 5 pointer(*)s to a 5 different functions.


class StructX509(ctypes.Structure):
    _fields_ = [
        ("handle_create", ctypes.c_void_p),
        ("handle_destroy_twice", ctypes.c_void_p),
        ("cert_get", ctypes.c_void_p),
        ("key_get", ctypes.c_void_p),
        ("name_get", ctypes.c_void_p),
    ]


# Load the C library
library_loaded = ctypes.cdll.LoadLibrary("libcustom_hsm_example.so")  # Or full path to file

# Assign the common function in header file to a variable
x509_interface_hsm_client = library_loaded.hsm_client_x509_interface

# Get the address of the common header function from the C library
# This is done as we are casting the function into a void pointer
address_x509_interface_hsm_client = ctypes.cast(x509_interface_hsm_client, ctypes.c_void_p).value

# Now we have an address for the main header function.
# And we have to get the real function from there.
# For a simple funtion it looks like 'func = functype(addr)'
# Our function is NOT simple. It actually returns a Pointer to a Structure containing 5 function pointers.
# So we need to define a functype with return type and input types.
# There is no input and the return type is a pointer to a structure.
functype_x509_address = ctypes.CFUNCTYPE(ctypes.POINTER(StructX509))
function_hsm_client_x509 = functype_x509_address(address_x509_interface_hsm_client)


# Call the function that got typed above.
# Since function does not accept any input argument, we dont have any param passed in the brackets.
# This calling will return a pointer to a structure containing the 5 function pointers.
# so 'result_x509_address' is a pointer to a structure which containing 5 function pointers.
# This should print out "hello from method" whcih proves it calls the main method.
print("call main method should print hello from method")
result_x509_address = function_hsm_client_x509()

# The result we got contains a pointer to a structure consisting of 5 pointers.
# To get to the structure we have to index of 0.
# And essentially to get to the first function pointer we have to use the param name defined.
# Fetch the structure.
struct_of_fn_pointers = result_x509_address[0]
# print(struct_of_fn_pointers)

# Function pointer for the create handle
func_pointer_create_handle = struct_of_fn_pointers.handle_create
functype_handle_create = ctypes.CFUNCTYPE(restype=ctypes.c_void_p)
callable_handle_create = functype_handle_create(func_pointer_create_handle)
created_handle_value = callable_handle_create()
print(created_handle_value)
print("Hexadecimal address of created handle")
print(hex(created_handle_value))

# Function pointer for the get certificate
func_pointer_get_cert = struct_of_fn_pointers.cert_get
functype_get_cert = ctypes.CFUNCTYPE(ctypes.c_char_p, ctypes.c_void_p)
callable_get_cert = functype_get_cert(func_pointer_get_cert)
created_cert_val = callable_get_cert(created_handle_value)
print(created_cert_val)

# Function pointer for the get key
func_pointer_get_key = struct_of_fn_pointers.key_get
functype_get_key = ctypes.CFUNCTYPE(ctypes.c_char_p, ctypes.c_void_p)
callable_get_key = functype_get_key(func_pointer_get_key)
created_key_val = callable_get_key(created_handle_value)
print(created_key_val)

# Function pointer for the get common name
func_pointer_get_name = struct_of_fn_pointers.name_get
functype_get_name = ctypes.CFUNCTYPE(ctypes.c_char_p, ctypes.c_void_p)
callable_get_name = functype_get_name(func_pointer_get_name)
created_name_val = callable_get_name(created_handle_value)
print(created_name_val)

# Function pointer for the destroy handle
func_pointer_destroy_handle = struct_of_fn_pointers.handle_destroy_twice
# The destroy handle function returns void (so use None).
functype_destroy_handle = ctypes.CFUNCTYPE(None, ctypes.c_void_p)
function_destroy_handle = functype_destroy_handle(func_pointer_destroy_handle)
function_destroy_handle(created_handle_value)
