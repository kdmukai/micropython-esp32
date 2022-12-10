
# Use these pin defs for the @samkorn custom pcb dev board
dev_board = dict(
    st7789=dict(
        mosi=11,
        clk=12,
        cs=10,
        dc=13,
        rst=14,
    ),
    camera=dict(
        sioc=9,  # SCL
        siod=8,  # SDA
        vsync=16, href=15,
        pclk=33, xclk=34,
        d6=36, d7=35,
        d4=38, d5=37,
        d2=40, d3=39,
        d0=42, d1=41,
        reset=-1, pwdn=-1,  # not connected
    ),
    buttons=dict(
        key1=2,
        key2=1,
        key3=0,
        joy_up=6,
        joy_down=4,
        joy_left=7,
        joy_right=3,
        joy_press=5,
    )
)



# use these defs for the original breadboard "spaghetti" wiring
manual_wiring = dict(
    st7789=dict(
        mosi=11,
        clk=12,
        cs=10,
        dc=1,
        rst=2,
    ),
    camera=dict(
        sioc=9,  # SCL
        siod=8,  # SDA
        vsync=7, href=6,
        pclk=5, xclk=4,
        d6=41, d7=42,
        d4=39, d5=40,
        d2=37, d3=38,
        d0=35, d1=36,
        reset=-1, pwdn=-1,  # not connected
    ),
    buttons=dict(
        key1=3,
        key2=34,
        key3=33,
        joy_up=13,
        joy_down=14,
        joy_left=15,
        joy_right=16,
        joy_press=17,
    )
)