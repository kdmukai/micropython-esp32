# Create an INTERFACE library for our C module.
add_library(secp256k1 INTERFACE)

# Add our source files to the lib
target_sources(secp256k1 INTERFACE
    ${CMAKE_CURRENT_LIST_DIR}/secp256k1/src/secp256k1.c
	${CMAKE_CURRENT_LIST_DIR}/mpy/config/ext_callbacks.c
	${CMAKE_CURRENT_LIST_DIR}/mpy/libsecp256k1.c
)

# Add the current directory as an include directory.
target_include_directories(secp256k1 INTERFACE
    ${CMAKE_CURRENT_LIST_DIR}/secp256k1
	${CMAKE_CURRENT_LIST_DIR}/secp256k1/src
	${CMAKE_CURRENT_LIST_DIR}/mpy/config
)
target_compile_options(secp256k1 INTERFACE
    -DHAVE_CONFIG_H 
	-Wno-unused-function
	-Wno-error
)


# Link our INTERFACE library to the usermod target.
target_link_libraries(usermod INTERFACE secp256k1)
